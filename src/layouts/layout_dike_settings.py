from dash import html, dcc
import dash_bootstrap_components as dbc

from src.constants import ResultType

dike_settings_layout = html.Div([dcc.Slider(2025, 2125, value=2025,
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
                                 ])
