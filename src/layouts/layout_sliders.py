from dash import dcc

layout_year_slider = dcc.Slider(2025, 2125, value=2025,
                                marks={
                                    2025: {'label': '2025'},
                                    2045: {'label': '2045'},
                                    2075: {'label': '2075'},
                                    2125: {'label': '2125'}
                                },
                                included=False,
                                tooltip={"placement": "bottom", "always_visible": True},
                                id="slider_year_reliability_results",
                                )

layout_urgency_length_slider = dcc.Slider(0, 15, value=0,
                                          marks={
                                              0: {'label': '0 km'},
                                              5: {'label': '5 km'},
                                              10: {'label': '10 km'},
                                              15: {'label': '15 km'}
                                          },
                                          included=False,
                                          tooltip={"placement": "bottom", "always_visible": True},
                                          id="slider_urgency_length",
                                          )
