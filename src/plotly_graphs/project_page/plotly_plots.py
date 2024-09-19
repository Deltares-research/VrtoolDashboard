import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.constants import REFERENCE_YEAR, CLASSIC_PLOTLY_COLOR_SEQUENCE, PROJECTS_COLOR_SEQUENCE
from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import get_traject_prob, get_initial_assessment_df, DikeTraject
from src.linear_objects.project import DikeProject
from src.utils.traject_probability import get_updated_beta_df
from src.utils.utils import pf_to_beta, interpolate_beta_values


def projects_reliability_over_time(projects: list[DikeProject], imported_runs_data: dict) -> go.Figure:
    _fig = go.Figure()

    # first sort projects by ending year
    projects = sorted(projects, key=lambda x: x.end_year)

    for index, traject_data in enumerate(imported_runs_data.values()):
        color_traject = CLASSIC_PLOTLY_COLOR_SEQUENCE[index]

        dike_traject = DikeTraject.deserialize(traject_data)
        _beta_df = get_initial_assessment_df(dike_traject.dike_sections)
        _traject_pf, _ = get_traject_prob(_beta_df)
        _traject_betas = pf_to_beta(_traject_pf)[0]

        # Initialize years and betas
        years_ini = np.linspace(2025, projects[0].end_year, projects[0].end_year - 2025 + 1)
        years_beta = np.array(dike_traject.dike_sections[0].years) + REFERENCE_YEAR
        betas_ini = interpolate_beta_values(years_ini, _traject_betas, years_beta)

        # Loop through projects and update betas
        for index, project in enumerate(projects):
            year_start = projects[index].end_year
            year_end = projects[index + 1].end_year if index < len(projects) - 1 else 2100

            # get all the sections of the project that are part of the traject
            dike_sections = [section for section in project.dike_sections if
                             section.parent_traject_name == dike_traject.name]

            _beta_df = get_updated_beta_df(dike_sections, _beta_df)

            _traject_pf = get_traject_prob(_beta_df)[0]
            _traject_betas = pf_to_beta(_traject_pf)[0]

            years = np.linspace(year_start, year_end, year_end - year_start + 1)
            betas = interpolate_beta_values(years, _traject_betas, years_beta)

            years_ini = np.concatenate((years_ini, years))
            betas_ini = np.concatenate((betas_ini, betas))

        _fig.add_trace(go.Scatter(name="ondergrens",
                                  x=years_ini,
                                  y=[pf_to_beta(dike_traject.lower_bound_value)] * len(years_ini),
                                  line=dict(color=color_traject, dash="dot"),
                                  mode='lines',
                                  legendgroup=dike_traject.name,
                                  legendgrouptitle=dict(text=dike_traject.name)
                                  ))

        _fig.add_trace(go.Scatter(name="Traject faalkans",
                                  x=years_ini,
                                  y=betas_ini,
                                  marker=dict(color=color_traject),
                                  line=dict(color=color_traject),
                                  mode='lines+markers',
                                  legendgroup=dike_traject.name,
                                  legendgrouptitle=dict(text=dike_traject.name)
                                  ))

    # Add project shapes:
    for index, project in enumerate(projects):
        color = PROJECTS_COLOR_SEQUENCE[index]
        _fig.add_shape(
            type="rect",
            x0=project.start_year,
            y0=0 + 0.5 * index,
            x1=project.end_year,
            y1=0.5 + 0.5 * index,
            fillcolor=color,
            opacity=0.5,
            layer="below",
            line_width=0,
        )
        # add annotation in the middle of the shape:
        _fig.add_annotation(
            x=(project.start_year + project.end_year) / 2,
            y=0.25 + 0.5 * index,
            text=project.name,
            showarrow=False,
            font=dict(color="black", size=18),
        )



    _fig.update_layout(xaxis_title='Jaar', yaxis_title="Betrouwbaarheid")

    return _fig
