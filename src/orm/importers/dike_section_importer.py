from copy import copy
from geopandas import GeoDataFrame

from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.models import Mechanism, MechanismPerSection
from vrtool.orm.models.section_data import SectionData

from src.linear_objects.dike_section import DikeSection

from src.orm.models import AssessmentMechanismResult, AssessmentSectionResult


class DikeSectionImporter(OrmImporterProtocol):
    traject_gdf: GeoDataFrame
    assessment_time: list[int]

    def __init__(self, traject_gdf: GeoDataFrame, assessment_time: list[int]):
        self.traject_gdf = traject_gdf
        self.assessment_time = assessment_time

    def _get_initial_assessment(self,
                                section_id: int,
                                active_mechanisms: list[str]
                                ) -> dict:
        """
        Gets the initial assessment of a section based on the table ComputationScenarioResult.
        Also sets the attribute assessment_time to the list of times for which the assessment is computed.
        :param section_data:
        :return:
        """
        _initial_assessment = {}

        # Add mechanism results
        for mechanism in active_mechanisms:
            _mechanism_id = Mechanism.get(Mechanism.name == mechanism).id

            _mechanism_per_section_id = MechanismPerSection.get(
                (MechanismPerSection.section == section_id) & (MechanismPerSection.mechanism == _mechanism_id)).id

            _query_betas = (AssessmentMechanismResult
                            .select(AssessmentMechanismResult.time, AssessmentMechanismResult.beta)
                            .where(AssessmentMechanismResult.mechanism_per_section == _mechanism_per_section_id)
                            .order_by(AssessmentMechanismResult.time))

            _initial_assessment[mechanism] = [row.beta for row in _query_betas if row.time in self.assessment_time]

        # Add section results
        _query_betas = (AssessmentSectionResult
                        .select(AssessmentSectionResult.time, AssessmentSectionResult.beta)
                        .where(AssessmentSectionResult.section_data == section_id)
                        .order_by(AssessmentSectionResult.time))

        # checking if the section has a beta value for the assessment time should not be necessary in theory if the
        # data in the database is consistent with assessment_time (config.T) but it is not often the case.
        _initial_assessment["Section"] = [row.beta for row in _query_betas if row.time in self.assessment_time]

        return _initial_assessment

    def _get_no_measure_case(self, initial_assessment: dict) -> dict:
        """"
        Get the initial assessment of a section without any measures.

        :param initial_assessment: Dictionary with the initial assessment betas of the section


        :return:
        """

        _final_measure = copy(initial_assessment)

        _final_measure["LCC"] = 0
        _final_measure["name"] = "Geen maatregel"
        _final_measure["investment_year"] = None

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

    def import_orm_without_measure(self, orm_model: SectionData) -> DikeSection:
        """ Import a SectionData ORM model into a DikeSection object without the taken measures. """
        if not orm_model:
            raise ValueError(f"No valid value given for {SectionData.__name__}.")
        _dike_section = DikeSection(name=orm_model.section_name,
                                    coordinates_rd=[],
                                    in_analyse=True,
                                    )
        # years: list[int]  # Years for which a reliability result is available (both for initial and measures)
        _dike_section.name = orm_model.section_name
        _dike_section.length = round(orm_model.section_length)
        _dike_section.coordinates_rd = self._get_coordinates(orm_model)
        _dike_section.in_analyse = orm_model.in_analysis
        _dike_section.is_reinforced = True  # TODO remove this argument?
        _dike_section.is_reinforced_veiligheidsrendement = True  # TODO remove this argument?
        _dike_section.is_reinforced_doorsnede = True  # TODO remove this argument?
        _dike_section.active_mechanisms = self._get_all_section_mechanism(orm_model)
        _dike_section.revetment = True if "Revetment" in _dike_section.active_mechanisms else False
        _dike_section.flood_damages = orm_model.flood_damage

        _dike_section.initial_assessment = self._get_initial_assessment(orm_model, _dike_section.active_mechanisms)
        _dike_section.years = self.assessment_time

        # Set the final measures to the initial assessment, they will be modified later on.
        _dike_section.final_measure_veiligheidsrendement = self._get_no_measure_case(_dike_section.initial_assessment)
        _dike_section.final_measure_doorsnede = self._get_no_measure_case(_dike_section.initial_assessment)

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
