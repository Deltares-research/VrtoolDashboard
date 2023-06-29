
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc

from src.components.navigation_bar import Navbar
from src.components.layout_main_page import make_layout_main_page
from src.linear_objects.traject import DikeTraject
from src.plotly_graphs.plotly_maps import plot_overview_map_dummy
from src.app import app
from src.utils.importers import parse_contents, parse_zip_content

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

@app.callback([Output('output-data-upload-zip', 'children'),
               Output("upload-toast", "is_open")],
              [Input('upload-data-zip', 'contents')],
              [State('upload-data-zip', 'filename')])
def upload_and_save_traject_input(contents: str, filename: str) -> tuple:
    """This is the callback for the upload of the zip files of the traject data.

    :param contents: string content of the uploaded zip file. The zip should content at least:
        - a geojson file with the dike data
        - a csv file with the results of the Veiligheidrendement method.

    :param filename: name of the uploaded zip file.

    :return: Return a tuple with:
        - html.Div with the serialized dike traject data.
        - boolean indicating if the upload was successful.
    """
    if contents is not None:
        _dike_traject = DikeTraject.from_uploaded_zip(contents, filename)
        return html.Div(
            dcc.Store(id='stored-data', data=_dike_traject.serialize())), True

    else:
        return html.Div("No file has been uploaded yet"), False


@app.callback(Output('output-div', 'children'),
              Input('stored-data', 'data'))
def make_graph_overview_dike(dike_traject_data: dict) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data:

    """
    _dike_traject = DikeTraject.deserialize(dike_traject_data)
    _fig = plot_overview_map_dummy(_dike_traject)
    return dcc.Graph(figure=_fig, style={'width': '100%', 'height': '100%'})


@app.callback(
    Output("content_tab", "children"),
    [Input("tabs", "active_tab")]
)
def render_tab_map_content(active_tab: str) -> html.Div:
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
    print("============================= RERUN THE APP ====================================")
    app.run_server(debug=True)
