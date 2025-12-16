from bisect import bisect_right
from typing import Optional

from src.constants import REFERENCE_YEAR, CalcType
from src.linear_objects.base_linear import BaseLinearObject
from src.utils.utils import get_beta


class DikeSection(BaseLinearObject):
    coordinates_rd: list[tuple[float, float]]  # from parent class
    name: str
    length: float
    in_analyse: bool
    is_reinforced_veiligheidsrendement: bool
    is_reinforced_doorsnede: bool
    revetment: bool
    initial_assessment: Optional[dict]
    final_measure_veiligheidsrendement: Optional[dict]
    final_measure_doorsnede: Optional[dict]  # replace dict with a Measure Object
    years: list[
        int
    ]  # Years for which a reliability result is available (both for initial and measures)
    active_mechanisms: list[str]  # Active mechanisms for the dike section
    parent_traject_name: Optional[str]  # Name of the parent traject

    def __init__(
        self, name: str, coordinates_rd: list[tuple[float, float]], in_analyse: int
    ):
        """
        :param name: name of the dike section
        :param coordinates_rd: list of tuples with the coordinates of the dike section in RD coordinates
        :param in_analyse: boolean indicating whether the dike section is in the analysis, i.e. whether its reliability
        is included in the reliability of the dike trajectory.
        """
        super().__init__(coordinates_rd)
        self.name = str(name)
        self.in_analyse = True if in_analyse == 1 else False
        self.length = -999
        self.is_reinforced_veiligheidsrendement = False
        self.is_reinforced_doorsnede = False
        self.initial_assessment = None
        self.final_measure_veiligheidsrendement = None
        self.final_measure_doorsnede = None
        self.years = []
        self.revetment = False
        self.active_mechanisms = []
        self.parent_traject_name = None  # this is used in project page to retrieve the parent traject of a section from a project

    def serialize(self) -> dict:
        """Serialize the DikeSection object to a dict, in order to be saved in dcc.Store"""
        return {
            "coordinates_rd": self.coordinates_rd,
            "name": self.name,
            "length": self.length,
            "in_analyse": self.in_analyse,
            "revetment": self.revetment,
            "is_reinforced_veiligheidsrendement": self.is_reinforced_veiligheidsrendement,
            "is_reinforced_doorsnede": self.is_reinforced_doorsnede,
            "initial_assessment": self.initial_assessment,
            "final_measure_veiligheidsrendement": self.final_measure_veiligheidsrendement,
            "final_measure_doorsnede": self.final_measure_doorsnede,
            "years": self.years,
            "active_mechanisms": self.active_mechanisms,
        }

    @staticmethod
    def deserialize(data: dict) -> "DikeSection":
        """Deserialize the DikeSection object from a dict, in order to be loaded from dcc.Store

        :param data: serialized dict with the data of the DikeSection object

        """
        section = DikeSection(
            name=data["name"],
            in_analyse=data["in_analyse"],
            coordinates_rd=data["coordinates_rd"],
        )
        section.length = data["length"]
        section.initial_assessment = data["initial_assessment"]
        section.is_reinforced_doorsnede = data["is_reinforced_veiligheidsrendement"]
        section.is_reinforced_veiligheidsrendement = data["is_reinforced_doorsnede"]
        section.final_measure_veiligheidsrendement = data[
            "final_measure_veiligheidsrendement"
        ]
        section.final_measure_doorsnede = data["final_measure_doorsnede"]
        section.years = data["years"]
        section.revetment = data["revetment"]
        section.active_mechanisms = data["active_mechanisms"]
        return section

    def export_as_geojson_feature(self, params: dict) -> dict:
        """Export the dike section as a GeoJSON feature"""
        if params.get("tab") == "overview":
            return self.export_features_overview()
        elif params.get("tab") == "assessment":
            return self.export_features_assessment(params)
        elif params.get("tab") == "reinforced_sections":
            return self.export_reinforced_sections_assessment(params)
        else:
            raise ValueError("This tab cannot be exported as geojson")

    def export_features_overview(self):
        """Export the dike section as a GeoJSON feature for the overview map"""
        return {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": self.coordinates_rd},
            "properties": {
                "name": self.name,
                "length": self.length,
                "in_analyse": self.in_analyse,
                "revetment": self.revetment,
            },
        }

    def export_features_assessment(self, params: dict):
        """Export the dike section as a GeoJSON feature for the assessment map"""

        feat = {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": self.coordinates_rd},
            "properties": {
                "name": self.name,
                "in_analyse": self.in_analyse,
                "revetment": self.revetment,
            },
        }

        for mechanism in self.active_mechanisms:
            _year_index = (
                bisect_right(self.years, params["selected_year"] - REFERENCE_YEAR) - 1
            )
            _beta_meca = get_beta(
                self.initial_assessment, _year_index, mechanism.upper()
            )
            feat["properties"][f"beta_{mechanism}"] = _beta_meca
        return feat

    def export_reinforced_sections_assessment(self, params: dict):
        """Export the dike section as a GeoJSON feature for the assessment map"""
        if params["calculation_type"] == CalcType.DOORSNEDE_EISEN.name:
            _final_measure = self.final_measure_doorsnede
            _is_reinforced = self.is_reinforced_doorsnede
        elif params["calculation_type"] == CalcType.VEILIGHEIDSRENDEMENT.name:
            _final_measure = self.final_measure_veiligheidsrendement
            _is_reinforced = self.is_reinforced_veiligheidsrendement
        else:
            raise ValueError("Calculation type not recognized")
        feat = {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": self.coordinates_rd},
            "properties": {
                "name": self.name,
                "in_analyse": self.in_analyse,
            },
        }
        if self.in_analyse:

            feat["properties"]["in_analyse"] = self.in_analyse
            feat["properties"]["revetment"] = self.revetment
            feat["properties"]["is_reinforced"] = _is_reinforced
            feat["properties"]["maatregel"] = _final_measure.get("name", None)
            feat["properties"]["investment_year"] = _final_measure.get(
                "investment_year", None
            )
            feat["properties"]["dberm"] = _final_measure.get("dberm", None)
            feat["properties"]["dcrest"] = _final_measure.get(
                "dberm_target_ratio", None
            )
            feat["properties"]["pf_target_ratio"] = _final_measure.get(
                "pf_target_ratio", None
            )
            feat["properties"]["diff_transition_level"] = _final_measure.get(
                "diff_transition_level", None
            )

            for mechanism in self.active_mechanisms:
                _year_index = (
                    bisect_right(self.years, params["selected_year"] - REFERENCE_YEAR)
                    - 1
                )
                _beta_meca = get_beta(_final_measure, _year_index, mechanism.upper())

                feat["properties"][
                    f'beta_{mechanism}_{params["calculation_type"]}'
                ] = _beta_meca
        return feat
