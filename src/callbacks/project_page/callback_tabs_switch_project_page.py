from dash import callback, Output, Input, html, State, dash

from src.component_ids import PROJECT_PAGE_VISUALIZATION_COST_GRAPH, PROJECT_PAGE_VISUALIZATION_RELIABILITY_GRAPH, STORED_IMPORTED_RUNS_DATA, STORED_PROJECT_OVERVIEW_DATA, \
    OVERVIEW_PROJECT_MAP_ID, PROJECT_OVERVIEW_TABLE_DISPLAY
from src.layouts.layout_project_page.layout_project_definition_tab import project_definition_tab_layout
from src.layouts.layout_project_page.layout_project_visualization_tab import project_visualization_tab_layout, \
    fill_project_display_overview_table
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


@callback(
    [Output(PROJECT_PAGE_VISUALIZATION_COST_GRAPH, "figure"),
     Output(PROJECT_PAGE_VISUALIZATION_RELIABILITY_GRAPH, "figure"),
     Output(OVERVIEW_PROJECT_MAP_ID, "figure"),
     Output(PROJECT_OVERVIEW_TABLE_DISPLAY, "children")],
    [Input("tabs_tab_project_page", "value"),
     State(STORED_IMPORTED_RUNS_DATA, "data"),
     State(STORED_PROJECT_OVERVIEW_DATA, "data")]
)
def update_project_page_visualization(tabs_switch, imported_runs_data: dict, project_overview_data: list):
    if tabs_switch == "tab-111" or tabs_switch == "tab-1":
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    if imported_runs_data is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    if project_overview_data is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    projects = get_projects_from_saved_data(imported_runs_data, project_overview_data)
    cost_fig = plot_cost_vs_time_projects(projects)
    reliability_fig = projects_reliability_over_time(projects, imported_runs_data)
    project_overview_table = fill_project_display_overview_table(projects)

    map_fig = plot_project_overview_map(projects)
    return cost_fig, reliability_fig, map_fig, project_overview_table

