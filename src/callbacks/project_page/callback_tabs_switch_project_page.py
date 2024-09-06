from dash import callback, Output, Input, html, State, dash

from src.component_ids import PROJECT_PAGE_VISUALIZATION_COST_GRAPH, PROJECT_PAGE_VISUALIZATION_RELIABILITY_GRAPH, \
    TABS_SWITCH_VISUALIZATION_PROJECT_PAGE, STORED_IMPORTED_RUNS_DATA, STORED_PROJECT_OVERVIEW_DATA, \
    OVERVIEW_PROJECT_MAP_ID
from src.layouts.layout_project_page.layout_project_definition_tab import project_definition_tab_layout
from src.layouts.layout_project_page.layout_project_visualization_tab import project_visualization_tab_layout
from src.linear_objects.project import get_projects_from_saved_data
from src.plotly_graphs.project_page.plotly_maps import plot_cost_vs_time_projects, plot_project_overview_map
from src.plotly_graphs.project_page.plotly_plots import projects_reliability_over_time


@callback(
    [Output("content_tab_project_page", "children")],
    [Input("tabs_tab_project_page", "value")],
)
def render_tab_content(tab_switch):
    if tab_switch == "tab-111" or tab_switch == "tab-1":
        return [project_definition_tab_layout]
    if tab_switch == "tab-112" or tab_switch == "tab-2":
        return [project_visualization_tab_layout]
    return [html.Div("Not yet implemented")]
    # return html.Div(
    #     id="status-container",
    #     children=[
    #         # build_quick_stats_panel(),
    #         html.Div("Not yet implemented"),
    #         html.Div(
    #             id="graphs-container",
    #             # children=[build_top_panel(stopped_interval), build_chart_panel()],
    #             children=[html.Div("Not yet implemented"), html.Div("Not yet implemented")],
    #         ),
    #     ],
    # )


@callback(
    [Output(PROJECT_PAGE_VISUALIZATION_COST_GRAPH, "figure"),
    Output(PROJECT_PAGE_VISUALIZATION_RELIABILITY_GRAPH, "figure"),
     Output(OVERVIEW_PROJECT_MAP_ID, "figure")],
    [Input("tabs_tab_project_page", "value"),
    State(STORED_IMPORTED_RUNS_DATA, "data"),
    State(STORED_PROJECT_OVERVIEW_DATA, "data")]
)
def update_project_page_visualization(tabs_switch, imported_runs_data: dict, project_overview_data: list):
    if tabs_switch == "tab-111" or tabs_switch == "tab-1":
        return dash.no_update, dash.no_update, dash.no_update
    if imported_runs_data is None:
        return dash.no_update, dash.no_update, dash.no_update
    if project_overview_data is None:
        return dash.no_update, dash.no_update, dash.no_update

    projects = get_projects_from_saved_data(imported_runs_data, project_overview_data)
    cost_fig = plot_cost_vs_time_projects(projects)
    reliability_fig = projects_reliability_over_time(projects, imported_runs_data)

    map_fig = plot_project_overview_map(projects)
    return cost_fig, reliability_fig, map_fig



# map_overview_area = dcc.Graph(
#         id=OVERVIEW_PROJECT_MAP_ID,
#         figure=plot_default_overview_map_dummy(),
#         style={"width": "100%", "height": "100%"},
#         config={"mapboxAccessToken": get_mapbox_token()},
#     )