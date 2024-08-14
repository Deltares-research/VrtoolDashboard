from dash import callback, Output, Input, html, dcc

from src.component_ids import STORED_PROJECT_DATA, OVERVIEW_PROJECT_MAP_ID
from src.constants import get_mapbox_token
from src.layouts.layout_project_page.layout_project_definition_tab import project_definition_tab_layout
from src.plotly_graphs.plotly_maps import plot_default_overview_map_dummy
from src.plotly_graphs.project_page.plotly_maps import plot_project_overview_map


@callback(Output(OVERVIEW_PROJECT_MAP_ID, "children"),
          [Input(STORED_PROJECT_DATA, "data"),
           Input("tabs_tab_project_page", "active_tab")])
def make_graph_overview_dike(project_data: dict, dummy: str) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data: The data of the dike traject to be displayed.
    """
    if project_data is None or project_data == {}:
        _fig = plot_default_overview_map_dummy()
    else:
        _fig = plot_project_overview_map(project_data)
    return dcc.Graph(
        figure=_fig,
        style={"width": "100%", "height": "100%"},
        config={"mapboxAccessToken": get_mapbox_token()},
    )
