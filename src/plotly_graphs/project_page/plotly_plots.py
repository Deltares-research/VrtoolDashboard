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
    color_1 = "rgba(245, 14, 151, 0.5)"
    color_2 = "rgba(69, 112, 219, 0.5)"

    all_dike_sections = [section for project in projects for section in project.dike_sections]
    _beta_df = get_initial_assessment_df(all_dike_sections)
    _traject_pf, _ = get_traject_prob(_beta_df)
    _traject_betas = pf_to_beta(_traject_pf)[0]

    # Initialize years and betas
    years_ini = np.linspace(2025, projects[0].year, projects[0].year - 2025 + 1)
    years_beta = np.array(projects[0].dike_sections[0].years) + REFERENCE_YEAR
    betas_ini = interpolate_beta_values(years_ini, _traject_betas, years_beta)
    _fig.add_shape(
        type="rect",
        x0=2025,
        x1=projects[0].year,
        y0=0,
        y1=5,
        fillcolor="grey",
        opacity=0.3,
        layer="below",
        line_width=0,
    )

    # Loop through projects and update betas
    for index in range(len(projects)):
        year_start = projects[index].year
        year_end = projects[index + 1].year if index < len(projects) - 1 else 2100
        _beta_df = get_updated_beta_df(projects[index].dike_sections, _beta_df)
        _traject_pf = get_traject_prob(_beta_df)[0]
        _traject_betas = pf_to_beta(_traject_pf)[0]

        years = np.linspace(year_start, year_end, year_end - year_start + 1)
        betas = interpolate_beta_values(years, _traject_betas, years_beta)

        years_ini = np.concatenate((years_ini, years))
        betas_ini = np.concatenate((betas_ini, betas))

        _fig.add_shape(
            type="rect",
            x0=year_start,
            x1=year_end,
            y0=0,
            y1=5,
            fillcolor=color_1 if index % 2 == 1 else color_2,
            opacity=0.3,
            layer="below",
            line_width=0,
        )

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

        # _reinforced_traject_pf, _ = get_traject_prob(beta_df)
        # _traject_pf = np.concatenate((traject_pf, _reinforced_traject_pf), axis=0)

    # return beta_df, np.array(traject_pf)
    return beta_df
