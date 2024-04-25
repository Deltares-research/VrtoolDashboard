from bisect import bisect_right
from typing import Optional

import numpy as np
import plotly.graph_objects as go
from pandas import DataFrame

from src.constants import REFERENCE_YEAR, ResultType, CalcType, Mechanism
from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject, cum_cost_steps, get_step_traject_pf
from src.utils.utils import pf_to_beta, beta_to_pf


def plot_measure_results_graph(measure_results: DataFrame, dike_section: DikeSection,
                               mechanism: Mechanism) -> go.Figure:
    """
    """
    fig = go.Figure()

    # Add traces for the measures (uncombined)
    custom = np.stack((measure_results['measure'], measure_results['dberm'], measure_results['dcrest']), axis=-1)

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

    # Add traces for the final measures
    add_trace_run_results(fig, dike_section.final_measure_doorsnede, CalcType.DOORSNEDE_EISEN, mechanism)
    add_trace_run_results(fig, dike_section.final_measure_veiligheidsrendement, CalcType.VEILIGHEIDSRENDEMENT,
                          mechanism)

    ## Update layout
    fig.update_layout(
        title=f"Maatregelen dijkvak {dike_section.name} {mechanism.value}",
        xaxis_title="LCC (mln €)",
        yaxis_title=r'$ \beta $',
        template='ggplot2'
    )

    return fig


def add_trace_run_results(fig: go.Figure, taken_measures: dict, calc_type: CalcType, mechanism: Mechanism):
    if taken_measures['name'] == 'Geen maatregel':
        hover_extra = ""
    else:
        hover_extra = f"Dberm: {taken_measures.get('dberm', None)}m<br>" + f"Dcrest: {taken_measures.get('dcrest', None)}m<br>"

    if calc_type == CalcType.VEILIGHEIDSRENDEMENT:
        name = 'Veiligheidsrendement'
        color = "green"
    elif calc_type == CalcType.DOORSNEDE_EISEN:
        name = 'Doorsnede'
        color = "blue"
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
        x=[taken_measures['LCC'] / 1e6],
        y=[taken_measures[meca_key][0]],
        mode='markers',
        marker=dict(
            size=8,
            color=color,
        ),
        hovertemplate=f"<b>{taken_measures['name']}</b><br><br>" +
                      "Beta: %{y:.2f}<br>" +
                      "LCC: €%{x:.2f} mln<br>" + hover_extra

    ))
