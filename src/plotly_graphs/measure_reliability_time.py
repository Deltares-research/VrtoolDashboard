import plotly.graph_objects as go
from pandas import DataFrame

from src.constants import REFERENCE_YEAR, Mechanism


def plot_measure_results_over_time_graph(
    meas_betas: list[float],
    init_betas: list[float],
    years: list[float],
    measure_data: dict,
) -> go.Figure:
    """

    :param meas_betas: betas for the clicked measure_result (combination Section/Mechanism)
    :param init_betas: betas of the initial assessment for the corresponding section & mechanism
    :param years: years for which the betas are available
    :param measure_data: dictionary with metadata of the measure result: name, dberm, dcrest, ...
    :return:
    """
    _fig = go.Figure()

    _years = [y + REFERENCE_YEAR for y in years]

    _fig.add_trace(
        go.Scatter(
            x=_years,
            y=meas_betas,
            mode="lines+markers",
            name=f"Maatregel",
            marker=dict(
                size=8,
                color="black",
            ),
            hovertemplate="<b>%{x}</b><br><br>" "Beta: %{y:.2f}<br>",
        )
    )

    _fig.add_trace(
        go.Scatter(
            x=_years,
            y=init_betas,
            mode="lines+markers",
            name=f"Beoordeling",
            marker=dict(
                size=8,
                color="red",
            ),
            hovertemplate="<b>%{x}</b><br><br>" "Beta: %{y:.2f}<br>",
        )
    )

    _fig.update_layout(
        title=f"{measure_data['measure_name']} <br>"
        f"dberm={measure_data['dberm']}m <br>"
        f"dcrest={measure_data['dcrest']}m",
        xaxis_title="Jaar",
        yaxis_title="Beta",
    )

    return _fig


def update_measure_results_over_time_graph(fig: dict, click_data: dict) -> go.Figure:
    """Update the plotly figure of the measure results over time with the clicked measure results to
    highlight the combined measures. The opacity of the other measures is reduced.

    :param fig: plotly figure object saved as a dict
    :param click_data: click event data

    :return: updated plotly figure object

    """
    _fig = go.Figure(fig)
    # update the opacity of the first trace :
    _fig.update_traces(marker=dict(opacity=0.3))
    click_custom_data = click_data["points"][0]["customdata"]
    measure_results_ids = list(map(int, click_custom_data.split(" + ")))

    measure_fig_data = fig["data"][0]
    for id, point in enumerate(measure_fig_data["customdata"]):
        if point[3] in measure_results_ids:
            _fig.add_trace(
                go.Scatter(
                    name="clicked",
                    x=[measure_fig_data["x"][id]],
                    y=[measure_fig_data["y"][id]],
                    mode="markers",
                    marker=dict(size=10, color="black"),
                    showlegend=False,
                    hovertemplate=f"{point[0]}  <br>"
                    f"Dberm: {point[1]}m <br>"
                    f"Dcrest: {point[2]}m <br>",
                )
            )
    return _fig
