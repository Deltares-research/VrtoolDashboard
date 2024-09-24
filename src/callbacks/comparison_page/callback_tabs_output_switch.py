from dash import html, Output, Input, callback, State, dcc

from src.component_ids import TABS_SWITCH_VISUALIZATION_COMPARISON_PAGE, CONTENT_TABS_COMPARISON_PAGE_ID, \
    STORED_RUNS_COMPARISONS_DATA, RUNS_COMPARISON_GRAPH_TIME_ID, \
    SLIDER_YEAR_RELIABILITY_RESULTS_ID, OVERVIEW_COMPARISON_MAP_ID, RUNS_COMPARISON_GRAPH_ID
from src.layouts.layout_comparison_page.layout_output_tabs import layout_project_output_tab_one, \
    layout_project_output_tab_two, layout_project_output_tab_three

from src.plotly_graphs.pf_length_cost import plot_default_scatter_dummy
from src.plotly_graphs.plotly_maps import plot_default_overview_map_dummy
from src.plotly_graphs.project_page.pf_traject_comparison import plot_pf_project_comparison, \
    plot_pf_time_runs_comparison
from src.plotly_graphs.project_page.plotly_maps import plot_comparison_runs_overview_map


@callback(

    Output(CONTENT_TABS_COMPARISON_PAGE_ID, "children"),

    [Input(TABS_SWITCH_VISUALIZATION_COMPARISON_PAGE, "active_tab")],
)
def render_project_overview_map_content(active_tab: str) -> html.Div:
    """
    Renders the content of the selected tab for the general overview page.
    :param active_tab:
    :return:
    """

    if active_tab == "tab-11111":
        return layout_project_output_tab_one()

    elif active_tab == "tab-11112":
        return layout_project_output_tab_two()

    elif active_tab == "tab-11113":
        return layout_project_output_tab_three()

    else:
        return html.Div("Invalid tab selected")


@callback(Output(OVERVIEW_COMPARISON_MAP_ID, "children"),
          [Input(STORED_RUNS_COMPARISONS_DATA, "data"),
           # Input("tabs_tab_project_page", "active_tab")
           ])
def make_graph_overview_project(imported_runs_data: dict, project_data: list[dict]) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data: The data of the dike traject to be displayed.
    """
    if imported_runs_data is None or imported_runs_data == {}:
        _fig = plot_default_overview_map_dummy()
    else:
        _fig = plot_comparison_runs_overview_map(imported_runs_data)
    return dcc.Graph(
        figure=_fig,
        style={"width": "100%", "height": "100%"},
    )


@callback(
    Output(RUNS_COMPARISON_GRAPH_ID, "figure"),
    [
        Input(STORED_RUNS_COMPARISONS_DATA, "data"),
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
    Output(RUNS_COMPARISON_GRAPH_TIME_ID, "figure"),
    [
        Input(STORED_RUNS_COMPARISONS_DATA, "data"),
        Input("select_cost_beta_switch", "value")
    ],
)
def make_graph_pf_time_comparison(
        project_data: dict,
        switch_cost_beta: str,
):
    """

    """
    if project_data is None:
        return plot_default_scatter_dummy()
    else:
        _fig = plot_pf_time_runs_comparison(project_data, switch_cost_beta)
    return _fig
