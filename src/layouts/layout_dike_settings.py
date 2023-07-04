from dash import html, dcc
import dash_bootstrap_components as dbc

from src.constants import ResultType, CalcType

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
               id="slider_year_initial_reliability_results",
               ),

    dbc.Row([

        dbc.Col([dbc.RadioItems(
            id="select_result_type_initial",
            options=[
                {"label": ResultType.RELIABILITY.value, "value": ResultType.RELIABILITY.name},
                {"label": ResultType.PROBABILITY.value, "value": ResultType.PROBABILITY.name
                 },
            ],
            value=ResultType.RELIABILITY.name,
            style={'width': '40vh', "height": "6vh", "margin-top": "2px"}
        ), ],
            md=6),

        dbc.Col([dbc.RadioItems(
            id="select_calculation_type",
            options=[
                {"label": CalcType.DOORSNEDE_EISEN.value, "value": CalcType.DOORSNEDE_EISEN.name},
                {"label": CalcType.VEILIGHEIDRENDEMENT.value,
                 "value": CalcType.VEILIGHEIDRENDEMENT.name},
            ],
            value=CalcType.VEILIGHEIDRENDEMENT.name,
            style={'width': '40vh', "height": "6vh", "margin-top": "2px"}
        ), ]
            , md=6),

    ], ),

])
