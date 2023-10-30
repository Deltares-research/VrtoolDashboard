from dash import html, dcc
import dash_bootstrap_components as dbc

layout_traject_select = html.Div([

    dcc.Upload(
        id='upload-data-config-json',
        children=html.Div([
            '',
            html.A('Selecteer een bestand config.json')
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
        accept='.json'
    ),
    html.Div(id="dummy_upload_id"),

    dbc.Toast(

        [html.P("Bestand succesvol geüpload!", className="mb-0")],
        id="upload-toast",
        header="Success",
        icon="success",
        duration=5000,  # Display duration in milliseconds
        dismissable=True,
        is_open=False,

    ),
    dbc.Row([

        # Column 1
        dbc.Col([
            dcc.Dropdown(
                id='my_dropdown',
                options=[
                    {'label': 'default run', 'value': 'run_1'},
                ],
                optionHeight=35,  # height/space between dropdown options
                value='default run',  # dropdown value selected automatically when page loads
                disabled=False,  # disable dropdown value selection
                multi=False,  # allow multiple dropdown values to be selected
                searchable=True,  # allow user-searching of dropdown values
                search_value='',  # remembers the value searched in dropdown
                clearable=True,  # allow user to removes the selected value
                style={'width': "100%"},
            ),
            # html.Div(id='dd-output_container'),

        ],
            md=5),

    ]),

])
