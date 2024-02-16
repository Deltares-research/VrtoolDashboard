from dash import html, dcc
import dash_bootstrap_components as dbc

from src.component_ids import DROPDOWN_SELECTION_RUN_ID, GREEDY_OPTIMIZATION_CRITERIA_BETA, \
    GREEDY_OPTIMIZATION_CRITERIA_YEAR, BUTTON_RECOMPUTE_GREEDY_STEPS
from src.layouts.layout_radio_items import layout_radio_greedy_optimization_stop_criteria

layout_number_field_optimization_stop_criteria = html.Div(
    dbc.Row([
        dbc.Col(
            dcc.Input(id=GREEDY_OPTIMIZATION_CRITERIA_BETA, type='number', placeholder='beta',
                      style={'width': '100%'})),
        dbc.Col(
            dcc.Input(id=GREEDY_OPTIMIZATION_CRITERIA_YEAR, type='number', placeholder='jaar',
                      style={'width': '100%'})),

    ]), )

layout_button_recompute_greedy_steps = html.Div(
    dbc.Button(
        "Recompute", id=BUTTON_RECOMPUTE_GREEDY_STEPS, className="ml-auto")
)


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
                id=DROPDOWN_SELECTION_RUN_ID,
                options=[
                    {'label': 'Basisberekening', 'value': 'Basisberekening'},
                ],
                optionHeight=35,  # height/space between dropdown options
                value='Basisberekening',  # dropdown value selected automatically when page loads
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
    # add vertical space
    html.Br(),
    dbc.Row([
        dbc.Col([layout_radio_greedy_optimization_stop_criteria], md=4),
        dbc.Col([layout_number_field_optimization_stop_criteria], md=4),
        dbc.Col([layout_button_recompute_greedy_steps], md=4)

    ])

])
