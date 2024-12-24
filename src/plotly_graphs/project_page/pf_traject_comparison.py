from bisect import bisect_right
from typing import Optional

import numpy as np
import plotly.graph_objects as go

from src.constants import REFERENCE_YEAR, ResultType, ColorBarResultType, PROJECTS_COLOR_SEQUENCE, \
    CLASSIC_PLOTLY_COLOR_SEQUENCE
from src.linear_objects.dike_traject import DikeTraject, cum_cost_steps, get_step_traject_pf, get_initial_assessment_df, \
    get_traject_prob
from src.linear_objects.project import DikeProject
from src.utils.utils import pf_to_beta, beta_to_pf


def plot_default_scatter_dummy() -> go.Figure:
    """

    """
    fig = go.Figure()
    fig.update_layout(template='plotly_white')

    return fig


def plot_pf_project_comparison(project_data: dict, selected_year: int, result_type: str) -> go.Figure:
    """
    :return:
    """

    fig = go.Figure()

    x_max = 0
    for index, (_, dike_traject_data) in enumerate(project_data.items()):
        dike_traject = DikeTraject.deserialize(dike_traject_data)
        _year_index = bisect_right(dike_traject.dike_sections[0].years, selected_year - REFERENCE_YEAR) - 1

        section_order_vr = ["Geen maatregel"] + dike_traject.reinforcement_order_vr
        # greedy_step_order = ["Geen maatregel"] + [f"Stap {o}" for o in range(1, len(dike_traject.greedy_steps))]

        x_vr = dike_traject.get_cum_cost("vr")
        # x_step = cum_cost_steps(dike_traject)
        title_x_axis = "Kosten (mln €)"
        max_x = x_vr[-1]
        x_max = np.max([max_x, x_max])
        title_extra = "Faalkans i.r.t kosten"

        if result_type == ResultType.RELIABILITY.name:
            y_vr = pf_to_beta(dike_traject.calc_traject_probability_array("vr")[:, _year_index])
            # y_step = pf_to_beta(get_step_traject_pf(dike_traject)[:, _year_index])
            y_ondergrens = pf_to_beta(dike_traject.lower_bound_value)
            y_signalering = pf_to_beta(dike_traject.signalering_value)
            title_y_axis = "Betrouwbaarheid"


        else:
            y_vr = dike_traject.calc_traject_probability_array("vr")[:, _year_index]
            # y_step = get_step_traject_pf(dike_traject)[:, _year_index]
            y_ondergrens = dike_traject.lower_bound_value
            y_signalering = dike_traject.signalering_value
            title_y_axis = "Trajectfaalkans per jaar"

        color = CLASSIC_PLOTLY_COLOR_SEQUENCE[index]
        if index == 0:
            add_signaleringswaarde(fig, max_x, y_signalering, y_ondergrens)

        fig.add_trace(go.Scatter(x=x_vr,
                                 y=y_vr,
                                 customdata=section_order_vr,
                                 mode='markers+lines',
                                 name=dike_traject.run_name,
                                 line=dict(color=color),
                                 marker=dict(size=6, color=color),
                                 hovertemplate="<b>%{customdata}</b><br><br>" +
                                               "Trajectfaalkans: %{y:.2e}<br>"
                                 ))

    fig.update_xaxes(range=[0, x_max], title=title_x_axis)
    fig.update_layout(title=title_extra, yaxis_title=title_y_axis, xaxis_title=title_x_axis)
    if result_type == ResultType.RELIABILITY.name:
        fig.update_yaxes(range=[None, 6])
    elif result_type == ResultType.PROBABILITY.name:

        fig.update_yaxes(range=[None, 1e-7],
                         type='log',
                         exponentformat='power',
                         )

    fig.update_layout(showlegend=True, template='plotly_white')

    return fig


def add_signaleringswaarde(fig, max_x, y_signalering, y_ondergrens):
    fig.add_trace(go.Scatter(
        x=[0, max_x],
        y=[y_ondergrens, y_ondergrens],
        mode="lines",
        marker=dict(size=0),
        showlegend=True,
        name="Ondergrens",
        line=dict(color='black', dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=[0, max_x],
        y=[y_signalering, y_signalering],
        mode="lines",
        marker=dict(size=0),
        showlegend=True,
        name="Signaleringswaarde",
        line=dict(color='black', dash='dot')
    ))


def plot_pf_time_runs_comparison(imported_runs_data: dict):
    fig = go.Figure()

    for index, (_, dike_traject_data) in enumerate(imported_runs_data.items()):
        dike_traject = DikeTraject.deserialize(dike_traject_data)
        legend_group = dike_traject.name + "|" + dike_traject.run_name
        color = CLASSIC_PLOTLY_COLOR_SEQUENCE[index]

        x_vr = dike_traject.get_cum_cost("vr")
        max_x = x_vr[-1]
        hover_extra = "Jaar: €%{x:.2f} mln<br>"

        initial_df = get_initial_assessment_df(dike_traject.dike_sections)
        initial_traject_pf_array, _ = get_traject_prob(initial_df)
        initial_traject_pf = pf_to_beta(initial_traject_pf_array[0, 0])

        y_vr = pf_to_beta(dike_traject.calc_traject_probability_array("vr")[-1, :])
        y_dsn = pf_to_beta(dike_traject.calc_traject_probability_array("dsn")[-1, :])

        # add initial pf at first position:
        y_vr = np.insert(y_vr, 0, initial_traject_pf)
        years = np.insert(dike_traject.dike_sections[0].years, 0, 0) + REFERENCE_YEAR

        fig.add_trace(go.Scatter(x=years,
                                 y=y_vr,
                                 legendgroup=legend_group,
                                 legendgrouptitle=dict(text=legend_group),
                                 mode='markers+lines',
                                 name='Veiligheidsrendement',
                                 line=dict(color=color),
                                 marker=dict(size=6, color=color),
                                 hovertemplate="Trajectfaalkans: %{y:.2e}<br>" + hover_extra
                                 ))

    fig.update_layout(template='plotly_white')
    fig.update_yaxes(title="Betrouwbaarheid")
    fig.update_xaxes(title="Investering jaar")

    fig.update_layout(barmode='group',
                      bargroupgap=0.1, )
    return fig
