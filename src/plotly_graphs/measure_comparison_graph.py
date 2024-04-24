from bisect import bisect_right
from typing import Optional

import numpy as np
import plotly.graph_objects as go
from pandas import DataFrame

from src.constants import REFERENCE_YEAR, ResultType
from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject, cum_cost_steps, get_step_traject_pf
from src.utils.utils import pf_to_beta, beta_to_pf


def plot_measure_results_graph(measure_results: DataFrame, dike_section: DikeSection) -> go.Figure:
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

    # Add traces for the selected measure of Doorsnede-eis:
    dsn_results = dike_section.final_measure_doorsnede
    if dsn_results['name'] == 'Geen maatregel':
        hover_extra = ""
    else:
        hover_extra = f"Dberm: {dsn_results['dberm']}m<br>" + f"Dcrest: {dsn_results['dcrest']}m<br>"
    fig.add_trace(go.Scatter(
        name=f'Doorsnede {dsn_results["name"]}',
        x=[dsn_results['LCC'] / 1e6],
        y=[dsn_results['Section'][0]],
        mode='markers',
        marker=dict(
            size=8,
            color='red',
        ),
        hovertemplate=f"<b>Doorsnede</b><br><br>" +
                      "Beta: %{y:.2f}<br>" +
                      "LCC: €%{x:.2f} mln<br>" + hover_extra

    ))

    # Add traces for the selected measure of Veiligheidsrendement:
    vr_results = dike_section.final_measure_veiligheidsrendement
    if vr_results['name'] == 'Geen maatregel':
        hover_extra = ""
    else:
        hover_extra = f"Dberm: {vr_results['dberm']}m<br>" + f"Dcrest: {vr_results['dcrest']}m<br>"

    fig.add_trace(go.Scatter(
        name=f'Veiligheidsrendement {vr_results["name"]}',
        x=[vr_results['LCC'] / 1e6],
        y=[vr_results['Section'][0]],
        mode='markers',
        marker=dict(
            size=8,
            color='blue',
        ),
        hovertemplate=f"<b>Veiligheidsrendement</b><br><br>" +
                      "Beta: %{y:.2f}<br>" +
                      "LCC: €%{x:.2f} mln<br>" + hover_extra
    ))

    ## Update layout
    fig.update_layout(
        title=f"Maatregelen dijkvak {dike_section.name}",
        xaxis_title="LCC (mln €)",
        yaxis_title="Betrouwbaarheid",
        template='ggplot2'
    )

    return fig
