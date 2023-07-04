from dash import html, dcc
import dash_bootstrap_components as dbc

from .layout_collasping_menus import make_collapsing_menu
from .layout_dike_settings import dike_settings_layout
from .layout_upload_dike_files import layout_upload_button
from ..constants import CalcType, ResultType


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
                            '''
                        ),

                        make_collapsing_menu(menu_name='Download',
                                             collapse_id=1,
                                             inner_layouts=[layout_upload_button]),

                        make_collapsing_menu(menu_name="Instellingen",
                                             collapse_id=2,
                                             inner_layouts=[dike_settings_layout])

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
                                dbc.Tab(label="Tab 3", tab_id="tab-3")
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
    return html.Div(
        children=[
            html.H2("Overzicht Kaart"),
            html.Div("The map below displays basic information about the imported dike traject."),
            dbc.Label("Select a result type:"),
            dbc.RadioItems(
                id="select_calculation_type",
                options=[
                    {"label": CalcType.DOORSNEDE_EISEN.value, "value": CalcType.DOORSNEDE_EISEN.name},
                    {"label": CalcType.VEILIGHEIDRENDEMENT.value,
                     "value": CalcType.VEILIGHEIDRENDEMENT.name},
                ],
                value=CalcType.VEILIGHEIDRENDEMENT.name,
                style={'width': '40vh', "height": "6vh", "margin-top": "2px"}
            ),
            html.Div(id='overview_map_div',
                     style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),
        ])


def layout_tab_two() -> html.Div:
    layout = html.Div(
        children=[
            html.H2("Beoordelingsresultaten"),
            html.Div(
                "The map below shows the reliability of the initial assessment for the entire dike traject. Use the slider to visualize another assessment year."),
            dcc.Slider(2025, 2125, value=2025,
                       marks={
                           2025: {'label': '2025', },
                           2045: {'label': '2045'},
                           2075: {'label': '2075'},
                           2125: {'label': '2125'}
                       },
                       included=False,
                       tooltip={"placement": "bottom", "always_visible": True},
                       id="slider_year_initial_reliability_results",
                       ),
            dbc.RadioItems(
                id="select_result_type_initial",
                options=[
                    {"label": ResultType.RELIABILITY.value, "value": ResultType.RELIABILITY.name},
                    {"label": ResultType.PROBABILITY.value, "value": ResultType.PROBABILITY.name
                     },
                ],
                value=ResultType.RELIABILITY.name,
                style={'width': '40vh', "height": "6vh", "margin-top": "2px"}
            ),
            html.Div(id='dike_traject_reliability_map_initial',
                     style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),

        ]
    )

    return layout


def layout_tab_three() -> html.Div:
    layout = html.Div(
        children=[
            html.H2("Maatregelen"),
            html.Div(
                "The map below shows the reliability of the initial assessment for the entire dike traject. Use the slider to visualize anothex    r assessment year."),
            dcc.Slider(2025, 2125, value=2025,
                       marks={
                           2025: {'label': '2025'},
                           2045: {'label': '2045'},
                           2075: {'label': '2075'},
                           2125: {'label': '2125'}
                       },
                       included=False,
                       tooltip={"placement": "bottom", "always_visible": True},
                       id="slider_year_reliability_results_measures",
                       ),
            dbc.RadioItems(
                id="select_result_type_measures",
                options=[
                    {"label": ResultType.RELIABILITY.value, "value": ResultType.RELIABILITY.name},
                    {"label": ResultType.PROBABILITY.value, "value": ResultType.PROBABILITY.name},
                ],
                value=ResultType.RELIABILITY.name,
                style={'width': '40vh', "height": "8vh", "margin-top": "2px"}
            ),
            html.Div(id='dike_traject_reliability_map_measures',
                     style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),

        ]
    )

    return layout
