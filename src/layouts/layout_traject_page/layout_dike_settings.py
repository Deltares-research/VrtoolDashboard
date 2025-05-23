from dash import html
import dash_bootstrap_components as dbc

from src.layouts.layout_traject_page.layout_radio_items import layout_radio_result_type, layout_radio_calc_type, \
    layout_radio_mechanism
from src.layouts.layout_traject_page.layout_sliders import layout_year_slider

dike_settings_layout = html.Div([
    html.Div("Kies hier de instellingen voor de weergave van de resultaten."),
    layout_year_slider,

    dbc.Row([

        dbc.Col([layout_radio_result_type], md=4),

        dbc.Col([layout_radio_calc_type], md=5),

        dbc.Col([layout_radio_mechanism], md=3),

    ]),

])
