from dash import html, Output, Input, callback

from src.component_ids import (TABS_SWITCH_VISUALIZATION_PROJECT_PAGE, CONTENT_TABS_PROJECT_PAGE_OUTPUT_ID)
from src.layouts.layout_project_page.tabs_output.layout_output_tabs import layout_project_output_tab_one, \
    layout_project_output_tab_two



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



