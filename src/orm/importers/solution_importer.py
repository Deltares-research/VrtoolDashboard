from peewee import JOIN
from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.models import OptimizationStep, SectionData, MeasurePerSection, MeasureResult, \
    OptimizationSelectedMeasure, Measure, MeasureResultParameter

from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject
from src.orm.importers.optimization_step_importer import _get_section_lcc, _get_final_measure_betas
from src.orm.orm_controller_custom import get_optimization_steps_ordered
from src.utils.utils import beta_to_pf


class TrajectSolutionRunImporter(OrmImporterProtocol):
    run_id_dsn: int  # run_id of the OptimizationRun for Doorsnede Eisen
    run_id_vr: int  # run_id of the OptimizationRun for Veiligheidsrendement
    final_greedy_step_id: int  # id of the final step of the greedy optimization
    assessment_time: list[int]

    def __init__(self, dike_traject: DikeTraject,
                 run_id_vr: int, run_id_dsn: int, final_greedy_step_id: int
                 ):
        self.dike_section_mapping = {section.name: section for section in dike_traject.dike_sections}
        self.run_id_dsn = run_id_dsn
        self.run_id_vr = run_id_vr
        self.final_greedy_step_id = final_greedy_step_id

    def import_orm(self):
        self.get_final_measure_vr()
        self.get_final_measure_dsn()


        return

    def get_final_measure_dsn(self) -> dict:
        """
        Get the dictionary containing the information about the final mesure of the section for Doorsnede-eisen.

        :param section_data:
        :return: dictionary with the followings keys: "name", "LCC", "Piping", "StabilityInner", "Overflow", "Revetment"
        ,"Section"
        """
        _optimization_steps = get_optimization_steps_ordered(self.run_id_dsn)

        _iterated_step_number = []
        for _optimization_step in _optimization_steps:

            section = (SectionData
                       .select()
                       .join(MeasurePerSection)
                       .join(MeasureResult)
                       .join(OptimizationSelectedMeasure)
                       .where(OptimizationSelectedMeasure.id == _optimization_step.optimization_selected_measure_id)
                       ).get()

            # find corresponding section in dike_section
            dike_section: DikeSection = self.dike_section_mapping[section.section_name]

            # With this if statement, we avoid getting the combined measures multiple times
            if _optimization_step.step_number not in _iterated_step_number:
                _iterated_step_number.append(_optimization_step.step_number)

                _optimum_section_optimization_steps = (OptimizationStep
                .select()
                .join(OptimizationSelectedMeasure)
                .where(
                    (OptimizationSelectedMeasure.optimization_run == self.run_id_dsn)
                    & (OptimizationStep.step_number == _optimization_step.step_number)
                )
                )
                # 3. Get all information into a dict based on the optimum optimization steps.

                _step_measure = self._get_measure(_optimum_section_optimization_steps,
                                                  active_mechanisms=dike_section.active_mechanisms)
                _step_measure["LCC"] = dike_section.final_measure_doorsnede["LCC"] = _get_section_lcc(
                    _optimization_step)
                dike_section.final_measure_doorsnede = _step_measure

    def get_final_measure_vr(self) -> dict:
        """
        Get the dictionary containing the information about the final measure of the section for Veiligheidsrendement,
        and calculates

        """

        # 1. Get the final step number, default is the one for which the Total Cost is minimal.
        _final_step_number = OptimizationStep.get(OptimizationStep.id == self.final_greedy_step_id).step_number

        _optimization_steps = get_optimization_steps_ordered(self.run_id_vr)

        # 2. Get the most optimal optimization step number
        # This is the last step_number (=highest) for the section of interest before the final_step_number
        # this implies that the _optimum_section_steps are ordered in ascending order of step_number

        _iterated_step_number = []
        for _optimization_step in _optimization_steps:
            # Stop when the last step has been reached
            if _optimization_step.step_number > _final_step_number:
                break

            section = (SectionData
                       .select()
                       .join(MeasurePerSection)
                       .join(MeasureResult)
                       .join(OptimizationSelectedMeasure)
                       .where(OptimizationSelectedMeasure.id == _optimization_step.optimization_selected_measure_id)
                       ).get()

            # find corresponding section in dike_section
            dike_section: DikeSection = self.dike_section_mapping[section.section_name]

            if _optimization_step.step_number not in _iterated_step_number:
                dike_section.final_measure_veiligheidsrendement["LCC"] += _get_section_lcc(_optimization_step)
                _iterated_step_number.append(_optimization_step.step_number)

                _optimum_section_optimization_steps = (OptimizationStep
                .select()
                .join(OptimizationSelectedMeasure)
                .where(
                    (OptimizationSelectedMeasure.optimization_run == self.run_id_vr)
                    & (OptimizationStep.step_number == _optimization_step.step_number)
                )
                )

                # 3. Get all information into a dict based on the optimum optimization steps.
                _step_measure = self._get_measure(_optimum_section_optimization_steps,
                                                  active_mechanisms=dike_section.active_mechanisms)
                _step_measure["LCC"] = dike_section.final_measure_veiligheidsrendement["LCC"]

                dike_section.final_measure_veiligheidsrendement = _step_measure

    def _get_measure(self, optimization_steps, active_mechanisms: list) -> dict:
        """
        Retrieve from the database the information related to the selected optimization steps: betas, name, measure
        paramaters.
        :param optimization_steps:
        :return: dictionary with the followings keys: "name", "LCC", "Piping", "StabilityInner", "Overflow", "Revetment"
        , "Section"
        """

        # Get the betas for the measure:
        _final_measure = _get_final_measure_betas(optimization_steps, active_mechanisms)

        # Get the extra information measure name and the corresponding parameter values for the most (combined or not) optimal step
        if optimization_steps.count() == 1:
            _final_measure["name"] = self._get_single_measure(optimization_steps[0]).name
            _final_measure['investment_year'] = self._get_investment_year(optimization_steps[0])

        elif optimization_steps.count() in [2, 3]:
            _final_measure["name"] = self._get_combined_measure_name(optimization_steps)
            _year_1 = self._get_investment_year(optimization_steps[0])
            _year_2 = self._get_investment_year(optimization_steps[1])
            _final_measure['investment_year'] = min([_year_1, _year_2])

        else:
            raise ValueError(f"Unexpected number of optimum steps: {optimization_steps.count()}")
        _final_measure.update(self._get_measure_parameters(optimization_steps))
        return _final_measure

    def _get_single_measure(self, optimization_step: OptimizationStep) -> Measure:
        """Return the measure associated with a given single optimization step"""

        measure = (Measure
                   .select()
                   .join(MeasurePerSection)
                   .join(MeasureResult)
                   .join(OptimizationSelectedMeasure)
                   .where(OptimizationSelectedMeasure.id == optimization_step.optimization_selected_measure_id)
                   .get())

        return measure

    def _get_investment_year(self, optimization_step: OptimizationStep) -> int:
        """
        Get the investment year of the optimization step.
        :param optimization_step: optimization step for which the investment year is retrieved.
        :return: investment year
        """
        _selected_optimization_measure = OptimizationSelectedMeasure.select().where(
            OptimizationSelectedMeasure.id == optimization_step.optimization_selected_measure_id).get()

        return _selected_optimization_measure.investment_year

    def _get_combined_measure_name(self, optimization_step: OptimizationStep) -> str:

        name = self._get_single_measure(optimization_step[0]).name + " + " + self._get_single_measure(
            optimization_step[1]).name
        return name

    def _get_measure_parameters(self, optimization_steps: OptimizationStep) -> dict:
        _params = {}

        for optimum_step in optimization_steps:

            optimum_selected_measure = OptimizationSelectedMeasure.get(
                OptimizationSelectedMeasure.id == optimum_step.optimization_selected_measure_id)
            measure_result = MeasureResult.get(MeasureResult.id == optimum_selected_measure.measure_result_id)

            params_dberm = MeasureResultParameter.select().where(
                (MeasureResultParameter.measure_result_id == measure_result.id) &
                (MeasureResultParameter.name == "DBERM")
            )
            params_dcrest = MeasureResultParameter.select().where(
                (MeasureResultParameter.measure_result_id == measure_result.id) &
                (MeasureResultParameter.name == "DCREST")
            )

            params_beta_target = MeasureResultParameter.select().where(
                (MeasureResultParameter.measure_result_id == measure_result.id) &
                (MeasureResultParameter.name == "BETA_TARGET")
            )
            params_transition_level = MeasureResultParameter.select().where(
                (MeasureResultParameter.measure_result_id == measure_result.id) &
                (MeasureResultParameter.name == "TRANSITION_LEVEL")
            )

            if _params.get('dberm') is None and params_dberm.count() > 0:
                _params['dberm'] = params_dberm[0].value
            if _params.get('dcrest') is None and params_dcrest.count() > 0:
                _params['dcrest'] = params_dcrest[0].value
            if _params.get('beta_target') is None and params_beta_target.count() > 0:
                _params['beta_target'] = params_beta_target[0].value
            if _params.get('transition_level') is None and params_transition_level.count() > 0:
                _params['transition_level'] = params_transition_level[0].value

            _params['pf_target_ratio'] = None
            _params['diff_transition_level'] = None

            # get the ratio of beta target and diff transition level when relevant
            if params_beta_target.count() > 0:
                _measure_per_section_id = MeasurePerSection.get(
                    MeasurePerSection.id == measure_result.measure_per_section_id).id

                # get the measure result which has the same measure_per_section as the applied measure but with the
                # lowest beta target (this is the initial revetment measure)
                _ini_measure_result = MeasureResult.select().where(
                    MeasureResult.measure_per_section_id == _measure_per_section_id).order_by(MeasureResult.id.asc())

                # Get the initial revetment parameters:
                ini_beta_target = MeasureResultParameter.select().where(
                    (MeasureResultParameter.measure_result_id == _ini_measure_result) &
                    (MeasureResultParameter.name == "BETA_TARGET")
                )
                ini_transition_level = MeasureResultParameter.select().where(
                    (MeasureResultParameter.measure_result_id == _ini_measure_result) &
                    (MeasureResultParameter.name == "TRANSITION_LEVEL")
                )

                _params['pf_target_ratio'] = round(
                    beta_to_pf(ini_beta_target[0].value) / beta_to_pf(_params['beta_target']), 1)
                _params["diff_transition_level"] = _params['transition_level'] - ini_transition_level[0].value

        return _params
