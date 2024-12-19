import numpy as np

from src.constants import REFERENCE_YEAR
from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import get_traject_prob_fast, DikeTraject
from src.linear_objects.project import DikeProject
from src.utils.utils import get_traject_reliability, pf_to_beta, interpolate_beta_values


class DikeProgram():
    dike_trajects: dict[str, DikeTraject]
    projects: list[DikeProject]
    trajects_pf_over_time: dict[str, dict[str, list[float]]]

    def __init__(self, imported_runs_data: dict, project_overview_data: list, calc_failure_pro: bool = True):
        """

        Args:
            imported_runs_data:
            project_overview_data:
            calc_failure_pro: True if the probability of failure of the PROJECTS (=subset made of DikeSections)
            should be calculated.
        """
        self.projects, self.dike_trajects = get_projects_from_saved_data(imported_runs_data, project_overview_data,
                                                                         calc_failure_pro)
        self.trajects_pf_over_time = self.calc_trajects_failure_proba()

    def calc_trajects_failure_proba(self):
        """
        Calculate the trajec probabilibty of failure for all the trajects in the program, reinforcing sections according
        to the projects in the program.

        Returns: a dict with the years and betas of the failure probability for each traject

        {"10-1": {"years": [2025, 2026, ...], "betas": [0.1, 0.2, ...]}, ...}

        For a year is the end_year of a project, the year si duplicated in the years list and two betas are given for
        the same year: the beta before and after the reinforcement of the project.

        """
        projects = sorted(self.projects, key=lambda x: x.end_year)
        traject_res = {}
        for dike_traject in self.dike_trajects.values():
            years_ini, betas_ini = self.calc_traject_failure_proba_from_program(dike_traject, projects)
            traject_res[dike_traject.name] = {"years": years_ini, "betas": betas_ini}
        return traject_res


    @staticmethod
    def calc_traject_failure_proba_from_program(dike_traject: DikeTraject, projects: list[DikeProject]):
        _traject_reliability = get_traject_reliability(dike_traject.dike_sections, 'initial')
        _traject_pf = get_traject_prob_fast(_traject_reliability)[1]
        _traject_betas = pf_to_beta(_traject_pf)

        # Initialize years and betas
        years_ini = np.linspace(2025, projects[0].end_year, projects[0].end_year - 2025 + 1)
        years_beta = np.array(dike_traject.dike_sections[0].years) + REFERENCE_YEAR
        betas_ini = interpolate_beta_values(years_ini, _traject_betas, years_beta)

        sections_to_reinforce = []
        # loop over projects of the traject
        for index, project in enumerate(projects):
            year_start = projects[index].end_year
            year_end = projects[index + 1].end_year if index < len(projects) - 1 else 2100
            # get all the section of the project that are part of the traject
            dike_section_project_list = [section for section in project.dike_sections if
                                         section.parent_traject_name == dike_traject.name]
            sections_to_reinforce.extend(dike_section_project_list)
            _unreinforced_sections = [section for section in dike_traject.dike_sections if
                                      section.name not in [s.name for s in sections_to_reinforce]]

            _traject_reliability = get_traject_reliability(sections_to_reinforce, 'partial',
                                                           unreinforced_sections=_unreinforced_sections)
            _traject_pf = get_traject_prob_fast(_traject_reliability)[1]

            _traject_betas = pf_to_beta(_traject_pf)

            years = np.linspace(year_start, year_end, year_end - year_start + 1)
            betas = interpolate_beta_values(years, _traject_betas, years_beta)

            years_ini = np.concatenate((years_ini, years))
            betas_ini = np.concatenate((betas_ini, betas))

        return years_ini, betas_ini


def get_projects_from_saved_data(imported_runs_data: dict, project_overview_data: list[dict],
                                 calc_failure_pro: bool = True) -> tuple[
    list[DikeProject], dict[str, DikeTraject]]:
    """

    :param imported_runs_data: stored data of all the imported runs as a dict with key format: "traject|run", for ex:
    "7-2|Basisberekening"
    :param project_overview_data: Overview of the projects with the selected sections
    :param calc_failure_pro: bool: if True, calculate the probability of failure for the projects
    :return:
    """
    projects = []

    # First populate the dike_trajects dict to avoid dezerializing the same data multiple times
    dict_runs = {}
    for run_name in imported_runs_data.keys():
        dike_traject = DikeTraject.deserialize(imported_runs_data[run_name])
        dict_runs[run_name] = dike_traject

    if project_overview_data is None:
        return projects, dict_runs

    # assemble project data:
    for project_data in project_overview_data:

        sections = []
        traject_damages = []  # a project can be theoretically composed of sections from multiple trajects which all have their own flood damage
        for section_traject in project_data["sections"]:  # multi_select_value
            section_name, traject_name = section_traject.split("|")
            for run_name in imported_runs_data.keys():
                if traject_name in run_name:
                    dike_traject = dict_runs[run_name]
                    traject_damages.append(dike_traject.flood_damage)
                    break

            section = dike_traject.get_section(section_name)
            section.parent_traject_name = traject_name
            sections.append(section)

        project = DikeProject(
            name=project_data["project"],
            start_year=project_data["start_year"],
            end_year=project_data["end_year"],
            dike_sections=sections,
            project_failure_prob_assessement=calc_prob_failure_before_reinforcement(
                sections) if calc_failure_pro else None,
            project_failure_prob_after_reinforcement=calc_prob_failure_after_reinforcement(
                sections) if calc_failure_pro else None,  # this is the faalkans at year 2025! be aware
            flood_damage=max(traject_damages),  # take the maximum flood damage of the trajects considered

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
    # _beta_df = get_initial_assessment_df(dike_sections)
    # _traject_pf, _ = get_traject_prob(_beta_df)

    _traject_reliability = get_traject_reliability(dike_sections, 'initial')
    _traject_pf = get_traject_prob_fast(_traject_reliability)[1]
    return _traject_pf[0]


def calc_prob_failure_after_reinforcement(dike_sections: list[DikeSection]) -> float:
    """
    Calculate the probability of failure (faalkans) for the given collection of sections after reinforcement at year 2025.
    Args:
        dike_sections:

    Returns: probability of failure for the first time step (year 2025)

    """
    # _beta_df_ini = get_initial_assessment_df(dike_sections)
    # _beta_df = get_updated_beta_df(dike_sections, _beta_df_ini)
    #
    # _traject_pf = get_traject_prob(_beta_df)[0]
    #
    _traject_reliability = get_traject_reliability(dike_sections, 'veiligheidsrendement')
    _traject_pf = get_traject_prob_fast(_traject_reliability)[1]
    return _traject_pf[0]


def calc_area_stats(projects: list[DikeProject], trajects: dict[str, DikeTraject]):
    """
    Calculate the total cost, damage and risk for the entire area.
    Cost is simply the sum of the costs of all the reinforced sections in the projects
    Damage is the sum of the flood damages of all the sections in the projects

    Risk is the sum of the flood damages of all the sections in the projects multiplied by the probability of failure
    after completion (i.e. reinforcement) of the project.

    :param projects: list of DikeProject objects
    :return: tuple: the total cost, and current risk and the risk after reinforcement
    """
    cost = 0
    damage = 0
    current_risk = 0
    future_risk = 0
    for project in projects:
        cost += project.calc_project_cost()

    for dike_traject in trajects.values():
        damage += dike_traject.flood_damage
        # _beta_df_ini = get_initial_assessment_df(dike_traject.dike_sections)
        # _traject_pf, _ = get_traject_prob(_beta_df_ini)

        _traject_reliability = get_traject_reliability(dike_traject.dike_sections, 'initial')
        _traject_pf = get_traject_prob_fast(_traject_reliability)[1]
        current_risk += dike_traject.flood_damage * _traject_pf[0]

        # _beta_df = get_updated_beta_df(dike_traject.dike_sections, _beta_df_ini)
        # _traject_pf = get_traject_prob(_beta_df)[0]
        _traject_reliability = get_traject_reliability(dike_traject.dike_sections, 'veiligheidsrendement')
        _traject_pf = get_traject_prob_fast(_traject_reliability)[1]
        future_risk += dike_traject.flood_damage * _traject_pf[0]  # this is the faalkans at year 2025! be aware

    return cost, current_risk, future_risk


def calc_area_stats_new(program: DikeProgram):
    """
    Calculate the total cost, damage and risk for the entire area.
    Cost is simply the sum of the costs of all the reinforced sections in the projects
    Damage is the sum of the flood damages of all the sections in the projects

    Risk is the sum of the flood damages of all the sections in the projects multiplied by the probability of failure
    after completion (i.e. reinforcement) of the project.


    """
    projects, trajects = program.projects, program.dike_trajects
    cost = 0
    damage = 0

    risk_metrics = {"current": {2025: 0, 2050: 0, 2075: 0},
                    "program": {2025: 0, 2050: 0, 2075: 0}}
    for project in projects:
        cost += project.calc_project_cost()

    for dike_traject in trajects.values():
        damage += dike_traject.flood_damage

        _traject_reliability = get_traject_reliability(dike_traject.dike_sections, 'initial')
        _traject_pf = get_traject_prob_fast(_traject_reliability)[1]
        # get id where year is 2050 in the list dike_traject.sections[0].years
        idx_2050 = np.where(np.array(dike_traject.dike_sections[0].years) == 25)[0][0]
        idx_2075 = np.where(np.array(dike_traject.dike_sections[0].years) == 50)[0][0]

        risk_metrics["current"][2025] += dike_traject.flood_damage * _traject_pf[0]
        risk_metrics["current"][2050] += dike_traject.flood_damage * _traject_pf[idx_2050]
        risk_metrics["current"][2075] += dike_traject.flood_damage * _traject_pf[idx_2075]

        # Get the risk for the program
        idx_2050 = np.where(program.trajects_pf_over_time[f"{dike_traject.name}"]["years"] == 2050)[0][-1]
        idx_2075 = np.where(program.trajects_pf_over_time[f"{dike_traject.name}"]["years"] == 2075)[0][-1]
        risk_metrics["program"][2025] += program.trajects_pf_over_time[f"{dike_traject.name}"]["betas"][0] * dike_traject.flood_damage
        risk_metrics["program"][2050] += program.trajects_pf_over_time[f"{dike_traject.name}"]["betas"][idx_2050] * dike_traject.flood_damage
        risk_metrics["program"][2075] += program.trajects_pf_over_time[f"{dike_traject.name}"]["betas"][idx_2075] * dike_traject.flood_damage


    return cost, risk_metrics
