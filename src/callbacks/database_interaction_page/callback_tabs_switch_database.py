from dash import callback, Output, Input, html

from src.layouts.layout_database_interaction.layout_custom_measures_table import custom_measure_tab_layout
from src.layouts.layout_database_interaction.layout_vr_optimalization import dike_vr_optimization_layout_ag_grid


@callback(

    Output("content_tab_database_interaction", "children"),

    [Input("tabs_database_interaction", "active_tab")],
)
def render_tab_map_content(active_tab: str) -> html.Div:
    """
    Renders the content of the selected tab for the general overview page.
    :param active_tab:
    :return:
    """
    if active_tab == "tab-11":
        return dike_vr_optimization_layout_ag_grid

    if active_tab == "tab-12":
        return custom_measure_tab_layout

    else:
        return html.Div("Invalid tab selected")
