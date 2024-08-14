from bisect import bisect_right
from typing import Optional

import numpy as np
import plotly.graph_objects as go

from src.constants import REFERENCE_YEAR, ResultType
from src.linear_objects.dike_traject import DikeTraject, cum_cost_steps, get_step_traject_pf
from src.utils.utils import pf_to_beta, beta_to_pf


def plot_default_scatter_dummy() -> go.Figure:
    """

    """
    fig = go.Figure()
    fig.update_layout(template='plotly_white')

    return fig


def plot_pf_project_comparison(project_data: dict, selected_year) -> go.Figure:
    """
    :return:
    """

    fig = go.Figure()

    for _, dike_traject_data in project_data.items():
        dike_traject = DikeTraject.deserialize(dike_traject_data)
        _year_index = bisect_right(dike_traject.dike_sections[0].years, selected_year - REFERENCE_YEAR) - 1

        section_order_dsn = ["Geen maatregel"] + dike_traject.reinforcement_order_dsn
        section_order_vr = ["Geen maatregel"] + dike_traject.reinforcement_order_vr
        # greedy_step_order = ["Geen maatregel"] + [f"Stap {o}" for o in range(1, len(dike_traject.greedy_steps))]

        x_vr = dike_traject.get_cum_cost("vr")
        x_dsn = dike_traject.get_cum_cost("dsn")
        # x_step = cum_cost_steps(dike_traject)
        title_x_axis = "Kosten (mln €)"
        max_x = max(x_vr[-1], x_dsn[-1])
        hover_extra = "Kosten: €%{x:.2f} mln<br>"
        title_extra = "Faalkans i.r.t. kosten"

        y_vr = pf_to_beta(dike_traject.calc_traject_probability_array("vr")[:, _year_index])
        y_dsn = pf_to_beta(dike_traject.calc_traject_probability_array("dsn")[:, _year_index])
        # y_step = pf_to_beta(get_step_traject_pf(dike_traject)[:, _year_index])

        title_y_axis = "Betrouwbaarheid"
        y_ondergrens = pf_to_beta(dike_traject.lower_bound_value)
        y_signalering = pf_to_beta(dike_traject.signalering_value)

        legend_group = dike_traject.name + "|" + dike_traject.run_name
        print(legend_group)

        # add traces for Veiligheidrendement and Doorsnede-eisen

        fig.add_trace(go.Scatter(x=x_dsn,
                                 y=y_dsn,
                                 legendgroup=legend_group,
                                 legendgrouptitle=dict(text=legend_group),
                                 customdata=section_order_dsn,
                                 mode='markers+lines',
                                 name='Doorsnede-eisen',
                                 line=dict(color='blue'),
                                 marker=dict(size=6, color='blue'),
                                 hovertemplate="<b>%{customdata}</b><br><br>" +
                                               "Trajectfaalkans: %{y:.2e}<br>" + hover_extra
                                 ))

        fig.add_trace(go.Scatter(x=x_vr,
                                 y=y_vr,
                                 legendgroup=legend_group,
                                 legendgrouptitle=dict(text=legend_group),
                                 customdata=section_order_vr,
                                 mode='markers+lines',
                                 name='Veiligheidsrendement',
                                 line=dict(color='green'),
                                 marker=dict(size=6, color='green'),
                                 hovertemplate="<b>%{customdata}</b><br><br>" +
                                               "Trajectfaalkans: %{y:.2e}<br>" + hover_extra
                                 ))

        # fig.add_trace(go.Scatter(x=x_step,
        #                          y=y_step,
        #                          customdata=greedy_step_order,
        #                          mode='markers+lines',
        #                          name='Optimalisatie stappen',
        #                          line=dict(color='green', dash='dot'),
        #                          marker=dict(size=3, color='green'),
        #                          hovertemplate="<b>%{customdata}</b><br><br>" +
        #                                        "Trajectfaalkans: %{y:.2e}<br>" + hover_extra
        #                          ))

        fig.add_trace(go.Scatter(
            x=[0, max_x],
            y=[y_ondergrens, y_ondergrens],
            mode="lines",
            marker=dict(size=0),
            showlegend=True,
            name="Ondergrens",
            legendgroup=legend_group,
            legendgrouptitle=dict(text=legend_group),
            line=dict(color='black', dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=[0, max_x],
            y=[y_signalering, y_signalering],
            mode="lines",
            marker=dict(size=0),
            showlegend=True,
            name="Signaleringswaarde",
            legendgroup=legend_group,
            legendgrouptitle=dict(text=legend_group),
            line=dict(color='black', dash='dot')
        ))

        x_max = np.max([np.max(x_vr), np.max(x_dsn)])
        # fig.update_xaxes(range=[0, x_max], title=title_x_axis)
        fig.update_layout(title=title_extra + f'TODO year', yaxis_title=title_y_axis)

        fig.update_yaxes(range=[None, 6])

        fig.update_layout(showlegend=True, template='plotly_white')

    return fig
