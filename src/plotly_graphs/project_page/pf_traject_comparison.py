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


def plot_pf_project_comparison(project_data: dict, selected_year) -> go.Figure:
    """
    :return:
    """

    fig = go.Figure()
    for index, (_, dike_traject_data) in enumerate(project_data.items()):
        dike_traject = DikeTraject.deserialize(dike_traject_data)
        _year_index = bisect_right(dike_traject.dike_sections[0].years, selected_year - REFERENCE_YEAR) - 1

        section_order_vr = ["Geen maatregel"] + dike_traject.reinforcement_order_vr
        # greedy_step_order = ["Geen maatregel"] + [f"Stap {o}" for o in range(1, len(dike_traject.greedy_steps))]

        x_vr = dike_traject.get_cum_cost("vr")
        # x_step = cum_cost_steps(dike_traject)
        title_x_axis = "Kosten (mln €)"
        max_x = x_vr[-1]
        title_extra = "Faalkans i.r.t kosten"

        y_vr = pf_to_beta(dike_traject.calc_traject_probability_array("vr")[:, _year_index])
        # y_step = pf_to_beta(get_step_traject_pf(dike_traject)[:, _year_index])

        title_y_axis = "Betrouwbaarheid"
        y_ondergrens = pf_to_beta(dike_traject.lower_bound_value)
        y_signalering = pf_to_beta(dike_traject.signalering_value)

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



        x_max = np.max([np.max(x_vr)])
        fig.update_xaxes(range=[0, x_max], title=title_x_axis)
        fig.update_layout(title=title_extra, yaxis_title=title_y_axis, xaxis_title=title_x_axis)

        fig.update_yaxes(range=[None, 6])

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

def plot_pf_time_runs_comparison(imported_runs_data: dict, switch_cost_beta: str):
    fig = go.Figure()

    for _, dike_traject_data in imported_runs_data.items():
        dike_traject = DikeTraject.deserialize(dike_traject_data)
        legend_group = dike_traject.name + "|" + dike_traject.run_name
        # pick a random color
        color = f"rgb({np.random.randint(0, 255)}, {np.random.randint(0, 255)}, {np.random.randint(0, 255)})"

        if switch_cost_beta == ColorBarResultType.RELIABILITY.name:
            x_vr = dike_traject.get_cum_cost("vr")
            x_dsn = dike_traject.get_cum_cost("dsn")
            max_x = max(x_vr[-1], x_dsn[-1])
            hover_extra = "Jaar: €%{x:.2f} mln<br>"
            title_extra = "Faalkans i.r.t. kosten"

            initial_df = get_initial_assessment_df(dike_traject.dike_sections)
            initial_traject_pf_array, _ = get_traject_prob(initial_df)
            initial_traject_pf = pf_to_beta(initial_traject_pf_array[0, 0])

            y_vr = pf_to_beta(dike_traject.calc_traject_probability_array("vr")[-1, :])
            y_dsn = pf_to_beta(dike_traject.calc_traject_probability_array("dsn")[-1, :])

            # add initial pf at first position:
            y_vr = np.insert(y_vr, 0, initial_traject_pf)
            y_dsn = np.insert(y_dsn, 0, initial_traject_pf)
            years = np.insert(dike_traject.dike_sections[0].years, 0, 0) + REFERENCE_YEAR

            fig.add_trace(go.Scatter(x=years,
                                     y=y_dsn,
                                     legendgroup=legend_group,
                                     legendgrouptitle=dict(text=legend_group),
                                     # customdata=section_order_dsn,
                                     mode='markers+lines',
                                     name='Doorsnede-eisen',
                                     line=dict(color='blue'),
                                     marker=dict(size=6, color='blue'),
                                     hovertemplate="<b>%{customdata}</b><br><br>" +
                                                   "Trajectfaalkans: %{y:.2e}<br>" + hover_extra
                                     ))
            fig.add_trace(go.Scatter(x=years,
                                     y=y_vr,
                                     legendgroup=legend_group,
                                     legendgrouptitle=dict(text=legend_group),
                                     # customdata=section_order_vr,
                                     mode='markers+lines',
                                     name='Veiligheidsrendement',
                                     line=dict(color='green'),
                                     marker=dict(size=6, color='green'),
                                     hovertemplate="<b>%{customdata}</b><br><br>" +
                                                   "Trajectfaalkans: %{y:.2e}<br>" + hover_extra
                                     ))


        elif switch_cost_beta == ColorBarResultType.COST.name:

            cost_dict = {}
            for section_name in dike_traject.reinforcement_order_dsn:
                section = dike_traject.get_section(section_name)
                lcc = section.final_measure_doorsnede["LCC"] / 1e6
                investment_year = section.final_measure_doorsnede["investment_year"][
                    0]  # TODO: separate for combined measure with different investment years
                if investment_year not in cost_dict:
                    cost_dict[investment_year] = lcc
                else:
                    cost_dict[investment_year] += lcc

            sorted_data = sorted(cost_dict.items())
            years = np.insert([k for k, v in sorted_data], 0, 0) + REFERENCE_YEAR
            y_dsn = np.insert([v for k, v in sorted_data], 0, 0)

            fig.add_trace(go.Bar(
                x=years,
                y=y_dsn,
                marker=dict(color=color),
                legendgroup=legend_group,
                legendgrouptitle=dict(text=legend_group),
                name='Doorsnede-eisen',
            ))

            cost_dict = {}
            for section_name in dike_traject.reinforcement_order_vr:
                section = dike_traject.get_section(section_name)
                lcc = section.final_measure_doorsnede["LCC"] / 1e6
                investment_year = section.final_measure_doorsnede["investment_year"][
                    0]  # TODO: separate for combined measure with different investment years
                if investment_year not in cost_dict:
                    cost_dict[investment_year] = lcc
                else:
                    cost_dict[investment_year] += lcc

            sorted_data = sorted(cost_dict.items())
            years = np.insert([k for k, v in sorted_data], 0, 0) + REFERENCE_YEAR
            y_dsn = np.insert([v for k, v in sorted_data], 0, 0)
            fig.add_trace(go.Bar(
                x=years,
                y=y_dsn,
                marker=dict(color=color, pattern_shape='/'),
                legendgroup=legend_group,
                legendgrouptitle=dict(text=legend_group),
                name='Veiligheidsrendement',

            ))





        else:
            raise ValueError(f"Invalid switch_cost_beta value: {switch_cost_beta}")

    fig.update_layout(template='plotly_white')
    fig.update_yaxes(title="Kosten (mln €)")
    fig.update_xaxes(title="Investering jaar")

    fig.update_layout(barmode='group',
                      bargroupgap=0.1, )
    return fig
