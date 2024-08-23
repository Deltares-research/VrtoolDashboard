from dash import html, Output, Input, callback, State

from src.component_ids import (TABS_SWITCH_VISUALIZATION_PROJECT_PAGE, CONTENT_TABS_PROJECT_PAGE_OUTPUT_ID,
                               STORED_IMPORTED_RUNS_DATA, PROJECT_COMPARISON_GRAPH_TIME_VS_COST_ID,
                               STORED_PROJECT_OVERVIEW_DATA)
from src.layouts.layout_project_page.tabs_output.layout_output_tabs import layout_project_output_tab_one, \
    layout_project_output_tab_two
from src.linear_objects.project import DikeProject, get_projects_from_saved_data
from src.plotly_graphs.pf_length_cost import plot_default_scatter_dummy
from src.plotly_graphs.project_page.pf_traject_comparison import plot_cost_vs_time_projects


@callback(

    Output(CONTENT_TABS_PROJECT_PAGE_OUTPUT_ID, "children"),

    [Input(TABS_SWITCH_VISUALIZATION_PROJECT_PAGE, "active_tab")],
)
def render_project_overview_map_content(active_tab: str) -> html.Div:
    """
    Renders the content of the selected tab for the general overview page.
    :param active_tab:
    :return:
    """

    if active_tab == "tab-1111":
        return layout_project_output_tab_one()

    elif active_tab == "tab-1114":
        return layout_project_output_tab_two()

    else:
        return html.Div("Invalid tab selected")


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

    if imported_runs_data is None:
        return plot_default_scatter_dummy()

    if project_overview_data is None:
        return plot_default_scatter_dummy()


    else:
        projects = get_projects_from_saved_data(imported_runs_data, project_overview_data)

        _fig = plot_cost_vs_time_projects(projects)

    return _fig
