import json

from dash import html, Output, Input, callback, State, dcc, no_update

from src.component_ids import TABS_SWITCH_VISUALIZATION_COMPARISON_PAGE, CONTENT_TABS_COMPARISON_PAGE_ID, \
    STORED_RUNS_COMPARISONS_DATA, RUNS_COMPARISON_GRAPH_TIME_ID, \
    SLIDER_YEAR_RELIABILITY_RESULTS_ID, OVERVIEW_COMPARISON_MAP_ID, RUNS_COMPARISON_GRAPH_ID, \
    EXPORT_PROJECTS_TO_JSON_ID, BUTTON_DOWNLOAD_PROJECTS_EXPORT_NB_CLICKS, BUTTON_DOWNLOAD_PROJECTS_EXPORT, \
    STORED_PROJECT_OVERVIEW_DATA, STORED_IMPORTED_RUNS_DATA
from src.constants import get_mapbox_token
from src.layouts.layout_comparison_page.layout_output_tabs import layout_project_output_tab_one, \
    layout_project_output_tab_two, layout_project_output_tab_three

from src.plotly_graphs.pf_length_cost import plot_default_scatter_dummy
from src.plotly_graphs.plotly_maps import plot_default_overview_map_dummy
from src.plotly_graphs.project_page.pf_traject_comparison import plot_pf_project_comparison, \
    plot_pf_time_runs_comparison
from src.plotly_graphs.project_page.plotly_maps import plot_comparison_runs_overview_map


@callback(
    [Output(EXPORT_PROJECTS_TO_JSON_ID, 'data'),
     Output(BUTTON_DOWNLOAD_PROJECTS_EXPORT_NB_CLICKS, "value")],
    [
        Input(BUTTON_DOWNLOAD_PROJECTS_EXPORT, 'n_clicks'),
        Input(BUTTON_DOWNLOAD_PROJECTS_EXPORT_NB_CLICKS, 'value'),
        State(STORED_PROJECT_OVERVIEW_DATA, "data"),
        State(STORED_IMPORTED_RUNS_DATA, "data"), ]
)
def download_reinforced_sections_geojson(n_clicks: int, store_n_click_button: int, imported_runs_data: dict,
                                         project_data: list[dict]) -> tuple[dict, int]:
    """
    Trigger the button to download and save the projects data into a json file so that it can reused later on.

    :return:
    """

    if imported_runs_data is None or project_data is None or n_clicks == 0 or n_clicks is None:
        return no_update, no_update

    if n_clicks is None or store_n_click_button == n_clicks:  # update when clicking on button ONLY
        return no_update, no_update


    else:
        _content = dict(imported_runs_data=imported_runs_data,
                        project_data=project_data)
        _content_json = json.dumps(_content)

        return dict(content=_content_json,
                    filename=f"projects_{store_n_click_button}.json"), n_clicks
