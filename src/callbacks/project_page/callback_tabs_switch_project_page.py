from dash import callback, Output, Input, html, State

from src.layouts.layout_project_page.layout_project_definition_tab import project_definition_tab_layout


@callback(
    [Output("content_tab_project_page", "children")],
    [Input("tabs_tab_project_page", "value")],
)
def render_tab_content(tab_switch):
    if tab_switch == "tab-111" or tab_switch == "tab-1":
        return [project_definition_tab_layout]
    if tab_switch == "tab-112" or tab_switch == "tab-2":
        return [html.Div("Not yet implemented")]
    return [html.Div("Not yet implemented")]
    # return html.Div(
    #     id="status-container",
    #     children=[
    #         # build_quick_stats_panel(),
    #         html.Div("Not yet implemented"),
    #         html.Div(
    #             id="graphs-container",
    #             # children=[build_top_panel(stopped_interval), build_chart_panel()],
    #             children=[html.Div("Not yet implemented"), html.Div("Not yet implemented")],
    #         ),
    #     ],
    # )
