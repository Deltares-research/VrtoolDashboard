from dash import html, Output, Input, callback

from src.component_ids import TABS_SWITCH_VISUALIZATION_PROJECT_PAGE, CONTENT_TABS_PROJECT_PAGE_OUTPUT_ID
from src.layouts.layout_project_page.tabs_output.layout_output_tabs import layout_project_output_tab_one
from src.layouts.layout_traject_page.layout_main_page import (
    layout_tab_one,
    layout_tab_two,
    layout_tab_three,
    layout_tab_four,
    layout_tab_five,
    layout_tab_six,
)
from src.layouts.layout_traject_page.layout_radio_items import layout_radio_calc_type, layout_radio_result_type, \
    layout_radio_mechanism


@callback(

    Output(CONTENT_TABS_PROJECT_PAGE_OUTPUT_ID, "children"),

    [Input(TABS_SWITCH_VISUALIZATION_PROJECT_PAGE, "active_tab")],
)
def render_tab_map_content(active_tab: str) -> html.Div:
    """
    Renders the content of the selected tab for the general overview page.
    :param active_tab:
    :return:
    """

    if active_tab == "tab-1111":
        return layout_project_output_tab_one()

    elif active_tab == "tab-1112":
        return html.Div("Not implemented yet")

    else:
        return html.Div("Invalid tab selected")
