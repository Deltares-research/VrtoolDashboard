from dash import html, dcc
import dash_bootstrap_components as dbc


table_header = [
    html.Thead(html.Tr([html.Th("Dijkvak"),
                        html.Th("Versterking"),
                        html.Th("Maatregel"),
                        html.Th("Jaar van uitvoering"),
                        ]))
]

row1 = html.Tr([html.Td("01A"), html.Td("Aan"), html.Td("Bermverbreding"), html.Td("2025")])
row2 = html.Tr([html.Td("01B"), html.Td("Uit"), html.Td("VZG"), html.Td("2025")])
row3 = html.Tr([html.Td("2"), html.Td("Aan"), html.Td("Stabiliteitsscherm"), html.Td("2035")])
row4 = html.Tr([html.Td("3"), html.Td("Aan"), html.Td("VZG"), html.Td("2035")])


table_body = [html.Tbody([row1, row2, row3, row4])]

dike_vr_optimization_layout = html.Div([

    dbc.Row([

        # Column 1
        dbc.Col([
            dcc.Dropdown(
                id='my_dropdown',
                options=[
                    {'label': 'Database 1', 'value': 'db_1'},
                    {'label': 'Database 2', 'value': 'db_2'},
                    {'label': 'Database 3 (sensitivity)', 'value': 'db_3'},

                ],
                optionHeight=35,  # height/space between dropdown options
                value='db_1',  # dropdown value selected automatically when page loads
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

        dbc.Col([ dcc.Upload(
            id='upload-data-zip2',
            children=html.Div([
                'Upload database',
                html.A('')
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
            ],
            md=7),



    ]),
    dbc.Table(table_header + table_body, bordered=True),
    html.Div(
    [dbc.Button("Optimize", id="button_optimize", color="primary", className="mr-1"),
     dbc.Tooltip("Click to call VRCore optimization routine via the new calculation constraints.", target="button_optimize")
     ])

])



