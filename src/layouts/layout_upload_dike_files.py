from dash import html, dcc
import dash_bootstrap_components as dbc

layout_traject_select = html.Div([
    dbc.Select(id='selection_traject_name', options=[{"label": "38-1", "value": "38-1"},
                                                     {"label": "38-1 dummy", "value": "38-1 bis"}]),

    dbc.Toast(

        [html.P("Bestand succesvol geüpload!", className="mb-0")],
        id="upload-toast",
        header="Success",
        icon="success",
        duration=5000,  # Display duration in milliseconds
        dismissable=True,
        is_open=False,

        ),
        html.Div('Signaleringswaarde:', style={'margin': '10px'}),
        dcc.Input(id='tempo_signaleringswaarde', type='text', placeholder="1/30000", name="tempo_signaalering_warde", value="1/30000"),
        html.Div('Ondergrens:', style={'margin': '10px'}),
        dcc.Input(id='tempo_ondergrens', type='text', placeholder="1/10000", value="1/10000"),

        html.Div(id='output-data-upload-zip'),
    ])
