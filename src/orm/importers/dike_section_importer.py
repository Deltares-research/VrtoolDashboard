from pathlib import Path
from typing import Iterator

import numpy as np
from geopandas import GeoDataFrame
from peewee import JOIN

from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.models import Mechanism, MechanismPerSection, ComputationScenario, MeasurePerSection, Measure, \
    OptimizationStep, OptimizationRun, OptimizationStepResultMechanism, OptimizationStepResultSection, \
    OptimizationSelectedMeasure, OptimizationType, MeasureResult, MeasureResultParameter, MeasureResultSection, \
    StandardMeasure, MeasureType
from vrtool.orm.models.section_data import SectionData
from vrtool.probabilistic_tools.combin_functions import CombinFunctions
from vrtool.probabilistic_tools.probabilistic_functions import beta_to_pf, pf_to_beta

from src.linear_objects.dike_section import DikeSection
from src.orm import models as orm
from src.orm.models import AssessmentMechanismResult, AssessmentSectionResult
from src.orm.orm_controller_custom import get_optimization_step_with_lowest_total_cost_table_no_closing, \
    get_optimization_steps_ordered


class DikeSectionImporter(OrmImporterProtocol):
    traject_gdf: GeoDataFrame
    run_id_dsn: int  # run_id of the OptimizationRun for Doorsnede Eisen
    run_id_vr: int  # run_id of the OptimizationRun for Veiligheidsrendement
    final_greedy_step_id: int  # id of the final step of the greedy optimization
    assessment_time: list[int]

    def __init__(self, traject_gdf: GeoDataFrame, run_id_vr: int, run_id_dsn: int, final_greedy_step_id: int):
        self.traject_gdf = traject_gdf
        self.run_id_dsn = run_id_dsn
        self.run_id_vr = run_id_vr
        self.final_greedy_step_id = final_greedy_step_id

    def _get_initial_assessment(self,
                                section_data: SectionData,
                                ) -> dict:
        """
        Gets the initial assessment of a section based on the table ComputationScenarioResult.
        Also sets the attribute assessment_time to the list of times for which the assessment is computed.
        :param section_data:
        :return:
        """
        _initial_assessment = {}
        _section_id = section_data.id

        # Add mechanism results
        for mechanism in self.active_mechanisms:
            _mechanism_id = Mechanism.get(Mechanism.name == mechanism).id

            _mechanism_per_section_id = MechanismPerSection.get(
                (MechanismPerSection.section == _section_id) & (MechanismPerSection.mechanism == _mechanism_id)).id

            _query_betas = (AssessmentMechanismResult
                            .select(AssessmentMechanismResult.time, AssessmentMechanismResult.beta)
                            .where(AssessmentMechanismResult.mechanism_per_section == _mechanism_per_section_id)
                            .order_by(AssessmentMechanismResult.time))

            _initial_assessment[mechanism] = [row.beta for row in _query_betas]

        # Add section results
        _query_betas = (AssessmentSectionResult
                        .select(AssessmentSectionResult.time, AssessmentSectionResult.beta)
                        .where(AssessmentSectionResult.section_data == _section_id)
                        .order_by(AssessmentSectionResult.time))

        _initial_assessment["Section"] = [row.beta for row in _query_betas]

        self.__setattr__("assessment_time", [row.time for row in _query_betas])
        return _initial_assessment

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

            _params['dberm'] = params_dberm[0].value if params_dberm.count() > 0 else 0
            _params['dcrest'] = params_dcrest[0].value if params_dcrest.count() > 0 else 0
            _params['beta_target'] = params_beta_target[0].value if params_beta_target.count() > 0 else None
            _params['transition_level'] = params_transition_level[
                0].value if params_transition_level.count() > 0 else None
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

    def _get_vzg_parameters(self) -> tuple[float, float]:
        _vzg_params = (StandardMeasure.select(StandardMeasure.prob_of_solution_failure,
                                              StandardMeasure.failure_probability_with_solution)
        .join(Measure)
        .join(MeasureType)
        .where(
            (Measure.combinable_type_id == 3) &
            (MeasureType.name == "Vertical Geotextile")

        )
        ).get()

        return _vzg_params.prob_of_solution_failure, _vzg_params.failure_probability_with_solution

    def get_final_measure_dsn(self, section_data: SectionData) -> dict:
        """
        Get the dictionary containing the information about the final mesure of the section for Doorsnede-eisen.

        :param section_data:
        :return: dictionary with the followings keys: "name", "LCC", "Piping", "StabilityInner", "Overflow", "Revetment"
        ,"Section"
        """
        _optimization_steps = get_optimization_steps_ordered(self.run_id_dsn)

        _optimum_section_step_number = None
        _cost = 0
        _iterated_step_number = []
        for _optimization_step in _optimization_steps:

            section = (SectionData
                       .select()
                       .join(MeasurePerSection)
                       .join(MeasureResult)
                       .join(OptimizationSelectedMeasure)
                       .where(OptimizationSelectedMeasure.id == _optimization_step.optimization_selected_measure_id)
                       ).get()

            if section.id == section_data.id and _optimization_step.step_number not in _iterated_step_number:
                _optimum_section_step_number = _optimization_step.step_number
                _cost += self._get_section_lcc(_optimization_step) # for dsn there should be only one addition
                _iterated_step_number.append(_optimization_step.step_number)



        if _optimum_section_step_number is None:
            return self._get_no_measure_case(section_data)

        _optimum_section_optimization_steps = (OptimizationStep
        .select()
        .join(OptimizationSelectedMeasure, JOIN.INNER, on=(
                OptimizationStep.optimization_selected_measure_id == OptimizationSelectedMeasure.id))
        .where(
            (OptimizationSelectedMeasure.optimization_run == self.run_id_dsn) & (
                    OptimizationStep.step_number == _optimum_section_step_number))
        )

        _final_measure = self._get_final_measure(_optimum_section_optimization_steps)
        _final_measure["LCC"] = _cost
        return _final_measure

    def get_final_measure_vr(self, section_data: SectionData) -> dict:
        """
        Get the dictionary containing the information about the final mesure of the section for Veiligheidsrendement.

        :param section_data: section fror which information should be retrieved.
        :return: dictionary with the followings keys: "name", "LCC", "Piping", "StabilityInner", "Overflow",
        "Revetment", "Section"
        """

        # 1. Get the final step number, default is the one for which the Total Cost is minimal.
        _final_step_number = OptimizationStep.get(OptimizationStep.id == self.final_greedy_step_id).step_number

        _optimization_steps = get_optimization_steps_ordered(self.run_id_vr)

        # 2. Get the most optimal optimization step number
        # This is the last step_number (=highest) for the section of interest before the final_step_number
        # this implies that the _optimum_section_steps are ordered in ascending order of step_number
        _optimum_section_step_number = None

        _section_cumulative_cost = 0  # this is the cost for one section, cumulative for all the optimization steps
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

            if section.id == section_data.id and _optimization_step.step_number not in _iterated_step_number:
                _section_cumulative_cost += self._get_section_lcc(_optimization_step)
                _optimum_section_step_number = _optimization_step.step_number
                _iterated_step_number.append(_optimization_step.step_number)

        if _optimum_section_step_number is None:
            # In this case, the section has not been reinforced, so the initial assessment is the final measure.
            return self._get_no_measure_case(section_data)

        _optimum_section_optimization_steps = (OptimizationStep
        .select()
        .join(OptimizationSelectedMeasure)
        .where(
            (OptimizationSelectedMeasure.optimization_run == self.run_id_vr)
            & (OptimizationStep.step_number == _optimum_section_step_number)
        )
        )
        # 3. Get all information into a dict based on the optimum optimization steps.

        _final_measure = self._get_final_measure(_optimum_section_optimization_steps)
        _final_measure["LCC"] = _section_cumulative_cost
        return _final_measure

    def _get_no_measure_case(self, section_data: SectionData) -> dict:

        _final_measure = self._get_initial_assessment(section_data)

        _final_measure["LCC"] = 0
        _final_measure["name"] = "Geen maatregel"
        _final_measure["investment_year"] = None

        return _final_measure

    def _get_final_measure(self, optimization_steps) -> dict:
        """
        Retrieve from the database the information related to the selected optimization steps: betas, LCC, name, measure
        paramaters.
        :param optimization_steps:
        :return: dictionary with the followings keys: "name", "LCC", "Piping", "StabilityInner", "Overflow", "Revetment"
        , "Section"
        """

        # Get the betas for the measure:
        _final_measure = self._get_final_measure_betas(optimization_steps)

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

    def _get_investment_year(self, optimization_step: OptimizationStep) -> int:
        """
        Get the investment year of the optimization step.
        :param optimization_step: optimization step for which the investment year is retrieved.
        :return: investment year
        """
        _selected_optimization_measure = OptimizationSelectedMeasure.select().where(
            OptimizationSelectedMeasure.id == optimization_step.optimization_selected_measure_id).get()

        return _selected_optimization_measure.investment_year

    def _get_mechanism_beta(self, optimization_step: OptimizationStep, mechanism: str) -> Iterator[
        orm.OptimizationStepResultMechanism]:

        """
        Get the beta values for a mechanism for a given optimization step
        :param optimization_step: optimization step for which the betas are retrieved
        :param mechanism: string name of the mechanism
        :return:

        """
        _query = (OptimizationStepResultMechanism
                  .select(OptimizationStepResultMechanism.beta)
                  .join(MechanismPerSection, JOIN.INNER,
                        on=(OptimizationStepResultMechanism.mechanism_per_section == MechanismPerSection.id))
                  .join(Mechanism, JOIN.INNER,
                        on=(MechanismPerSection.mechanism_id == Mechanism.id))
                  .where((Mechanism.name == mechanism) & (
                OptimizationStepResultMechanism.optimization_step_id == optimization_step.id)))

        return _query

    def _get_section_betas(self, optimization_step: OptimizationStep) -> Iterator[orm.OptimizationStepResultSection]:
        """
        Get the beta values for the section for a given optimization step
        :param optimization_step:  optimization step for which the betas are retrieved
        :return:
        """
        _query = (OptimizationStepResultSection
                  .select(OptimizationStepResultSection.beta)
                  .where(OptimizationStepResultSection.optimization_step_id == optimization_step.id))
        return _query

    def _get_section_lcc(self, optimization_step: OptimizationStep) -> float:
        """
        Get the lcc of a section for a given optimization step
        :param optimization_step:
        :param section_data:
        :return:
        """

        # Get all the optimization_steps for the section:

        _query = (OptimizationStepResultSection
                  .select(OptimizationStepResultSection.lcc)
                  .where(OptimizationStepResultSection.optimization_step_id == optimization_step.id)).first()

        return _query.lcc

    def _get_final_measure_betas(self, optimization_steps: OptimizationStep) -> dict:
        _final_measure = {}
        _dict_probabilities = {}

        if optimization_steps.count() == 1:

            # for mechanism_per_section in mechanisms_per_section:
            for mechanism in self.active_mechanisms:
                _final_measure[mechanism] = [row.beta for row in
                                             self._get_mechanism_beta(optimization_steps[0], mechanism)]
            # Add section betas as well:
            _final_measure["Section"] = [row.beta for row in self._get_section_betas(optimization_steps[0])]

            return _final_measure


        elif optimization_steps.count() in [2, 3]:
            _final_measure = self._get_final_measure_combined_betas(optimization_steps)

            return _final_measure
        elif optimization_steps.count() > 3:
            raise ValueError("No more than 2 measure results is allowed")
        else:
            raise ValueError("No measure results found")

    def _get_final_measure_combined_betas(self, optimization_steps: OptimizationStep) -> dict:
        """
        Combine the mechanism probabilities from a Combinable+Partial measure set. And compute the section betas.
        :param optimization_steps:
        :return:
        """
        _final_measure = {}
        _dict_probabilities = {}

        # find which optimization step is the soil reinforcement or vzg or revetment
        soil_reinforcement_step, vzg_step, revetment_step, diaphram_wall_step, stability_screen_step = None, None, None, None, None
        for optimization_step in optimization_steps:
            _measure_type = self._get_mesure_type_from_optimization_step(optimization_step)
            if _measure_type.name in ["Soil reinforcement", "Soil reinforcement with stability screen"]:
                soil_reinforcement_step = optimization_step
            elif _measure_type.name in ["Vertical Geotextile"]:
                vzg_step = optimization_step
            elif _measure_type.name in ["Revetment"]:
                revetment_step = optimization_step
            elif _measure_type.name in ["Diaphragm Wall"]:
                diaphram_wall_step = optimization_step
            elif _measure_type.name in ["Stability Screen"]:
                stability_screen_step = optimization_step

        # Assign the mechanism betas according to the right optimization step(s):
        for mechanism in self.active_mechanisms:

            if mechanism == "Stability Screen" and stability_screen_step is not None:
                _betas = np.array([row.beta for row in
                                   self._get_mechanism_beta(stability_screen_step, mechanism)])
                _final_measure[mechanism] = _betas
                _dict_probabilities[mechanism] = beta_to_pf(_betas)
                continue

            if diaphram_wall_step is not None and mechanism != "Revetment":
                _betas = np.array([row.beta for row in
                                   self._get_mechanism_beta(diaphram_wall_step, mechanism)])
                _final_measure[mechanism] = _betas
                _dict_probabilities[mechanism] = beta_to_pf(_betas)
                continue

            if revetment_step is not None and mechanism != "Revetment" and vzg_step is None and soil_reinforcement_step is None:
                _betas = np.array([row.beta for row in
                                   self._get_mechanism_beta(revetment_step, mechanism)])
                _final_measure[mechanism] = _betas
                _dict_probabilities[mechanism] = beta_to_pf(_betas)
                continue


            if mechanism == "Revetment" and revetment_step is not None:
                _betas_revetment = np.array(
                    [row.beta for row in self._get_mechanism_beta(revetment_step, mechanism)])
                _final_measure[mechanism] = _betas_revetment
                _dict_probabilities[mechanism] = beta_to_pf(_betas_revetment)
                continue  # don't need to go further

            if mechanism == "Piping" and vzg_step is not None and soil_reinforcement_step is not None:
                _pf_solution_failure, _pf_with_solution = self._get_vzg_parameters()
                _betas_soil_reinforcement = np.array(
                    [row.beta for row in self._get_mechanism_beta(soil_reinforcement_step, mechanism)])
                _pf_soil_reinforcement = beta_to_pf(_betas_soil_reinforcement)
                _pf_combined_solutions = _pf_solution_failure * _pf_soil_reinforcement + (
                        1 - _pf_solution_failure) * _pf_with_solution
                _beta_combined_solutions = pf_to_beta(_pf_combined_solutions)
                _final_measure[mechanism] = _beta_combined_solutions
                _dict_probabilities[mechanism] = _pf_combined_solutions
                continue

            if vzg_step is not None and soil_reinforcement_step is not None:
                _betas_soil_reinforcement = np.array([row.beta for row in
                                                      self._get_mechanism_beta(soil_reinforcement_step, mechanism)])
                _betas_vzg = np.array([row.beta for row in
                                       self._get_mechanism_beta(vzg_step, mechanism)])

                _beta_combined_solutions = np.maximum(
                    _betas_soil_reinforcement,
                    _betas_vzg
                )
                _final_measure[mechanism] = _beta_combined_solutions
                _pf_combined_solutions = beta_to_pf(_beta_combined_solutions)
                _dict_probabilities[mechanism] = _pf_combined_solutions
                continue

            if vzg_step is not None and soil_reinforcement_step is None:
                _betas = np.array([row.beta for row in self._get_mechanism_beta(vzg_step, mechanism)])
                _final_measure[mechanism] = _betas
                _dict_probabilities[mechanism] = beta_to_pf(_betas)
                continue

            if soil_reinforcement_step is not None and vzg_step is None:
                _betas = np.array([row.beta for row in
                                   self._get_mechanism_beta(soil_reinforcement_step, mechanism)])
                _final_measure[mechanism] = _betas
                _dict_probabilities[mechanism] = beta_to_pf(_betas)
                continue

            # raise ValueError("Error, configuration to be implemented")

        section = CombinFunctions.combine_probabilities(_dict_probabilities, tuple(_dict_probabilities.keys()))

        # Add section betas as well: You need to redo product of betas here:

        _final_measure["Section"] = [pf_to_beta(pf_section) for pf_section in section]

        return _final_measure

    def _get_mesure_type_from_optimization_step(self, optimization_step: OptimizationStep) -> MeasureType:
        """
        Get the measure type from the optimization step
        :param optimization_step:
        :return:
        """
        measure = self._get_single_measure(optimization_step)

        measure_type = MeasureType.get(MeasureType.id == measure.measure_type_id)

        return measure_type

    def _get_coordinates(self, section_data: SectionData) -> list[tuple[float, float]]:
        """
        Get the RD coordinates of the section
        :param section_data:
        :return:
        """
        # Get the coordinates of the section

        _section_name = section_data.section_name
        # check if the section name is in the traject_gdf
        if _section_name not in self.traject_gdf["section_name"].values:
            raise ValueError(
                f"Section name {_section_name} not found in traject_gdf, try renaming the section 0{_section_name} in the database.")

        _coordinates = self.traject_gdf[self.traject_gdf["section_name"] == _section_name].geometry.iloc[0]

        return _coordinates

    def import_orm(self, orm_model: SectionData) -> DikeSection:
        """ Import a SectionData ORM model into a DikeSection object"""
        if not orm_model:
            raise ValueError(f"No valid value given for {SectionData.__name__}.")

        _dike_section = DikeSection(name=orm_model.section_name,
                                    coordinates_rd=[],
                                    in_analyse=True,
                                    )
        self.active_mechanisms = self._get_all_section_mechanism(orm_model)
        # years: list[int]  # Years for which a reliability result is available (both for initial and measures)
        _dike_section.name = orm_model.section_name
        print("section name: ", orm_model.section_name)
        _dike_section.length = round(orm_model.section_length)
        _dike_section.coordinates_rd = self._get_coordinates(orm_model)
        _dike_section.in_analyse = orm_model.in_analysis
        _dike_section.is_reinforced = True  # TODO remove this argument?
        _dike_section.is_reinforced_veiligheidsrendement = True  # TODO remove this argument?
        _dike_section.is_reinforced_doorsnede = True  # TODO remove this argument?
        _dike_section.revetment = True if "Revetment" in self.active_mechanisms else False

        _dike_section.initial_assessment = self._get_initial_assessment(orm_model)
        _dike_section.years = self.assessment_time

        if self.final_greedy_step_id is not None:
            _dike_section.final_measure_veiligheidsrendement = self.get_final_measure_vr(orm_model)
            _dike_section.final_measure_doorsnede = self.get_final_measure_dsn(orm_model)
        else:
            _dike_section.final_measure_veiligheidsrendement = None
            _dike_section.final_measure_doorsnede = None

        return _dike_section

    def _get_all_section_mechanism(self, section_data: SectionData) -> list[str]:
        """
        Get all the active mechanism for the given section.
        A mechanism is active if it is present in the table MechanismPerSection.
        :param section_data:
        :return:
        """
        _mechanism_list = []

        mechanisms_for_section = (
            Mechanism
            .select(Mechanism.name)
            .join(MechanismPerSection, on=(Mechanism.id == MechanismPerSection.mechanism_id))
            .where(MechanismPerSection.section_id == section_data.id)
        )

        # Execute the query and print the results
        for mechanism in mechanisms_for_section:
            _mechanism_list.append(mechanism.name)
        return _mechanism_list
