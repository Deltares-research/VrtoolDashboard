from pathlib import Path
from typing import Iterator

from geopandas import GeoDataFrame
from peewee import JOIN

from vrtool.common.enums import MechanismEnum
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.io.importers.optimization.optimization_step_importer import OptimizationStepImporter

from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.models import Mechanism, MechanismPerSection, ComputationScenario, MeasurePerSection, Measure, \
    OptimizationStep, OptimizationRun, OptimizationStepResultMechanism, OptimizationStepResultSection, \
    OptimizationSelectedMeasure, OptimizationType, MeasureResult, MeasureResultParameter
from vrtool.orm.models.section_data import SectionData
from vrtool.orm.orm_controllers import get_optimization_steps

from src.linear_objects.dike_section import DikeSection
from src.orm import models as orm
from src.orm.models import GreedyOptimizationOrder, ModifiedMeasure, MeasureCost, \
    MeasureReliability, TargetReliabilityBasedOrder, AssessmentMechanismResult, AssessmentSectionResult
from src.orm.orm_controller_custom import get_optimization_step_with_lowest_total_cost_table_no_closing


class DikeSectionImporter(OrmImporterProtocol):
    traject_gdf: GeoDataFrame
    run_id: int  # run_id of the OptimizationRun for Veiligheidsrendement
    final_greedy_step_id: int  # id of the final step of the greedy optimization
    assessment_time: list[int]

    def __init__(self, traject_gdf: GeoDataFrame, run_id: int, final_greedy_step_id: int):
        self.traject_gdf = traject_gdf
        self.run_id = run_id
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

    def _get_taken_measure_modified_measure_id(self, section_id: int, assessment_type: str) -> int:
        """
        DEPRECATED
        Get the corresponding ModifiedMeasure id for the section_id in either the GreedyOptimizationOrder or
        TargetReliaiblityBasedOrder table
        :param section_id: id of the Section of interest, for this id there should be one matching row in the
        Order table
        :param assessment_type: one of TargetReliabilityBased (doorsnede-eis) or
         GreedyOptimizationBased (veiligheidrendement))
        :return:
        """

        order_table = GreedyOptimizationOrder if assessment_type == "GreedyOptimizationBased" else TargetReliabilityBasedOrder

        for row in order_table.select():
            _modified_measure = ModifiedMeasure.get(ModifiedMeasure.id == row.modified_measure_id)

            _measure_per_section = MeasurePerSection.get(
                MeasurePerSection.id == _modified_measure.measure_per_section_id)

            _section = SectionData.get(SectionData.id == _measure_per_section.section_id)
            if _section.id == section_id:
                return _modified_measure.id
        raise ValueError(f"No match found for Section id={section_id} in {assessment_type} table")

    def _get_measure_name(self, modified_measure_id: int) -> str:
        """
        DEPRECATED
        Get the corresponding measure name from the ModifiedMeasure id
        :param modified_measure_id:
        :return:
        """

        _measure_per_section_id = ModifiedMeasure.get(ModifiedMeasure.id == modified_measure_id).measure_per_section_id
        _measure_id = MeasurePerSection.get(MeasurePerSection.id == _measure_per_section_id).measure_id
        _measure_name = Measure.get(Measure.id == _measure_id).name
        return _measure_name

    @staticmethod
    def _get_final_step_vr(optimization_run_id: int) -> int:
        """Get the final step id of the optimization run.
        The final step in this case is the step with the lowest total cost.

        :param optimization_run_id: The id of the optimization run

        :return: The id of the final step
        """

        # TODO Temporary hardcoded config. This will be improved in another PR
        _vr_config = VrtoolConfig()
        _vr_config.input_directory = Path(
            r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\TestCase1_38-1_no_housing")
        _vr_config.excluded_mechanisms = [MechanismEnum.REVETMENT, MechanismEnum.HYDRAULIC_STRUCTURES]
        _vr_config.output_directory = _vr_config.input_directory / "results"
        _vr_config.externals = (
                Path(__file__).parent.parent / "externals/D-Stability 2022.01.2/bin"
        )
        _vr_config.traject = "38-1"

        _vr_config.input_database_name = "vrtool_input.db"

        _step_id, _, _ = get_optimization_step_with_lowest_total_cost_table_no_closing(_vr_config, optimization_run_id)

        return _step_id

    def get_final_measure_vr(self, section_data: SectionData) -> dict:

        _final_measure = {}
        _section_id = section_data.id

        _final_step_number = OptimizationStep.get(OptimizationStep.id == self.final_greedy_step_id).step_number

        _optimization_steps = get_optimization_steps(self.run_id)

        # 2. Get the most optimal o
        # This is the last step_number (=highest) for the section of interest before the final_step_number
        _optimum_section_step_number = None

        for _optimization_step in _optimization_steps:

            # Stop when the last step has been reached
            if _optimization_step.step_number > _final_step_number:
                break

            optimization_selected_measure = OptimizationSelectedMeasure.get(
                OptimizationSelectedMeasure.id == _optimization_step.optimization_selected_measure_id)
            measure_result = MeasureResult.get(MeasureResult.id == optimization_selected_measure.measure_result_id)
            measure_per_section = MeasurePerSection.get(MeasurePerSection.id == measure_result.measure_per_section_id)
            section = SectionData.get(SectionData.id == measure_per_section.section_id)

            if section.id == _section_id:
                _optimum_section_step_number = _optimization_step.step_number

        if _optimum_section_step_number is None:
            raise ValueError(
                f"Sectie {_section_id} niet gevonden in de optimalisatie")  # TODO: reassign the betas to those of the initial assessment.

        _optimum_section_optimization_steps = (OptimizationStep.select().where(
            OptimizationStep.step_number == _optimum_section_step_number)
        )

        info = []
        meas_str = ''
        for optimum_step in _optimum_section_optimization_steps:
            optimum_selected_measure = OptimizationSelectedMeasure.get(
                OptimizationSelectedMeasure.id == optimum_step.optimization_selected_measure_id)
            measure_result = MeasureResult.get(MeasureResult.id == optimum_selected_measure.measure_result_id)
            measure_per_section = MeasurePerSection.get(MeasurePerSection.id == measure_result.measure_per_section_id)
            measure = Measure.get(Measure.id == measure_per_section.measure_id)

            names_to_search = ["DBERM", "DCREST"]
            params = MeasureResultParameter.select().where(
                (MeasureResultParameter.measure_result_id == measure_result.id) &
                (MeasureResultParameter.name.in_(names_to_search))
            )
            meas_str += measure.name
            attribute_values = {}  # Create a dictionary to store attribute values
            for param in params:
                attribute_values[param.name] = param.value

        s = SectionData.get(SectionData.id == _section_id)

        print(s.section_name, _optimum_section_step_number,
              [s.optimization_selected_measure_id for s in _optimum_section_optimization_steps],
              meas_str)

        _final_measure_betas = self._get_final_measure_betas(_optimum_section_optimization_steps)

        return _final_measure_betas

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
        Get the beta values for a mechanism for a given optimization step
        :param optimization_step:  optimization step for which the betas are retrieved
        :return:
        """
        _query = (OptimizationStepResultSection
                  .select(OptimizationStepResultSection.beta)
                  .where(OptimizationStepResultSection.optimization_step_id == optimization_step.id))
        return _query

    def _get_final_measure_betas(self, optimization_steps: OptimizationStep) -> dict:
        _final_measure = {}

        if optimization_steps.count() == 1:

            # for mechanism_per_section in mechanisms_per_section:
            for mechanism in ["Piping", "StabilityInner", "Overflow"]:
                _final_measure[mechanism] = [row.beta for row in
                                             self._get_mechanism_beta(optimization_steps[0], mechanism)]
            # Add section betas as well:
            _final_measure["Section"] = [row.beta for row in self._get_section_betas(optimization_steps[0])]
            return _final_measure


        elif optimization_steps.count() == 2:
            print("Combined step")
            # for mechanism_per_section in mechanisms_per_section:
            for mechanism in ["Piping", "StabilityInner", "Overflow"]:
                _final_measure[mechanism] = [row.beta for row in
                                             self._get_mechanism_beta(optimization_steps[0], mechanism)]
            # Add section betas as well:
            _final_measure["Section"] = [row.beta for row in self._get_section_betas(optimization_steps[0])]
            return _final_measure
        elif optimization_steps.count > 2:
            raise ValueError("No more than 2 measure results is allowed")
        else:
            raise ValueError("No measure results found")

    def _get_final_measure(self, section_data: SectionData, assessment_type: str) -> dict:
        """
        DEPRECATED
        :param section_data:
        :param assessment_type: one of TargetReliabilityBased or GreedyOptimizationBased
        :return:
        """

        _final_measure = {}
        _section_id = section_data.id

        _modified_measure_id = self._get_taken_measure_modified_measure_id(_section_id, assessment_type)

        _total_cost = MeasureCost.get(MeasureCost.modified_measure == _modified_measure_id).cost
        _dberm = ModifiedMeasure.get(ModifiedMeasure.id == _modified_measure_id).dberm
        _dcrest = ModifiedMeasure.get(ModifiedMeasure.id == _modified_measure_id).dcrest

        _final_measure["LCC"] = _total_cost
        _final_measure["name"] = self._get_measure_name(_modified_measure_id)
        _final_measure["dberm"] = _dberm
        _final_measure["dcrest"] = _dcrest

        for mechanism in ["Overflow", "StabilityInner", "Piping", "Section"]:
            # TODO: multiple mechanism_per_section for the same computation_type_id. commented to avoid crashes
            # elif mechanism == "Piping":
            #     # How to aggregate all the piping scenarios into a single beta?
            #     # Should VRCore handle this and only write a single piping beta in the table ComputationScenarioResult?
            #     continue
            _query_betas = (MeasureReliability
                            .select(MeasureReliability.time, MeasureReliability.beta, MeasureReliability.id)
                            .where((MeasureReliability.modified_measure == _modified_measure_id) & (
                    MeasureReliability.mechanism == mechanism))
                            # .order_by(MeasureReliability.time)
                            )

            _final_measure[mechanism] = [row.beta for row in _query_betas]

        self.__setattr__("assessment_time", [row.time for row in _query_betas])
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

        _dike_section.final_measure_veiligheidrendement = self.get_final_measure_vr(orm_model)
        _dike_section.final_measure_doorsnede = self.get_final_measure_vr(orm_model)
        print(_dike_section.final_measure_veiligheidrendement)

        return _dike_section
