from typing import Optional

from pandas import DataFrame

from src.linear_objects.base_linear import BaseLinearObject


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
    years: list[int]  # Years for which a reliability result is available (both for initial and measures)

    def __init__(self, name: str, coordinates_rd: list[tuple[float, float]], in_analyse: int):
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

    def serialize(self) -> dict:
        """Serialize the DikeSection object to a dict, in order to be saved in dcc.Store"""
        return {
            'coordinates_rd': self.coordinates_rd,
            'name': self.name,
            'length': self.length,
            'in_analyse': self.in_analyse,
            'revetment': self.revetment,
            'is_reinforced_veiligheidsrendement': self.is_reinforced_veiligheidsrendement,
            'is_reinforced_doorsnede': self.is_reinforced_doorsnede,
            'initial_assessment': self.initial_assessment,
            'final_measure_veiligheidsrendement': self.final_measure_veiligheidsrendement,
            'final_measure_doorsnede': self.final_measure_doorsnede,
            'years': self.years
        }

    @staticmethod
    def deserialize(data: dict) -> 'DikeSection':
        """Deserialize the DikeSection object from a dict, in order to be loaded from dcc.Store

        :param data: serialized dict with the data of the DikeSection object

        """
        section = DikeSection(name=data['name'], in_analyse=data['in_analyse'], coordinates_rd=data['coordinates_rd'])
        section.length = data['length']
        section.initial_assessment = data['initial_assessment']
        section.is_reinforced_doorsnede = data['is_reinforced_veiligheidsrendement']
        section.is_reinforced_veiligheidsrendement = data['is_reinforced_doorsnede']
        section.final_measure_veiligheidsrendement = data['final_measure_veiligheidsrendement']
        section.final_measure_doorsnede = data['final_measure_doorsnede']
        section.years = data['years']
        section.revetment = data['revetment']
        return section
