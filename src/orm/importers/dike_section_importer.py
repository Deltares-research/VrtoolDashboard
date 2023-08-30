from geopandas import GeoDataFrame

from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.models import Mechanism, MechanismPerSection, ComputationScenario, MeasurePerSection, Measure
from vrtool.orm.models.section_data import SectionData

from src.linear_objects.dike_section import DikeSection
from src.orm.models import GreedyOptimizationOrder, ModifiedMeasure, MeasureCost, \
    MeasureReliability, TargetReliabilityBasedOrder, AssessmentMechanismResult, AssessmentSectionResult


class DikeSectionImporter(OrmImporterProtocol):
    traject_gdf: GeoDataFrame
    assessment_time: list[int]

    def __init__(self, traject_gdf: GeoDataFrame):
        self.traject_gdf = traject_gdf

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

        for mechanism in ["Overflow", "StabilityInner", "Piping"]:

            # TODO: multiple mechanism_per_section for the same computation_type_id. commented to avoid crashes

            # if mechanism == "Piping":
            #     # How to aggregate all the piping scenarios into a single beta?
            #     # Should VRCore handle this and only write a single piping beta in the table ComputationScenarioResult?
            #     continue

            _mechanism_id = Mechanism.get(Mechanism.name == mechanism).id
            _mechanism_per_section_id = MechanismPerSection.get(
                (MechanismPerSection.section == _section_id) & (MechanismPerSection.mechanism == _mechanism_id)).id



            _query_betas = (AssessmentMechanismResult
                            .select(AssessmentMechanismResult.time, AssessmentMechanismResult.beta)
                            .where(AssessmentMechanismResult.mechanism_per_section == _mechanism_per_section_id)
                            .order_by(AssessmentMechanismResult.time))


            _initial_assessment[mechanism] = [row.beta for row in _query_betas]

        self.__setattr__("assessment_time", [row.time for row in _query_betas])

        return _initial_assessment

    def _get_taken_measure_modified_measure_id(self, section_id: int, assessment_type: str) -> int:
        """
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
        Get the corresponding measure name from the ModifiedMeasure id
        :param modified_measure_id:
        :return:
        """

        _measure_per_section_id = ModifiedMeasure.get(ModifiedMeasure.id == modified_measure_id).measure_per_section_id
        _measure_id = MeasurePerSection.get(MeasurePerSection.id == _measure_per_section_id).measure_id
        _measure_name = Measure.get(Measure.id == _measure_id).name
        return _measure_name

    def _get_final_measure(self, section_data: SectionData, assessment_type: str) -> dict:
        """

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
        # _dike_section.final_measure_veiligheidrendement = self._get_final_measure(orm_model,
        #                                                                           assessment_type="GreedyOptimizationBased")
        # _dike_section.final_measure_doorsnede = self._get_final_measure(orm_model,
        #                                                                 assessment_type="TargetReliabilityBased")

        _dike_section.initial_assessment = self._get_initial_assessment(orm_model)

        _dike_section.years = self.assessment_time

        return _dike_section
