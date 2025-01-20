from dash import callback, Output, Input, html, State, dash

from src.component_ids import PROJECT_PAGE_VISUALIZATION_COST_GRAPH, PROJECT_PAGE_VISUALIZATION_RELIABILITY_GRAPH, \
    STORED_IMPORTED_RUNS_DATA, STORED_PROJECT_OVERVIEW_DATA, \
    OVERVIEW_PROJECT_MAP_ID, PROJECT_OVERVIEW_TABLE_DISPLAY, RADIO_PROJECT_PAGE_RESULT_TYPE, TOTAL_AREA_COST, TOTAL_AREA_RISK_TABLE
from src.layouts.layout_project_page.layout_project_definition_tab import project_definition_tab_layout
from src.layouts.layout_project_page.layout_project_visualization_tab import project_visualization_tab_layout, \
    fill_project_display_overview_table
from src.linear_objects.reinforcement_program import calc_area_stats_new, DikeProgram
from src.plotly_graphs.project_page.plotly_maps import plot_project_overview_map
from src.plotly_graphs.project_page.plotly_plots import projects_reliability_over_time, plot_cost_vs_time_projects


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
     Output(PROJECT_OVERVIEW_TABLE_DISPLAY, "children"),
     Output(TOTAL_AREA_COST, "children"),
     Output(TOTAL_AREA_RISK_TABLE, "rowData")
     ],
    [Input("tabs_tab_project_page", "value"),
     Input(RADIO_PROJECT_PAGE_RESULT_TYPE, "value"),
     State(STORED_IMPORTED_RUNS_DATA, "data"),
     State(STORED_PROJECT_OVERVIEW_DATA, "data")]
)
def update_project_page_visualization(tabs_switch, result_type: str, imported_runs_data: dict, project_overview_data: list):
    """
    This function updates the project page visualization based on the selected tab and result type.

    :param tabs_switch: str: the selected tab, this is trigger the callback when switching tab
    :param result_type: str: the selected result type between reliability, probability, and factor distance to norm
    :param imported_runs_data: dict: the imported runs data
    :param project_overview_data: list: the project overview data

    :return: tuple: the cost figure, the reliability figure, the map figure, and the project overview table
    """
    if tabs_switch == "tab-111" or tabs_switch == "tab-1":
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    if imported_runs_data is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    if project_overview_data is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    program = DikeProgram(imported_runs_data, project_overview_data)
    projects, trajects = program.projects, program.dike_trajects

    cost_fig = plot_cost_vs_time_projects(projects)
    reliability_fig = projects_reliability_over_time(program, result_type)
    project_overview_table = fill_project_display_overview_table(projects)

    map_fig = plot_project_overview_map(projects, trajects.values())


    risk_table = []

    cost, risk_metrics = calc_area_stats_new(program)
    for year in [2030, 2040, 2050, 2075]:
        risk_table.append({"year": year,
                           "current_risk": round(risk_metrics["current"][year] / 1e6,2),
                           "program_risk": round(risk_metrics["program"][year] /1e6, 2)
                           })
    return cost_fig, reliability_fig, map_fig, project_overview_table, f"{cost/1e6:.1f} M€", risk_table

