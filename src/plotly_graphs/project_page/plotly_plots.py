import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.constants import REFERENCE_YEAR
from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import get_traject_prob, get_initial_assessment_df
from src.linear_objects.project import DikeProject
from src.utils.utils import pf_to_beta, interpolate_beta_values


def projects_reliability_over_time(projects: list[DikeProject]) -> go.Figure:
    _fig = go.Figure()
    #first sort projects by year
    projects = sorted(projects, key=lambda x: x.year)
    print("")
    print("project order", [(project.name, project.year) for project in projects])

    all_dike_sections = [section for project in projects for section in project.dike_sections]
    _beta_df = get_initial_assessment_df(all_dike_sections)
    _traject_pf, _ = get_traject_prob(_beta_df)
    _traject_betas = pf_to_beta(_traject_pf)[0]

    # before the first project
    year_start_ini = 2025
    year_end_ini = projects[0].year
    years_ini = np.linspace(year_start_ini, year_end_ini, year_end_ini - year_start_ini + 1)
    years_beta = np.array(projects[0].dike_sections[0].years) + REFERENCE_YEAR
    betas_ini = interpolate_beta_values(years_ini, _traject_betas, years_beta)

    for index in range(0, len(projects)-1):
        year_end_ini = projects[index+1].year
        year_start_ini = projects[index].year
        _beta_df = get_updated_beta_df(projects[index].dike_sections, _beta_df)
        _traject_pf = get_traject_prob(_beta_df)[0]
        _traject_betas = pf_to_beta(_traject_pf)[0]

        years = np.linspace(year_start_ini, year_end_ini, year_end_ini - year_start_ini + 1)
        years_beta = np.array(projects[0].dike_sections[0].years) + REFERENCE_YEAR
        betas = interpolate_beta_values(years, _traject_betas, years_beta)

        #add the first beta value of the project
        years_ini = np.concatenate((years_ini, years))
        betas_ini = np.concatenate((betas_ini, betas))

    # last project:
    year_start_ini = projects[-1].year
    year_end_ini = 2100
    years = np.linspace(year_start_ini, year_end_ini, year_end_ini - year_start_ini + 1)
    years_beta = np.array(projects[0].dike_sections[0].years) + REFERENCE_YEAR
    betas = interpolate_beta_values(years, _traject_betas, years_beta)
    years_ini = np.concatenate((years_ini, years))
    betas_ini = np.concatenate((betas_ini, betas))



    _fig.add_trace(go.Scatter(x=years_ini, y=betas_ini, mode='lines+markers', name='Reliability over time'))

    return _fig


def get_updated_beta_df(dike_sections: list[DikeSection], beta_df: pd.DataFrame) -> pd.DataFrame:
    # _beta_df = get_initial_assessment_df(dike_sections)
    # _traject_pf, _ = get_traject_prob(_beta_df)
    years = dike_sections[0].years

    for section in dike_sections:
        # for section_name in _section_order:
        #     section = self.get_section(section_name)

        if not section.in_analyse:  # skip if the section is not reinforced
            continue

        if (
                not section.is_reinforced_veiligheidsrendement
        ):  # skip if the section is not reinforced
            continue
        _active_mechanisms = ["Overflow", "Piping", "StabilityInner"]
        if section.revetment:
            _active_mechanisms.append("Revetment")
        # add a row to the dataframe with the initial assessment of the section
        for mechanism in _active_mechanisms:
            mask = (beta_df["name"] == section.name) & (
                    beta_df["mechanism"] == mechanism
            )
            # replace the row in the dataframe with the betas of the section if both the name and mechanism match

            for year, beta in zip(
                    years, getattr(section, "final_measure_veiligheidsrendement")[mechanism]
            ):
                beta_df.loc[mask, year] = beta

        # _reinforced_traject_pf, _ = get_traject_prob(beta_df)
        # _traject_pf = np.concatenate((traject_pf, _reinforced_traject_pf), axis=0)

    # return beta_df, np.array(traject_pf)
    return beta_df


