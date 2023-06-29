from dataclasses import dataclass

from src.linear_objects.base_linear import BaseLinearObject


class DikeSection(BaseLinearObject):
    coordinates_rd: list[tuple[float, float]]  # from parent class
    name: str
    in_analyse: bool
    initial_assessment: dict
    final_measure_veiligheidrendement: dict
    final_measure_doorsnede: dict  # replace dict with a Measure Object

    def __init__(self, name: str, in_analyse: bool, coordinates_rd: list[tuple[float, float]]):
        super().__init__(coordinates_rd)
        self.name = name
        self.in_analyse = False
        self.initial_assessment = {}
        self.final_measure_veiligheidrendement = {}
        self.final_measure_doorsnede = {}


    def serialize(self):
        """Serialize the DikeSection object to a dict, in order to be saved in dcc.Store"""
        return {
            'coordinates_rd': self.coordinates_rd,
            'name': self.name,
            'in_analyse': self.in_analyse,
            'initial_assessment': self.initial_assessment,
            'final_measure_veiligheidrendement': self.final_measure_veiligheidrendement,
            'final_measure_doorsnede': self.final_measure_doorsnede,
        }

