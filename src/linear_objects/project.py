from dataclasses import dataclass
from typing import Optional

from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject, get_initial_assessment_df, get_traject_prob
from src.utils.traject_probability import get_updated_beta_df


@dataclass
class DikeProject():
    name: str
    dike_sections: list[DikeSection]
    start_year: int  # starting year of the project
    end_year: int  # ending year of the project, this is the year where reinforced beta is taken.s
    project_failure_prob_assessement: Optional[float] = None
    project_failure_prob_after_reinforcement: Optional[float] = None

    def calc_project_cost(self):
        cost = 0
        for dike_section in self.dike_sections:
            cost += dike_section.final_measure_veiligheidsrendement["LCC"]

        return cost

    @property
    def total_length(self):
        return sum([section.length for section in self.dike_sections])


def get_projects_from_saved_data(imported_runs_data: dict, project_overview_data: list[dict]) -> tuple[list[DikeProject], list[DikeTraject]]:
    """

    :param imported_runs_data: stored data of all the imported runs as a dict with key format: "traject|run", for ex:
    "7-2|Basisberekening"
    :param project_overview_data: Overview of the projects with the selected sections
    :return:
    """
    projects = []


    # First populate the dike_trajects dict to avoid dezerializing the same data multiple times
    dict_runs = {}
    for run_name in imported_runs_data.keys():
        dike_traject = DikeTraject.deserialize(imported_runs_data[run_name])
        dict_runs[run_name] = dike_traject

    # assemble project data:
    for project_data in project_overview_data:

        sections = []
        for section_traject in project_data["sections"]:  # multi_select_value
            section_name, traject_name = section_traject.split("|")
            for run_name in imported_runs_data.keys():
                if traject_name in run_name:
                    dike_traject = dict_runs[run_name]
                    break

            section = dike_traject.get_section(section_name)
            section.parent_traject_name = traject_name
            sections.append(section)

        project = DikeProject(
            name=project_data["project"],
            start_year=project_data["start_year"],
            end_year=project_data["end_year"],
            dike_sections=sections,
            project_failure_prob_assessement=calc_prob_failure_before_reinforcement(sections),
            project_failure_prob_after_reinforcement=calc_prob_failure_after_reinforcement(sections)
        )
        projects.append(project)
    return projects, dict_runs


def calc_prob_failure_before_reinforcement(dike_sections: list[DikeSection]) -> float:
    """
    Calculate the probability of failure (faalkans) for the given collection of sections and return the probability for
    the first time step (year 2025).

    :param dike_sections: list of DikeSection objects
    :return: probability of failure for the first time step (year 2025)
    """
    _beta_df = get_initial_assessment_df(dike_sections)
    _traject_pf, _ = get_traject_prob(_beta_df)
    return _traject_pf[0][0]

def calc_prob_failure_after_reinforcement(dike_sections: list[DikeSection]) -> float:
    _beta_df_ini = get_initial_assessment_df(dike_sections)
    _beta_df = get_updated_beta_df(dike_sections, _beta_df_ini)

    _traject_pf = get_traject_prob(_beta_df)[0]
    return _traject_pf[0][0]



def calc_area_stats(projects: list[DikeProject]):
    cost = 0
    damage = 0
    risk = 0
    for project in projects:
        cost += project.calc_project_cost()
        for section in project.dike_sections:
            pass
            # damage += section.final_measure_veiligheidsrendement["schade"]
            # risk += section.final_measure_veiligheidsrendement["risico"]

    return cost, damage, risk