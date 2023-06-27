import base64
import datetime
import io
from pathlib import Path

from dash import dash_table
import pandas as pd
import geopandas as gdf
from dash import html, dcc, Output, Input, State, dependencies
import plotly.graph_objects as go
from app import app
import dash_bootstrap_components as dbc

from components.navigation_bar import Navbar
from components.upload_dike_files import FileDikeUpload
from src.gws_convertor import GWSRDConvertor

card_style = dbc.Row(
    [
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Column 1"),
                    dbc.CardBody(
                        # Content for column 1
                        "Content for column 1 goes here"
                    ),
                ]
            ),
            md=6,
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Column 2"),
                    dbc.CardBody(

                        # Content for column 2
                        "Content for column 2 goes here"
                    ),
                ]
            ),
            md=6,
        ),
    ]
)

normal_style = dbc.Row(
    [
        dbc.Col(
            html.Div(
                [
                    html.H2("Instellingen"),
                    dcc.Markdown(
                        '''
                        Welcome to the dashboard page of Veiligheidrendement 🌊.
                        
                        You can start using the dashboard by uploading below a Geojson file of a dike:
                    
                        '''
                    ),
                    FileDikeUpload(),

                ]
            ),
            md=4,  # Specify the width of the column (6 out of 12 columns)
        ),
        dbc.Col(
            html.Div(
                [

                    dbc.Tabs(
                        [
                            dbc.Tab(label="Tab 1", tab_id="tab-1"),
                            dbc.Tab(label="Tab 2", tab_id="tab-2"),
                        ],
                        id="tabs",
                        active_tab="tab-1",  # Set the initial active tab
                    ),
                    html.Div(id="content_tab"),

                ]
            ),
            md=8,  # Specify the width of the column (6 out of 12 columns)
        ),
    ]
)
# Define the index page layout
app.layout = dbc.Container(
    id="app-container",
    children=
    [
        dcc.Location(id='url', pathname='welcome', refresh=False),
        Navbar(),

        # card_style,
        normal_style,

    ],
    fluid=True,
)


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))

        elif 'geojson' in filename:
            df = gdf.read_file(io.BytesIO(decoded))
            df["geometry"] = df["geometry"].apply(lambda x: list(x.coords))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        # dash_table.DataTable(
        #     data=df.to_dict('records'),
        #     columns=[{'name': i, 'id': i} for i in df.columns],
        #     page_size=15
        # ),
        dcc.Store(id='stored-data', data=df.to_dict('records')),

        html.Hr(),  # horizontal line
    ])


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
def make_graphs(data):
    fig = go.Figure()

    for dijkvak in data:
        # convert in GWS coordinates:
        linestring_rd = dijkvak['geometry']
        convertor = [GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in linestring_rd]

        if dijkvak["objectid"] in [0, 1, 2, 4, 7, 8, 30, 31, 33, 34, 35]:
            color = 'red'
        elif dijkvak["objectid"] in [5, 6, 9, 10, 11, 12, 13, 14, 21, 22]:
            color = 'orange'
        elif dijkvak["objectid"] in [15, 16, 17, 18, 19, 20]:
            color = 'green'
        else:
            color = 'blue'

        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lat=[x[0] for x in convertor],
            lon=[x[1] for x in convertor],
            marker={'size': 10, 'color': color},
            line={'width': 5, 'color': color},
            name='Traject 38-1',
            hovertemplate=f'Vaknaam {dijkvak["vaknaam"]}',
            showlegend=False, ))

        mapbox_access_token = open(Path(__file__).parent / "mapbox_token.txt").read()

        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(lat=convertor[0][0], lon=convertor[0][1]),
                zoom=11,
            ))
    return dcc.Graph(figure=fig, style={'width': '100%', 'height': '100%'})


@app.callback(
    Output("content_tab", "children"),
    [Input("tabs", "active_tab")]
)
def render_tab_content(active_tab):
    if active_tab == "tab-1":
        # return html.Div("Content for Tab 1")
        #
        return html.Div(id="content_tab",
                        children=[
                            html.H2("Overzicht Kaart"),
                            html.Div("The map below dsiplays basic information on the imported dike traject."),
                            html.Div(id='output-div',
                                     style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),

                        ]),

    elif active_tab == "tab-2":
        return html.Div("Content for Tab 2")
    else:
        return html.Div("Invalid tab selected")


# Run the app on localhost:8050
if __name__ == '__main__':
    app.run_server(debug=True)
