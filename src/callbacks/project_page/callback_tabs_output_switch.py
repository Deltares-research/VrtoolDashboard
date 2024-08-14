from dash import html, Output, Input, callback

from src.component_ids import TABS_SWITCH_VISUALIZATION_PROJECT_PAGE, CONTENT_TABS_PROJECT_PAGE_OUTPUT_ID, \
    PROJECT_COMPARISON_GRAPH_ID, STORED_PROJECT_DATA, SLIDER_YEAR_RELIABILITY_RESULTS_ID, \
    PROJECT_COMPARISON_GRAPH_TIME_ID
from src.layouts.layout_project_page.tabs_output.layout_output_tabs import layout_project_output_tab_one, \
    layout_project_output_tab_two, layout_project_output_tab_three
from src.plotly_graphs.pf_length_cost import plot_default_scatter_dummy
from src.plotly_graphs.project_page.pf_traject_comparison import plot_pf_project_comparison, plot_pf_time_project
from src.utils.utils import export_to_json


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

    elif active_tab == "tab-1112":
        return layout_project_output_tab_two()

    elif active_tab == "tab-1113":
        return layout_project_output_tab_three()

    else:
        return html.Div("Invalid tab selected")


@callback(
    Output(PROJECT_COMPARISON_GRAPH_ID, "figure"),
    [
        Input(STORED_PROJECT_DATA, "data"),
        Input(SLIDER_YEAR_RELIABILITY_RESULTS_ID, "value"),
    ],
)
def make_graph_pf_project_comparison(
        project_data: dict,
        selected_year: float,
):
    """

    """

    if project_data is None:
        return plot_default_scatter_dummy()
    else:
        _fig = plot_pf_project_comparison(project_data, selected_year)
    return _fig


@callback(
    Output(PROJECT_COMPARISON_GRAPH_TIME_ID, "figure"),
    [
        Input(STORED_PROJECT_DATA, "data"),
        Input("select_cost_beta_switch", "value")
    ],
)
def make_graph_pf_time_comparison(
        project_data: dict,
        switch_cost_beta: str,
):
    """

    """
    export_to_json(project_data, )
    if project_data is None:
        return plot_default_scatter_dummy()
    else:
        _fig = plot_pf_time_project(project_data, switch_cost_beta)
    return _fig
