from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable


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

    ]),
    DataTable(id='editable_traject_table',
              columns=(
                  [{'id': 'section_col', 'name': 'Dijkvak'},
                   {'id': 'reinforcement_col', 'name': 'Versterking', 'presentation': 'dropdown'},
                   {'id': 'measure_col', 'name': 'Maatregel', 'presentation': 'dropdown'},
                   {'id': 'reference_year_col', 'name': 'Referentiejaar'},
                   ]
              ),
              data=[],
              dropdown={
                  'reinforcement_col': {
                      'options': [{'label': 'Aan', 'value': "yes"}, {'label': 'Uit', 'value': "no"}]},
                  'measure_col': {
                      'options': [{'label': meas.value, 'value': meas.name} for meas in Measures]},
              },
              style_cell={'textAlign': 'left'},
              editable=True,
              # fixed_rows={'headers': True},  # either fix row with risk of overlap or have a slider
              style_table={'overflowX': 'scroll',
                           'overflowY': 'scroll'},

              ),

    html.Div(
        [dbc.Button("Optimize", id="button_optimize", color="primary", className="mr-1"),
         dbc.Tooltip("Click to call VRCore optimization routine via the new calculation constraints.",
                     target="button_optimize")
         ])

])
