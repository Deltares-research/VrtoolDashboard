from dash import callback, Output, Input, html, dcc, State

from src.component_ids import STORED_IMPORTED_RUNS_DATA, OVERVIEW_PROJECT_MAP_ID, STORED_PROJECT_OVERVIEW_DATA, \
    PROJECT_COMPARISON_GRAPH_TIME_VS_COST_ID
from src.constants import get_mapbox_token
from src.linear_objects.project import get_projects_from_saved_data
from src.plotly_graphs.plotly_maps import plot_default_overview_map_dummy
from src.plotly_graphs.project_page.pf_traject_comparison import plot_default_scatter_dummy
from src.plotly_graphs.project_page.plotly_maps import plot_project_overview_map, plot_cost_vs_time_projects
from src.plotly_graphs.project_page.plotly_plots import projects_reliability_over_time
from src.utils.utils import export_to_json


@callback(Output(OVERVIEW_PROJECT_MAP_ID, "children"),
          [Input(STORED_IMPORTED_RUNS_DATA, "data"),
           State(STORED_PROJECT_OVERVIEW_DATA, "data"),
           Input("tabs_tab_project_page", "active_tab")])
def make_graph_overview_area_projects(imported_runs_data: dict, project_data: list[dict], dummy: str) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data: The data of the dike traject to be displayed.
    """
    export_to_json(project_data)
    if imported_runs_data is None or imported_runs_data == {}:
        _fig = plot_default_overview_map_dummy()

    if project_data is None:
        _fig = plot_default_overview_map_dummy()
    else:

        _projects = get_projects_from_saved_data(imported_runs_data, project_data)

        # 2. Call
        _fig = plot_project_overview_map(_projects)
    return dcc.Graph(
        figure=_fig,
        style={"width": "100%", "height": "100%"},
        config={"mapboxAccessToken": get_mapbox_token()},
    )


@callback(
    Output(PROJECT_COMPARISON_GRAPH_TIME_VS_COST_ID, "figure"),
    [
        Input("select_cost_beta_switch", "value"),
        State(STORED_IMPORTED_RUNS_DATA, "data"),
        State(STORED_PROJECT_OVERVIEW_DATA, "data"),

    ],
)
def make_graph_pf_time_vs_cost_project_comparison(
        switch_cost_beta: str, imported_runs_data: dict, project_overview_data: list
):
    """

    """
    export_to_json(project_overview_data)

    if imported_runs_data is None:
        return plot_default_scatter_dummy()

    if project_overview_data is None:
        return plot_default_scatter_dummy()


    else:
        projects = get_projects_from_saved_data(imported_runs_data, project_overview_data)

        if switch_cost_beta == "COST":
            _fig = plot_cost_vs_time_projects(projects)

        elif switch_cost_beta == "RELIABILITY":
            _fig = projects_reliability_over_time(projects, imported_runs_data)

        else:
            raise ValueError(f"Switch cost beta value {switch_cost_beta} not recognized")

    return _fig
