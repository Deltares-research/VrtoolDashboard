from dataclasses import dataclass
from typing import Optional

from src.linear_objects.dike_section import DikeSection


@dataclass
class DikeProject():
    name: str
    dike_sections: list[DikeSection]
    start_year: int  # starting year of the project
    end_year: int  # ending year of the project, this is the year where reinforced beta is taken.s
    project_failure_prob_assessement: Optional[float] = None
    project_failure_prob_after_reinforcement: Optional[float] = None
    flood_damage: Optional[float] = None

    def calc_project_cost(self):
        cost = 0
        for dike_section in self.dike_sections:
            cost += dike_section.final_measure_veiligheidsrendement["LCC"]

        return cost

    @property
    def total_length(self):
        return sum([section.length for section in self.dike_sections])



