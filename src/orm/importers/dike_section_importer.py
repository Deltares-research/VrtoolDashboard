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
from vrtool.orm.orm_controllers import get_optimization_steps
from vrtool.probabilistic_tools.combin_functions import CombinFunctions
from vrtool.probabilistic_tools.probabilistic_functions import beta_to_pf, pf_to_beta

from src.linear_objects.dike_section import DikeSection
from src.orm import models as orm
from src.orm.models import AssessmentMechanismResult, AssessmentSectionResult
from src.orm.orm_controller_custom import get_optimization_step_with_lowest_total_cost_table_no_closing


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
        for mechanism in ["Overflow", "StabilityInner", "Piping"]:
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

    def _get_single_measure_name(self, optimization_step: OptimizationStep) -> str:
        measure = (Measure
                   .select()
                   .join(MeasurePerSection)
                   .join(MeasureResult)
                   .join(OptimizationSelectedMeasure)
                   .where(OptimizationSelectedMeasure.id == optimization_step.id)

                   .get())
        return measure.name

    def _get_combined_measure_name(self, optimization_step: OptimizationStep) -> str:

        name = self._get_single_measure_name(optimization_step[0]) + " + " + self._get_single_measure_name(
            optimization_step[1])
        return name

    def _get_measure_parameters(self, optimization_steps: OptimizationStep) -> dict:
        _params = {}
        for optimum_step in optimization_steps:

            optimum_selected_measure = OptimizationSelectedMeasure.get(
                OptimizationSelectedMeasure.id == optimum_step.optimization_selected_measure_id)
            measure_result = MeasureResult.get(MeasureResult.id == optimum_selected_measure.measure_result_id)

            names_to_search = ["DBERM", "DCREST"]
            params = MeasureResultParameter.select().where(
                (MeasureResultParameter.measure_result_id == measure_result.id) &
                (MeasureResultParameter.name.in_(names_to_search))
            )
            if params.count() > 0:
                _params['dberm'] = params[0].value
                _params['dcrest'] = params[1].value

            else:
                _params['dberm'] = None
                _params['dcrest'] = None

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
        :return: dictionary with the followings keys: "name", "LCC", "Piping", "StabilityInner", "Overflow", "Section"
        """
        _optimization_steps = get_optimization_steps(optimization_run_id=self.run_id_dsn)

        _optimum_section_step_number = None

        for _optimization_step in _optimization_steps:

            section = (SectionData
                       .select()
                       .join(MeasurePerSection)
                       .join(MeasureResult)
                       .join(OptimizationSelectedMeasure)
                       .where(OptimizationSelectedMeasure.id == _optimization_step.optimization_selected_measure_id)
                       ).get()

            if section.id == section_data.id:
                _optimum_section_step_number = _optimization_step.step_number

        if _optimum_section_step_number is None:
            raise ValueError(
                f"Sectie {section_data.id} niet gevonden in de optimalisatie")  # TODO: reassign the betas to those of the initial assessment.

        _optimum_section_optimization_steps = (OptimizationStep
                                               .select()
                                               .join(OptimizationSelectedMeasure, JOIN.INNER, on=(
                OptimizationStep.optimization_selected_measure_id == OptimizationSelectedMeasure.id))
                                               .where((OptimizationSelectedMeasure.optimization_run == self.run_id_dsn) & (
                OptimizationStep.step_number == _optimum_section_step_number))
                                               )

        return self._get_final_measure(_optimum_section_optimization_steps)

    def get_final_measure_vr(self, section_data: SectionData) -> dict:
        """
        Get the dictionary containing the information about the final mesure of the section for Veiligheidsrendement.

        :param section_data: section fror which information should be retrieved.
        :return: dictionary with the followings keys: "name", "LCC", "Piping", "StabilityInner", "Overflow", "Section"
        """

        # 1. Get the final step number, default is the one for which the Total Cost is minimal.
        _final_step_number = OptimizationStep.get(OptimizationStep.id == self.final_greedy_step_id).step_number
        _optimization_steps = get_optimization_steps(self.run_id_vr)

        # 2. Get the most optimal optimization step number
        # This is the last step_number (=highest) for the section of interest before the final_step_number
        _optimum_section_step_number = None

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

            if section.id == section_data.id:
                _optimum_section_step_number = _optimization_step.step_number

        if _optimum_section_step_number is None:
            raise ValueError(
                f"Sectie {section_data.id} niet gevonden in de optimalisatie")  # TODO: reassign the betas to those of the initial assessment.

        _optimum_section_optimization_steps = (OptimizationStep
        .select()
        .join(OptimizationSelectedMeasure)
        .where(
            (OptimizationSelectedMeasure.optimization_run == self.run_id_vr)
            & (OptimizationStep.step_number == _optimum_section_step_number)
        )
        )

        # 3. Get all information into a dict based on the optimum optimization steps.
        return self._get_final_measure(_optimum_section_optimization_steps)

    def _get_final_measure(self, optimization_steps) -> dict:
        """
        Retrieve from the database the information related to the selected optimization steps: betas, LCC, name, measure
        paramaters.
        :param optimization_steps:
        :return: dictionary with the followings keys: "name", "LCC", "Piping", "StabilityInner", "Overflow", "Section"
        """

        # Get the betas for the measure:
        _final_measure = self._get_final_measure_betas(optimization_steps)

        # Get the extra information measure name and the corresponding parameter values for the most (combined or not) optimal step
        _final_measure["LCC"] = self._get_section_lcc(optimization_steps[0])

        if optimization_steps.count() == 1:
            _final_measure["name"] = self._get_single_measure_name(optimization_steps[0])

        elif optimization_steps.count() == 2:
            _final_measure["name"] = self._get_combined_measure_name(optimization_steps)

        else:
            raise ValueError(f"Unexpected number of optimum steps: {optimization_steps.count()}")

        _final_measure.update(self._get_measure_parameters(optimization_steps))
        return _final_measure

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
        :return:
        """

        _query = (OptimizationStepResultSection
                  .select(OptimizationStepResultSection.lcc)
                  .where(OptimizationStepResultSection.optimization_step_id == optimization_step.id)).first()

        return _query.lcc

    def _get_final_measure_betas(self, optimization_steps: OptimizationStep) -> dict:
        _final_measure = {}
        _dict_probabilities = {}

        if optimization_steps.count() == 1:

            # for mechanism_per_section in mechanisms_per_section:
            for mechanism in ["Piping", "StabilityInner", "Overflow"]:
                _final_measure[mechanism] = [row.beta for row in
                                             self._get_mechanism_beta(optimization_steps[0], mechanism)]
            # Add section betas as well:
            _final_measure["Section"] = [row.beta for row in self._get_section_betas(optimization_steps[0])]

            return _final_measure


        elif optimization_steps.count() == 2:
            _final_measure = self._get_final_measure_combined_betas(optimization_steps)

            return _final_measure
        elif optimization_steps.count() > 2:
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

        section = (SectionData
        .select()
        .join(MeasurePerSection)
        .join(MeasureResult)
        .join(OptimizationSelectedMeasure)
        .where(
            OptimizationSelectedMeasure.id == optimization_steps[0].optimization_selected_measure_id)
        ).get()

        for mechanism in ["Piping", "StabilityInner", "Overflow"]:
            _mechanism_id = Mechanism.get(Mechanism.name == mechanism).id
            _mechanism_per_section_id = MechanismPerSection.get(
                (MechanismPerSection.section == section.id) & (
                        MechanismPerSection.mechanism == _mechanism_id)).id

            _query_initial_betas = (AssessmentMechanismResult
                                    .select(AssessmentMechanismResult.time, AssessmentMechanismResult.beta)
                                    .where(
                AssessmentMechanismResult.mechanism_per_section == _mechanism_per_section_id)
                                    .order_by(AssessmentMechanismResult.time))
            # It doesnt matter which one is which because we multiply their pf anyway
            _measure_1_pf = np.array([beta_to_pf(row.beta) for row in
                                      self._get_mechanism_beta(optimization_steps[0], mechanism)])
            _measure_2_pf = np.array([beta_to_pf(row.beta) for row in
                                      self._get_mechanism_beta(optimization_steps[1], mechanism)])

            _initial_pf = np.array([beta_to_pf(row.beta) for row in _query_initial_betas])
            pf_solution_failure, pf_with_solution = self._get_vzg_parameters()

            pf_vzg = pf_solution_failure * _initial_pf + (1 - pf_solution_failure) * pf_with_solution
            pf_combined_solutions = _measure_1_pf * _measure_2_pf + (1 - pf_solution_failure) * pf_vzg
            _final_measure[mechanism] = pf_to_beta(pf_combined_solutions)
            _dict_probabilities[mechanism] = pf_combined_solutions

        section = CombinFunctions.combine_probabilities(_dict_probabilities, tuple(_dict_probabilities.keys()))

        # Add section betas as well: You need to redo product of betas here:

        _final_measure["Section"] = [pf_to_beta(pf_section) for pf_section in section]

        return _final_measure

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

        # years: list[int]  # Years for which a reliability result is available (both for initial and measures)
        _dike_section.name = orm_model.section_name
        _dike_section.length = orm_model.section_length
        _dike_section.coordinates_rd = self._get_coordinates(orm_model)
        _dike_section.in_analyse = orm_model.in_analysis
        _dike_section.is_reinforced = True  # TODO remove this argument?
        _dike_section.is_reinforced_veiligheidsrendement = True  # TODO remove this argument?
        _dike_section.is_reinforced_doorsnede = True  # TODO remove this argument?
        _dike_section.revetment = False  # TODO

        _dike_section.initial_assessment = self._get_initial_assessment(orm_model)
        _dike_section.years = self.assessment_time

        _dike_section.final_measure_veiligheidsrendement = self.get_final_measure_vr(orm_model)
        _dike_section.final_measure_doorsnede = self.get_final_measure_dsn(orm_model)

        return _dike_section
