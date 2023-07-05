from dash import html, dcc
import dash_bootstrap_components as dbc

from .layout_collasping_menus import make_collapsing_menu
from .layout_dike_settings import dike_settings_layout
from .layout_upload_dike_files import layout_upload_button
from ..constants import CalcType, ResultType, ColorBarResultType


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
                        html.H2("Welkom bij het dashboard van de Veiligheidsrendementstool🌊"),
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
            html.Div(id='overview_map_div',
                     style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),
        ])


def layout_tab_two() -> html.Div:
    layout = html.Div(
        children=[
            html.H2("Beoordelingsresultaten"),
            html.Div(
                "The map below shows the reliability of the initial assessment for the entire dike traject. Use the slider to visualize another assessment year."),
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
                "The map below shows the reliability of the initial assessment for the entire dike traject. Use the slider  assessment year."),
            dcc.RadioItems(
                id="select_measure_map_result_type",
                options=[
                    {"label": ColorBarResultType.RELIABILITY.value, "value": ColorBarResultType.RELIABILITY.name},
                    {"label": ColorBarResultType.COST.value, "value": ColorBarResultType.COST.name},
                    {"label": ColorBarResultType.MEASURE.value, "value": ColorBarResultType.MEASURE.name},
                ],
                value=ColorBarResultType.RELIABILITY.name,
                inline=True,
                className='my-radio-items',  # add a class name
                style={'width': '40vh', "height": "6vh", "margin-top": "2px"}

            ),
            html.Div(id='dike_traject_reliability_map_measures',
                     style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),

        ]
    )

    return layout
