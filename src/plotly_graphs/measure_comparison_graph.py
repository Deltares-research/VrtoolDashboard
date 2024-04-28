from bisect import bisect_right
from typing import Optional

import numpy as np
import plotly.graph_objects as go
from pandas import DataFrame

from src.constants import REFERENCE_YEAR, ResultType, CalcType, Mechanism
from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject, cum_cost_steps, get_step_traject_pf
from src.utils.utils import pf_to_beta, beta_to_pf


def plot_measure_results_graph(measure_results: DataFrame, vr_steps: list[dict], dsn_steps: list[dict],
                               mechanism: Mechanism) -> go.Figure:
    """
    Make the plot Beta vs cost comparing all the measures for a dike section.
    
    :param measure_results: Dataframe containing the data (beta,LCC) for all the filtered measures from a dijkvak
    :param vr_steps: list of all the step measures for GreedyOptimization (veiligheidsrendement)
    :param dsn_steps: the single step measure for Doorsnede-eis.
    :param mechanism: Mechanism for which to display the beta.
    :return: 
    """""
    fig = go.Figure()

    # Add traces for the measures (uncombined)
    custom = np.stack(
        (measure_results['measure'], measure_results.get('dberm', None),
         measure_results.get('dcrest', None)),
        axis=-1)

    fig.add_trace(go.Scatter(
        name='Maatregelen',
        x=measure_results['LCC'] / 1e6,
        y=measure_results['beta'],
        customdata=custom,
        mode='markers',
        marker=dict(
            size=8,
            color='black',
        ),
        hovertemplate="<b>%{customdata[0]}</b><br><br>" +
                      "Dberm: %{customdata[1]}m<br>" +
                      "Dcrest: %{customdata[2]}m<br>" +
                      "Beta: %{y:.2f}<br>" +
                      "LCC: €%{x:.2f} mln<br>"
    ))

    # # Add traces for the final measures
    add_trace_run_results(fig, dsn_steps, CalcType.DOORSNEDE_EISEN, mechanism)
    add_trace_run_results(fig, vr_steps, CalcType.VEILIGHEIDSRENDEMENT, mechanism)

    ## Update layout
    fig.update_layout(
        title=f"Maatregelen dijkvak {mechanism.value}",
        xaxis_title="LCC (mln €)",
        yaxis_title='Beta',
        template='ggplot2'
    )

    return fig


def add_trace_run_results(fig: go.Figure, step_measures: list[dict], calc_type: CalcType, mechanism: Mechanism):
    """
    Add traces for the provided step_measures (either Veiligheidsrendement or doorsnede)
    :param fig:
    :param step_measures:
    :param calc_type:
    :param mechanism:
    :return:
    """
    for step_number, taken_measure in enumerate(step_measures):

        if taken_measure['name'] == 'Geen maatregel':
            hover_extra = ""
        else:
            hover_extra = f"Dberm: {taken_measure.get('dberm', None)}m<br>" + f"Dcrest: {taken_measure.get('dcrest', None)}m<br>"

        if calc_type == CalcType.VEILIGHEIDSRENDEMENT:
            name = 'Veiligheidsrendement'
            color = "green" if step_number != len(step_measures) - 1 else 'red'

            legendgroup = 'Veiligheidsrendement'
        elif calc_type == CalcType.DOORSNEDE_EISEN:
            name = 'Doorsnede'
            color = "blue"
            legendgroup = 'Doorsnede'
        else:
            raise ValueError(f"CalcType {calc_type} not recognized")

        if mechanism.name == Mechanism.SECTION.name:
            meca_key = "Section"
        elif mechanism.name == Mechanism.STABILITY.name:
            meca_key = "StabilityInner"
        elif mechanism.name == Mechanism.PIPING.name:
            meca_key = "Piping"
        elif mechanism.name == Mechanism.OVERFLOW.name:
            meca_key = "Overflow"
        elif mechanism.name == Mechanism.REVETMENT:
            meca_key = "Revetment"
        else:
            raise NotImplementedError(f"Mechanism {mechanism} not implemented")

        fig.add_trace(go.Scatter(
            name=name,
            legendgroup=legendgroup,
            showlegend=True if step_number == 0 else False,
            x=[taken_measure['LCC'] / 1e6],
            y=[taken_measure[meca_key][0]],
            mode='markers',
            marker=dict(
                size=10 if step_number == len(step_measures) - 1 else 8,
                color=color,
                symbol='diamond' if step_number == len(step_measures) - 1 else 'circle',
            ),
            hovertemplate=f"<b>Stap {step_number} {taken_measure['name']}</b><br><br>" +
                          "Beta: %{y:.2f}<br>" +
                          "LCC: €%{x:.2f} mln<br>" + hover_extra

        ))

        fig.add_annotation(
            text=f'{step_number}',

            x=taken_measure['LCC'] / 1e6,
            y=taken_measure[meca_key][0],
        )
