import plotly.graph_objects as go
from pandas import DataFrame

from src.constants import Mechanism


def plot_measure_results_over_time_graph(
        meas_betas: list[float],
        init_betas: list[float],
        mechanism: Mechanism,
        section_name: str,
        years: list[float],
) -> go.Figure:
    _fig = go.Figure()

    _fig.add_trace(
        go.Scatter(
            x=years,
            y=meas_betas,
            mode="lines+markers",
            name=f"{mechanism} - {section_name}",
            marker=dict(
                size=8,
                color="black",
            ),
            hovertemplate="<b>%{x}</b><br><br>"
                          "Beta: %{y:.2f}<br>",
        )
    )

    _fig.add_trace(
        go.Scatter(
            x=years,
            y=init_betas,
            mode="lines+markers",
            name=f"Initial - {section_name}",
            marker=dict(
                size=8,
                color="red",
            ),
            hovertemplate="<b>%{x}</b><br><br>"
                          "Beta: %{y:.2f}<br>",
        )
    )

    return _fig
