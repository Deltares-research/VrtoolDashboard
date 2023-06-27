from dash import html, dcc
import dash_bootstrap_components as dbc

from src.components.upload_dike_files import FileDikeUpload


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
    return layout