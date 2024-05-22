import plotly.graph_objects as go
from pandas import DataFrame

from src.constants import Mechanism


def plot_measure_results_over_time_graph(
        # measure_results: DataFrame,
        vr_steps: list[dict],
        dsn_steps: list[dict],
        mechanism: Mechanism,
        section_name: str,
        year_index: int,
) -> go.Figure:
    _fig = go.Figure()



    return _fig
