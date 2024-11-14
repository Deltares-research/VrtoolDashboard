import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.constants import REFERENCE_YEAR, CLASSIC_PLOTLY_COLOR_SEQUENCE, PROJECTS_COLOR_SEQUENCE, ResultType
from src.linear_objects.dike_traject import DikeTraject, get_traject_prob_fast
from src.linear_objects.project import DikeProject
from src.utils.utils import pf_to_beta, interpolate_beta_values, beta_to_pf, get_traject_reliability


def plot_cost_vs_time_projects(projects: list[DikeProject]):
    fig = go.Figure()
    start_program = 2025
    end_program = 2100
    years = list(range(2025, max([p.end_year for p in projects]) + 1))
    projects = sorted(projects, key=lambda x: x.end_year)

    for i, project in enumerate(projects):
        _color = PROJECTS_COLOR_SEQUENCE[i]

        # Split the cost equally over the duration of the project
        cost = project.calc_project_cost()
        cost_yearly = cost / (project.end_year - project.start_year + 1)
        cost_list = np.zeros(len(years))
        for year in range(project.start_year, project.end_year):
            cost_list[year - start_program] = cost_yearly

        fig.add_trace(go.Bar(
            name=project.name,
            x=years,
            y=cost_list,
            offset=0,
            marker=dict(color=_color, pattern_shape='/'),

            # hovertemplate with start and end year, total cost cost of project
            hovertemplate=f"{project.name}<br>Startjaar: {project.start_year}<br>"
                          f"Eindjaar: {project.end_year}<br>"
                          f"Jaarlijkse Kosten: {cost_yearly / 1e6:.2f} mln €<br>"
                          f"Totale Kosten: {cost / 1e6:.1f} mln €<extra></extra>"
        ))

    fig.update_layout(template='plotly_white')
    fig.update_yaxes(title="Kosten (mln €/jaar)")
    fig.update_xaxes(title="Jaar")

    # no gap between bars
    fig.update_layout(barmode='stack', bargap=0)
    # put legend on the right
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    return fig


def projects_reliability_over_time(projects: list[DikeProject], imported_runs_data: dict,
                                   result_type: str) -> go.Figure:
    _fig = go.Figure()

    # first sort projects by ending year
    projects = sorted(projects, key=lambda x: x.end_year)

    for index, traject_data in enumerate(imported_runs_data.values()):
        color_traject = CLASSIC_PLOTLY_COLOR_SEQUENCE[index]

        dike_traject = DikeTraject.deserialize(traject_data)

        _traject_reliability = get_traject_reliability(dike_traject.dike_sections, 'initial')
        _traject_pf = get_traject_prob_fast(_traject_reliability)[1]
        _traject_betas = pf_to_beta(_traject_pf)

        # Initialize years and betas
        years_ini = np.linspace(2025, projects[0].end_year, projects[0].end_year - 2025 + 1)
        years_beta = np.array(dike_traject.dike_sections[0].years) + REFERENCE_YEAR
        betas_ini = interpolate_beta_values(years_ini, _traject_betas, years_beta)

        sections_to_reinforce=[]
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


        if result_type == ResultType.RELIABILITY.name:
            y = betas_ini
            y_ondergrens = [pf_to_beta(dike_traject.lower_bound_value)] * len(years_ini)
            # name = "Betrouwbaarheid"
            name = dike_traject.name
            hovertemplate = "Jaar: %{x}<br>	β = %{y:.2e}"

        elif result_type == ResultType.PROBABILITY.name:
            y = beta_to_pf(betas_ini)
            y_ondergrens = [dike_traject.lower_bound_value] * len(years_ini)
            name = "Faalkans"
            hovertemplate = "Jaar: %{x}<br>Faalkans: %{y:.2e}"
        elif result_type == ResultType.DISTANCE_TO_NORM.name:
            y = beta_to_pf(betas_ini) / dike_traject.lower_bound_value
            y_ondergrens = [1] * len(years_ini)
            name = "Afstand tot norm"
            hovertemplate = "Jaar: %{x}<br>Afstand tot norm: %{y:.2e}"
        elif result_type == ResultType.RISK.name:
            y = beta_to_pf(betas_ini) * dike_traject.flood_damage
            discount_rate = 0.03
            y_ondergrens = None
            name = "Risico (€/jaar)"
            hovertemplate = "Jaar: %{x}<br>Risico: %{y:.2e}"
        elif result_type == ResultType.RISK_FACTOR.name:
            risk = beta_to_pf(betas_ini) * dike_traject.flood_damage
            discount_rate = 0.03
            risk_norm = [dike_traject.lower_bound_value * dike_traject.flood_damage] / (1 + discount_rate) ** (
                    years_ini - 2025)
            y = risk / risk_norm
            y_ondergrens = None
            name = "Risicofactor"
            hovertemplate = "Jaar: %{x}<br>Factor hoger dan bij norm: %{y:.2e}"


        else:
            raise ValueError(f"Result type {result_type} not recognized")
        if y_ondergrens is not None:
            _fig.add_trace(go.Scatter(name="ondergrens",
                                      x=years_ini,
                                      y=y_ondergrens,
                                      line=dict(color=color_traject, dash="dot"),
                                      mode='lines',
                                      legendgroup=dike_traject.name,
                                      legendgrouptitle=dict(text=dike_traject.name),
                                      ))

        _fig.add_trace(go.Scatter(name=name,
                                  x=years_ini,
                                  y=y,
                                  marker=dict(color=color_traject),
                                  line=dict(color=color_traject),
                                  mode='lines+markers',
                                  legendgroup=dike_traject.name,
                                  legendgrouptitle=dict(text=dike_traject.name),
                                  hovertemplate=hovertemplate
                                  ))

    def add_shapes(y0, y1, y_text, color):
        _fig.add_shape(
            type="rect",
            x0=project.start_year,
            y0=y0,
            x1=project.end_year,
            y1=y1,
            fillcolor=color,
            opacity=0.5,
            layer="below",
            line_width=0,
        )

        # add invisible trace for hover info
        _fig.add_trace(go.Scatter(
            x=[(project.start_year + project.end_year) / 2],
            y=[(y0 + y1) / 2],
            text=[project.name],
            mode="markers",
            opacity=0,
            marker=dict(color=color, opacity=0),
            hoverinfo="text",
            showlegend=False,
        ))
        # add annotation in the middle of the shape:
        # THIS IS BUGGY
        # _fig.add_annotation(
        #     x=(project.start_year + project.end_year) / 2,
        #     y=y_text,
        #     text=project.name,
        #     showarrow=False,
        #     font=dict(color="black", size=18),
        # )

    projects = sorted(projects, key=lambda x: x.end_year)

    if result_type == ResultType.RELIABILITY.name:
        y0_ini = 0
        y1_ini = 0.5
        # Add project shapes:
        for index, project in enumerate(projects):
            color = PROJECTS_COLOR_SEQUENCE[index]
            y0 = y0_ini + y1_ini * index
            y1 = y1_ini + y1_ini * index
            y_text = 0.25 + 0.5 * index,
            add_shapes(y0, y1, y_text, color)

        _fig.update_layout(xaxis_title='Jaar', yaxis_title="Betrouwbaarheid")

    elif result_type == ResultType.PROBABILITY.name:
        _fig.update_yaxes(type="log")
        y0_ini = 10e-6
        y1_ini = y0_ini * 5  # This is the range for each shape in log scale

        # Add project shapes, similar to linear case:
        for index, project in enumerate(projects):
            color = PROJECTS_COLOR_SEQUENCE[index]
            y0 = y0_ini * (5 ** index)
            y1 = y1_ini * (5 ** index)
            y_text = y0_ini * (5 ** index)
            add_shapes(y0, y1, y_text, color)
        ticks = [1.e-6, 1.e-5, 1.e-4, 0.001, 0.01, 0.1, 1]
        _fig.update_yaxes(type="log", tickvals=ticks, ticktext=[str(tick) for tick in ticks])
        _fig.update_layout(xaxis_title='Jaar', yaxis_title="Faalkans")

    elif result_type == ResultType.DISTANCE_TO_NORM.name:
        _fig.update_yaxes(type="log")
        y0_ini = 0.001
        y1_ini = y0_ini * 5
        # Add project shapes, similar to linear case:
        for index, project in enumerate(projects):
            color = PROJECTS_COLOR_SEQUENCE[index]
            y0 = y0_ini * (5 ** index)
            y1 = y1_ini * (5 ** index)
            y_text = y0_ini * (5 ** index)
            add_shapes(y0, y1, y_text, color)
        ticks = [0.001, 0.01, 0.1, 1, 10]
        _fig.update_yaxes(type="log", tickvals=ticks, ticktext=[str(tick) for tick in ticks])
        _fig.update_layout(xaxis_title='Jaar', yaxis_title="Afstand tot norm")

    elif result_type == ResultType.RISK.name:
        _fig.update_layout(xaxis_title='Jaar', yaxis_title="Risico (€/jaar)")
        y0_ini = 10e3
        y1_ini = y0_ini * 5  # This is the range for each shape in log scale
        # Add project shapes:
        # Add project shapes, similar to linear case:
        for index, project in enumerate(projects):
            color = PROJECTS_COLOR_SEQUENCE[index]
            y0 = y0_ini * (5 ** index)
            y1 = y1_ini * (5 ** index)
            y_text = y0_ini * (5 ** index)
            add_shapes(y0, y1, y_text, color)
        ticks = [1e5, 1e6, 1e7, 1e8, 1e9]
        _fig.update_yaxes(type="log", tickvals=ticks, ticktext=[f"{tick:.2e}" for tick in ticks])

    elif result_type == ResultType.RISK_FACTOR.name:
        _fig.update_yaxes(type="log")
        y0_ini = 0.001
        y1_ini = y0_ini * 5
        # Add project shapes, similar to linear case:
        for index, project in enumerate(projects):
            color = PROJECTS_COLOR_SEQUENCE[index]
            y0 = y0_ini * (5 ** index)
            y1 = y1_ini * (5 ** index)
            y_text = y0_ini * (5 ** index)
            add_shapes(y0, y1, y_text, color)
        ticks = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
        _fig.update_yaxes(type="log", tickvals=ticks, ticktext=[str(tick) for tick in ticks])
        _fig.update_layout(xaxis_title='Jaar', yaxis_title="Risico factor")


    else:
        raise ValueError(f"Result type {result_type} not recognized")

    _fig.update_layout(template='plotly_white')
    return _fig
