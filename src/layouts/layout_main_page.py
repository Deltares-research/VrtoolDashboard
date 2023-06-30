from dash import html, dcc
import dash_bootstrap_components as dbc
from enum import Enum
from .layout_upload_dike_files import layout_upload_button


class ResultType(Enum):
    DOORSNEDE_EISEN = "Doorsnede-Eisen"
    VEILIGHEID_RENDEMENT = "Veiligheidsrendement"


def make_layout_main_page() -> dbc.Row:
    """
    Return the layout for the main page. It consists in a two columns layout:
    - The left column is for the settings
    - The right column is for the visualizations with 2 tabs:
        - Tab 1: Overview map
        - Tab 2: TBD
    """
    layout = dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        html.H2("Welcome to the dashboard of the Veiligheidrendement tool🌊"),
                        dcc.Markdown(
                            '''
                            This dashboard is a tool to visualize the results of the Veiligheidrendement optimization for dike projects.
    
                            You can start using the dashboard by uploading below a Geojson file of a dike:
    
                            '''
                        ),
                        layout_upload_button,

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
    return layout


def layout_tab_one() -> html.Div:
    return html.Div(id="content_tab",
                    children=[
                        html.H2("Overzicht Kaart"),
                        html.Div("The map below displays basic information about the imported dike traject."),
                        dbc.RadioItems(
                            id="select_result_type",
                            options=[
                                {"label": ResultType.DOORSNEDE_EISEN.value, "value": ResultType.DOORSNEDE_EISEN.name},
                                {"label": ResultType.VEILIGHEID_RENDEMENT.value,
                                 "value": ResultType.VEILIGHEID_RENDEMENT.name},
                            ],
                            value=ResultType.VEILIGHEID_RENDEMENT.name,
                            style={'width': '40vh', "height": "7vh", "margin": "20px"}
                        ),
                        html.Div(id='overview_map_div',
                                 style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),
                    ])
