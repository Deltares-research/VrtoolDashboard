from dash import html, dcc
import dash_bootstrap_components as dbc

from .layout_collasping_menus import make_collapsing_menu
from .layout_dike_settings import dike_settings_layout
from .layout_radio_items import layout_radio_color_bar_result_type, layout_radio_sub_type_result, \
    layout_radio_length_switch
from .layout_sliders import layout_urgency_length_slider
from .layout_upload_dike_files import layout_upload_button
from .layout_vr_optimalization import dike_vr_optimization_layout


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
                        html.H2("Welkom bij het dashboard van de Veiligheidsrendementstool 🌊"),
                        dcc.Markdown(
                            '''
                            Dit dashboard is een tool om de resultaten van de optimalisatie van Veiligheidsrendement voor dijkprojecten te visualiseren.
                            '''
                        ),

                        make_collapsing_menu(menu_name='Download',
                                             collapse_id=1,
                                             inner_layouts=[layout_upload_button]),

                        make_collapsing_menu(menu_name="Instellingen",
                                             collapse_id=2,
                                             inner_layouts=[dike_settings_layout]),

                        make_collapsing_menu(menu_name="VR optimalisatie",
                                             collapse_id=3,
                                             inner_layouts=[dike_vr_optimization_layout],
                                             is_open=False),

                    ]
                ),
                md=4,  # Specify the width of the column (6 out of 12 columns)
            ),
            dbc.Col(
                html.Div(
                    [

                        dbc.Tabs(
                            [
                                dbc.Tab(label="TEST", tab_id="tab-6"),
                                dbc.Tab(label="Overzicht", tab_id="tab-1"),
                                dbc.Tab(label="Beoordelingsresultaten Kaart", tab_id="tab-2"),
                                dbc.Tab(label="Verstreking Kaart", tab_id="tab-3"),
                                dbc.Tab(label="Optimalisatie resultaten", tab_id="tab-4"),
                                dbc.Tab(label="Prioritering Kaart", tab_id="tab-5"),

                            ],
                            id="tabs",
                            active_tab="tab-6",  # Set the initial active tab
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
            html.Div("De onderstaande kaart geeft basisinformatie weer over het geïmporteerde dijktraject."),
            html.Div(id='overview_map_div',
                     style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),
        ])


def layout_tab_two() -> html.Div:
    layout = html.Div(
        children=[
            html.H2("Beoordelingsresultaten"),
            html.Div(
                "De onderstaande kaart toont de betrouwbaarheid van de initiële beoordeling voor het gehele dijktraject. Gebruik de schuifregelaar om een andere beoordelingsjaar te visualiseren."),
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
                " "),

            dbc.Row([

                dbc.Col([layout_radio_color_bar_result_type], md=4),
                dbc.Col([layout_radio_sub_type_result], md=4),

            ]),

            html.Div(id='dike_traject_reliability_map_measures',
                     style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),

        ]
    )

    return layout


def layout_tab_four() -> html.Div:
    layout = html.Div(
        children=[
            html.H2("Optimalisatie"),
            html.Div(
                "De figuur laat zien de relatie tussen de trajectfaalkans en de kosten van de versterking voor de geselecteerd referentie jaar."),

            dbc.Row([

                dbc.Col([layout_radio_length_switch], md=4),

            ]),

            html.Div(id='dike_traject_pf_cost_graph',
                     style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),

        ]
    )

    return layout


def layout_tab_five() -> html.Div:
    layout = html.Div(
        children=[
            html.H2("Prioritering"),
            html.Div(
                "Kies hoeveel cumulatieve lengte van de dijk de hoogste prioriteit heeft:"),
            layout_urgency_length_slider,
            html.Div(id='dike_traject_urgency_map',
                     style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),

        ]
    )

    return layout


def layout_test():
    layout = html.Div(
        children=[
            html.H2("Test"),
            html.Div(id="test_figure_1", style={'width': '130vh', 'height': '30vh', 'border': "2px solid black"}),
            html.Div(id="test_figure_2", style={'width': '130vh', 'height': '30vh', 'border': "2px solid black"}),
        ])

    return layout
