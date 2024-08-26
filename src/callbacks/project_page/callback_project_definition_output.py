from dash import callback, Output, Input, html, dcc, State

from src.component_ids import STORED_IMPORTED_RUNS_DATA, OVERVIEW_PROJECT_MAP_ID, STORED_PROJECT_OVERVIEW_DATA
from src.constants import get_mapbox_token
from src.layouts.layout_project_page.layout_project_definition_tab import project_definition_tab_layout
from src.plotly_graphs.plotly_maps import plot_default_overview_map_dummy
from src.plotly_graphs.project_page.plotly_maps import plot_project_overview_map


@callback(Output(OVERVIEW_PROJECT_MAP_ID, "children"),
          [Input(STORED_IMPORTED_RUNS_DATA, "data"),
           State(STORED_PROJECT_OVERVIEW_DATA, "data"),
           Input("tabs_tab_project_page", "active_tab")])
def make_graph_overview_dike(imported_runs_data: dict, project_data: list[dict], dummy: str) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data: The data of the dike traject to be displayed.
    """
    if imported_runs_data is None or imported_runs_data == {}:
        _fig = plot_default_overview_map_dummy()
    else:
        _fig = plot_project_overview_map(imported_runs_data, project_data)
    return dcc.Graph(
        figure=_fig,
        style={"width": "100%", "height": "100%"},
        config={"mapboxAccessToken": get_mapbox_token()},
    )
