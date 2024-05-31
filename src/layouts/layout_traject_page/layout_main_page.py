from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable

from .layout_collasping_menus import make_collapsing_menu
from .layout_dike_settings import dike_settings_layout
from .layout_download_buttons import layout_download_overview, layout_download_assessment, \
    layout_download_reinforced_sections
from .layout_radio_items import layout_radio_color_bar_result_type, layout_radio_sub_type_result, \
    layout_radio_length_switch
from .layout_sliders import layout_urgency_length_slider
from src.layouts.layout_traject_page.layout_tabs.layout_tab_measures import layout_radio_dike_section_selection
from .layout_upload_dike_files import layout_traject_select
from src.component_ids import GRAPH_MEASURE_COMPARISON_ID
from src.constants import get_mapbox_token
from src.plotly_graphs.pf_length_cost import plot_default_scatter_dummy
from src.plotly_graphs.plotly_maps import plot_default_overview_map_dummy


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
                        html.H2("Welkom bij het dashboard van Versterkingsaanpak vanuit VR tool 🌊"),
                        dcc.Markdown(
                            '''
                            Dit dashboard kan worden gebruikt om de resultaten van veiligheidsrendementberekeningen te visualiseren, en deze te vertalen naar de scope van dijkversterkingsprojecten.
                            '''
                        ),

                        make_collapsing_menu(menu_name='Traject selectie',
                                             collapse_id=1,
                                             inner_layouts=[layout_traject_select]),

                        make_collapsing_menu(menu_name="Instellingen",
                                             collapse_id=2,
                                             inner_layouts=[dike_settings_layout]),

                        # make_collapsing_menu(menu_name="Maatregelen optimalisatie",
                        #                      collapse_id=3,
                        #                      # inner_layouts=[dike_vr_optimization_layout],
                        #                      inner_layouts=[dike_vr_optimization_layout_ag_grid],
                        #                      is_open=False),

                    ]
                ),
                md=4,  # Specify the width of the column (6 out of 12 columns),
                id="left-column",
            ),
            dbc.Col(
                html.Div(
                    [

                        dbc.Tabs(
                            [
                                dbc.Tab(label="Overzicht", tab_id="tab-1"),
                                dbc.Tab(label="Beoordelingsresultaten", tab_id="tab-2"),
                                dbc.Tab(label="Versterkingsmaatregelen", tab_id="tab-3"),
                                dbc.Tab(label="Resultaten optimalisatie", tab_id="tab-4"),
                                dbc.Tab(label="Prioriteringsinformatie", tab_id="tab-5"),
                                dbc.Tab(label="Maatregelen", tab_id="tab-6"),


                            ],
                            id="tabs",
                            active_tab="tab-1",  # Set the initial active tab
                        ),
                        html.Div(id="content_tab"),

                    ]
                ),
                md=8,  # Specify the width of the column (6 out of 12 columns),
                id="right-column",
            ),
        ]
    )
    return layout


def layout_tab_one() -> html.Div:
    return html.Div(
        children=[
            dbc.Row([
                dbc.Col([html.H2("Overzicht dijkvakken")], md=10),
                dbc.Col([layout_download_overview], md=2)
            ]),

            DataTable(id='table'),
            html.Div(
                "De onderstaande kaart geeft een overzicht van de dijkvakken binnen het geïmporteerde dijktraject."),
            html.Div(id='overview_map_div',
                     style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),

        ])


def layout_tab_two() -> html.Div:
    layout = html.Div(
        children=[
            dbc.Row([
                dbc.Col([html.H2("Beoordelingsresultaten")], md=10),
                dbc.Col([layout_download_assessment], md=2)
            ]),

            html.Div(
                "De onderstaande kaart toont de betrouwbaarheid/faalkans van de initiële beoordeling voor het gehele dijktraject. Gebruik de schuifregelaar om een ander beoordelingsjaar te visualiseren."),
            html.Div(id='dike_traject_reliability_map_initial',
                     style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),

        ]
    )

    return layout


def layout_tab_three() -> html.Div:
    layout = html.Div(
        children=[

            dbc.Row([
                dbc.Col([html.H2("Maatregelen")], md=10),
                dbc.Col([layout_download_reinforced_sections], md=2)
            ]),
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
                "Onderstaande figuur toont de relatie tussen de trajectfaalkans en de kosten of lengte van de versterking voor het geselecteerde referentiejaar."),

            dbc.Row([

                dbc.Col([layout_radio_length_switch], md=4),

            ]),

            html.Div(
                style={'width': '130vh', 'height': '60vh', 'border': "2px solid black"},
                children=[
                    dcc.Graph(id='dike_traject_pf_cost_graph', figure=plot_default_scatter_dummy(),
                              style={'width': '100%', 'height': '100%'},
                              config={'mapboxAccessToken': get_mapbox_token()}),
                    dcc.Store(id="store_clicked_section", data='all')
                ],

            ),
            html.Br(),
            html.Div(
                style={'width': '130vh', 'height': '30vh', 'border': "2px solid black"},
                children=[
                    dcc.Graph(id='dike_traject_pf_cost_helping_map', figure=plot_default_overview_map_dummy(),
                              style={'width': '100%', 'height': '100%'},
                              config={'mapboxAccessToken': get_mapbox_token()})
                ]),

        ]
    )

    return layout


def layout_tab_five() -> html.Div:
    layout = html.Div(
        children=[
            html.H2("Prioritering"),
            html.Div(
                "Onderstaande kaart geeft de meest urgente dijkvakken op basis van de optimalisatievolgorde."),
            layout_urgency_length_slider,
            html.Div(id='dike_traject_urgency_map',
                     style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),

        ]
    )

    return layout



def layout_tab_six() -> html.Div:
    layout = html.Div(
        children=[
            html.H2("Maatregelen"),
            html.Div("Selecteer een dijkvak om de resultaten van de maatregelen te bekijken:"),
            layout_radio_dike_section_selection,
            # html.Div(id=GRAPH_MEASURE_COMPARISON_ID,
            #          style={'width': '130vh', 'height': '90vh', 'border': "2px solid black"}),
            html.Div("U kunt op een maatregel bolletje kliken om de betrouwbaarheid van de maatregel over tijd te bekijken."),

            html.Div(
                style={'width': '130vh', 'height': '60vh', 'border': "2px solid black"},
                children=[
                    dcc.Graph(id=GRAPH_MEASURE_COMPARISON_ID, figure=plot_default_scatter_dummy(),
                              style={'width': '100%', 'height': '100%'},
                              ),
                ],

            ),

        ]
    )

    return layout
