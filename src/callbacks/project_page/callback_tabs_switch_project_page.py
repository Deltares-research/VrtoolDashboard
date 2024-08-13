from dash import callback, Output, Input, html

from src.layouts.layout_project_page.layout_project_definition_tab import project_definition_tab_layout


@callback(

    Output("content_tab_project_page", "children"),

    [Input("tabs_tab_project_page", "active_tab")],
)
def render_tab_project_page(active_tab: str) -> html.Div:
    """
    Renders the content of the selected tab for the general overview page.
    :param active_tab:
    :return:
    """
    if active_tab == "tab-111":
        return project_definition_tab_layout

    if active_tab == "tab-112":
        return html.Div("Not yet implemented")

    else:
        return html.Div("Invalid tab selected")
