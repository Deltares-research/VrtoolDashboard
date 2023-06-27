from dash import html, dcc, Output, Input, State
from app import app
import dash_bootstrap_components as dbc

from components.navigation_bar import Navbar
from src.components.layout_main_page import make_layout_main_page
from src.plotly_graphs.plotly_maps import plot_overview_map_dummy
from src.utils.importers import parse_contents

# Define the app layout
app.layout = dbc.Container(
    id="app-container",
    children=
    [
        dcc.Location(id='url', pathname='welcome', refresh=False),
        Navbar(),
        make_layout_main_page(),
    ],
    fluid=True,
)

# Define the callbacks
@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents: list, list_of_names: list[str], list_of_dates: list[str]) -> list[html.Div]:
    """Returns the uploaded file in a table"""
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(Output('output-div', 'children'),
              Input('stored-data', 'data'))
def make_graph_overview_dike(data: list[dict]) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param data: list of dictionaries containing the dike data. Each element of the list is a different dijkvak.

    """
    fig = plot_overview_map_dummy(data)
    return dcc.Graph(figure=fig, style={'width': '100%', 'height': '100%'})


@app.callback(
    Output("content_tab", "children"),
    [Input("tabs", "active_tab")]
)
def render_tab_content(active_tab: str) -> html.Div:
    """
    Renders the content of the selected tab for the general overview page.
    :param active_tab:
    :return:
    """
    if active_tab == "tab-1":
        return html.Div(id="content_tab",
                        children=[
                            html.H2("Overzicht Kaart"),
                            html.Div("The map below displays basic information about the imported dike traject."),
                            html.Div(id='output-div',
                                     style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),

                        ])
    elif active_tab == "tab-2":
        return html.Div("Content for Tab 2")
    else:
        return html.Div("Invalid tab selected")


# Run the app on localhost:8050
if __name__ == '__main__':
    app.run_server(debug=True)
