from bisect import bisect_right

import numpy as np
import plotly.graph_objects as go

from src.constants import REFERENCE_YEAR, ResultType
from src.linear_objects.dike_traject import DikeTraject
from src.utils.utils import pf_to_beta


def plot_default_scatter_dummy() -> go.Figure:
    """

    """
    fig = go.Figure()
    fig.update_layout(template='plotly_white')

    return fig


def plot_pf_length_cost(dike_traject: DikeTraject, selected_year: float, result_type: str,
                        cost_length_switch: str) -> go.Figure:
    """

    :param dike_traject:
    :param selected_year:
    :param result_type:
    :param cost_length_switch:

    :return:
    """


    fig = go.Figure()
    _year_index = bisect_right(dike_traject.dike_sections[0].years, selected_year - REFERENCE_YEAR) - 1

    section_order_dsn = ["Geen maatregel"] + dike_traject.reinforcement_order_dsn
    section_order_vr = ["Geen maatregel"] + dike_traject.reinforcement_order_vr

    if cost_length_switch == "COST":
        x_vr = dike_traject.get_cum_cost("vr")
        x_dsn = dike_traject.get_cum_cost("dsn")
        title_x_axis = "Kosten (mln €)"
        max_x = max(x_vr[-1], x_dsn[-1])
    elif cost_length_switch == "LENGTH":
        x_vr = dike_traject.get_cum_length("vr")
        x_dsn = dike_traject.get_cum_length("dsn")
        title_x_axis = "Lengte (km)"
        max_x = max(x_vr[-1], x_dsn[-1])
    else:
        raise ValueError("Wrong cost_length_switch value")

    if result_type == ResultType.RELIABILITY.name:
        y_vr = pf_to_beta(dike_traject.calc_traject_probability_array("vr")[:, _year_index])
        y_dsn = pf_to_beta(dike_traject.calc_traject_probability_array("dsn")[:, _year_index])
        title_y_axis = "Betrouwbaarheid"
        y_ondergrens = pf_to_beta(dike_traject.lower_bound_value)
        y_signalering = pf_to_beta(dike_traject.signalering_value)

    elif result_type == ResultType.PROBABILITY.name:
        y_vr = dike_traject.calc_traject_probability_array("vr")[:, _year_index]
        y_dsn = dike_traject.calc_traject_probability_array("dsn")[:, _year_index]
        title_y_axis = "Trajectfaalkans per jaar"
        y_ondergrens = dike_traject.lower_bound_value
        y_signalering = dike_traject.signalering_value

    else:
        raise ValueError("Wrong result_type value")

    # add traces for Veiligheidrendement and Doorsnede-eisen

    fig.add_trace(go.Scatter(x=x_dsn,
                             y=y_dsn,
                             customdata=section_order_dsn,
                             mode='markers+lines',
                             name='Doorsnede-eisen',
                             line=dict(color='blue'),
                             marker=dict(size=6, color='blue'),
                             hovertemplate="<b>%{customdata}</b><br><br>" +
                                           "Kosten: €%{x:.2f} mln<br>" +
                                           "Trajectfaalkans: %{y:.2e}<br>"
                             ))

    fig.add_trace(go.Scatter(x=x_vr,
                             y=y_vr,
                             customdata=section_order_vr,
                             mode='markers+lines',
                             name='Veiligheidsrendement',
                             line=dict(color='gold'),
                             marker=dict(size=6, color='gold'),
                             hovertemplate="<b>%{customdata}</b><br><br>" +
                                           "Kosten: €%{x:.2f} mln<br>" +
                                           "Trajectfaalkans: %{y:.2e}<br>"
                             ))

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

    # add annotations for dijkvaken order:
    for index, (x, section_name) in enumerate(zip(x_vr[1:], section_order_vr[1:])):
        sign = 1 if index % 2 == 0 else -1
        fig.add_annotation(x=x,
                           y=1 + sign * 0.15,
                           text=section_name,
                           textangle=270,
                           showarrow=False,
                           font=dict(size=14, color='gold'),
                           )

    for index, (x, section_name) in enumerate(zip(x_dsn[1:], section_order_dsn[1:])):
        sign = 1 if index % 2 == 0 else -1
        fig.add_annotation(x=x,
                           y=0 + sign * 0.15,
                           text=section_name,
                           textangle=270,
                           showarrow=False,
                           font=dict(size=14, color='blue'),
                           )

    x_max = np.max([np.max(x_vr), np.max(x_dsn)])
    fig.update_xaxes(range=[0, x_max], title=title_x_axis)
    fig.update_layout(title=f'Faalkans i.r.t. kosten ({selected_year})', yaxis_title=title_y_axis)

    if result_type == ResultType.RELIABILITY.name:
        fig.update_yaxes(range=[None, 6])
    elif result_type == ResultType.PROBABILITY.name:

        fig.update_yaxes(range=[None, 1e-7],
                         type='log',
                         exponentformat='power',
                         )
    fig.update_layout(showlegend=True, template='plotly_white')

    return fig
