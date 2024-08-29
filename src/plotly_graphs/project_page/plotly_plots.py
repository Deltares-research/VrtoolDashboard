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
    # first sort projects by year
    projects = sorted(projects, key=lambda x: x.year)
    # add rectangle between years with random color


    all_dike_sections = [section for project in projects for section in project.dike_sections]
    _beta_df = get_initial_assessment_df(all_dike_sections)
    _traject_pf, _ = get_traject_prob(_beta_df)
    _traject_betas = pf_to_beta(_traject_pf)[0]

    # Initialize years and betas
    years_ini = np.linspace(2025, projects[0].year, projects[0].year - 2025 + 1)
    years_beta = np.array(projects[0].dike_sections[0].years) + REFERENCE_YEAR
    betas_ini = interpolate_beta_values(years_ini, _traject_betas, years_beta)

    # Loop through projects and update betas
    for index, project in enumerate(projects):
        year_start = projects[index].year
        year_end = projects[index + 1].year if index < len(projects) - 1 else 2100
        _beta_df = get_updated_beta_df(projects[index].dike_sections, _beta_df)
        _traject_pf = get_traject_prob(_beta_df)[0]
        _traject_betas = pf_to_beta(_traject_pf)[0]

        years = np.linspace(year_start, year_end, year_end - year_start + 1)
        betas = interpolate_beta_values(years, _traject_betas, years_beta)

        years_ini = np.concatenate((years_ini, years))
        betas_ini = np.concatenate((betas_ini, betas))

        _fig.add_annotation(x=year_start, y=betas_ini[-1], text=project.name, showarrow=True, arrowhead=1)
        _fig.add_hline(y=pf_to_beta(3.3333333333333335e-05), line_dash="dot", line_color="black")



    _fig.add_trace(go.Scatter(x=years_ini, y=betas_ini, mode='lines+markers'))


    _fig.update_layout(xaxis_title='Tijd', yaxis_title="Betrouwbaarheid")


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

    return beta_df
