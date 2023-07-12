from dash import html, dcc
import dash_bootstrap_components as dbc

from src.layouts.layout_radio_items import layout_radio_result_type, layout_radio_calc_type, layout_radio_mechanism

dike_settings_layout = html.Div([
    dcc.Slider(2025, 2125, value=2025,
               marks={
                   2025: {'label': '2025'},
                   2045: {'label': '2045'},
                   2075: {'label': '2075'},
                   2125: {'label': '2125'}
               },
               included=False,
               tooltip={"placement": "bottom", "always_visible": True},
               id="slider_year_reliability_results",
               ),

    dbc.Row([

        dbc.Col([layout_radio_result_type], md=4),

        dbc.Col([layout_radio_calc_type], md=5),

        dbc.Col([layout_radio_mechanism], md=3),

    ]),

])
