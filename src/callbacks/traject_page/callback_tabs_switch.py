from dash import html, Output, Input

from src.app import app
from src.layouts.layout_main_page import layout_tab_one, layout_tab_two, layout_tab_three, layout_tab_four, \
    layout_tab_five
from src.layouts.layout_radio_items import layout_radio_calc_type, layout_radio_result_type, layout_radio_mechanism


@app.callback(
    [Output("content_tab", "children"),
     Output("select_calculation_type", "options"),
     Output("select_result_type", "options"),
     Output("select_mechanism_type", "options")],
    [Input("tabs", "active_tab")]
)
def render_tab_map_content(active_tab: str) -> tuple[html.Div, list, list, list]:
    """
    Renders the content of the selected tab for the general overview page.
    :param active_tab:
    :return:
    """

    enabled_calc_type_options = layout_radio_calc_type.options
    enabled_result_type_options = layout_radio_result_type.options
    enabled_mechanism_options = layout_radio_mechanism.options
    disabled_calc_type_options = disable_all_radio_options(enabled_calc_type_options)
    disabled_result_type_options = disable_all_radio_options(enabled_result_type_options)
    disabled_mechanism_options = disable_all_radio_options(enabled_mechanism_options)

    if active_tab == "tab-1":
        return layout_tab_one(), disabled_calc_type_options, disabled_result_type_options, disabled_mechanism_options
    elif active_tab == "tab-2":
        return layout_tab_two(), disabled_calc_type_options, enabled_result_type_options, enabled_mechanism_options
    elif active_tab == "tab-3":
        return layout_tab_three(), enabled_calc_type_options, enabled_result_type_options, enabled_mechanism_options
    elif active_tab == "tab-4":
        return layout_tab_four(), disabled_calc_type_options, enabled_result_type_options, disabled_mechanism_options
    elif active_tab == "tab-5":
        return layout_tab_five(), enabled_calc_type_options, enabled_result_type_options, disabled_mechanism_options

    else:
        return html.Div("Invalid tab selected"), [], [], []


def disable_all_radio_options(enabled_options: list) -> list:
    """Turn off the all options of a Radio option list"""
    return [{'label': option['label'], 'value': option['value'], 'disabled': True} for option in
            enabled_options]
