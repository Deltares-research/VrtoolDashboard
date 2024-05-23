import plotly.graph_objects as go
from pandas import DataFrame

from src.constants import Mechanism, REFERENCE_YEAR


def plot_measure_results_over_time_graph(
        meas_betas: list[float],
        init_betas: list[float],
        mechanism: Mechanism,
        section_name: str,
        years: list[float],
        measure_data: dict,
) -> go.Figure:
    """

    :param meas_betas: betas for the clicked measure_result (combination Section/Mechanism)
    :param init_betas: betas of the initial assessment for the corresponding section & mechanism
    :param mechanism: mechanism of the clicked measure_result
    :param section_name: section name of the clicked measure_result
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
            hovertemplate="<b>%{x}</b><br><br>"
                          "Beta: %{y:.2f}<br>",
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
            hovertemplate="<b>%{x}</b><br><br>"
                          "Beta: %{y:.2f}<br>",
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
