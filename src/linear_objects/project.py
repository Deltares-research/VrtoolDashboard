from dataclasses import dataclass

from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject


@dataclass
class DikeProject():
    name: str
    dike_sections: list[DikeSection]
    start_year: int  # starting year of the project
    end_year: int   # ending year of the project, this is the year where reinforced beta is taken.s
    total_length: float = 0

    def calc_project_cost(self):
        cost = 0
        for dike_section in self.dike_sections:
            cost += dike_section.final_measure_veiligheidsrendement["LCC"]

        return cost


def get_projects_from_saved_data(imported_runs_data: dict, project_overview_data: list[dict]) -> list[DikeProject]:
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
        )
        projects.append(project)
    return projects
