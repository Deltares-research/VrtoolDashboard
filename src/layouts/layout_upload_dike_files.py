from dash import html, dcc
import dash_bootstrap_components as dbc



layout_upload_button = html.Div([

        dcc.Upload(
            id='upload-data-zip',
            children=html.Div([
                'Drag and Drop een zip-bestand of ',
                html.A('Selecteer een bestand')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=False,
            accept='.zip'
        ),

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
