from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc


from src.component_ids import DROPDOWN_SELECTION_RUN_ID, GREEDY_OPTIMIZATION_CRITERIA_BETA, \
    GREEDY_OPTIMIZATION_CRITERIA_YEAR, BUTTON_RECOMPUTE_GREEDY_STEPS, BUTTON_RECOMPUTE_GREEDY_STEPS_NB_CLICKS, \
    DIV_NUMBERFIELD_OPTIMIZATION_STOP_CRITERIA, DIV_BUTTON_RECOMPUTE_GREEDY_STEPS_ID, BUTTON_SAVE_RUN_AS_JSON, \
    RUN_SAVE_NAME_ID, DOWNLOAD_RUN_JSON_ID
from src.layouts.layout_traject_page.layout_radio_items import layout_radio_greedy_optimization_stop_criteria

layout_number_field_optimization_stop_criteria = html.Div(
    dbc.Row([
        dbc.Col(
            dcc.Input(id=GREEDY_OPTIMIZATION_CRITERIA_BETA, type='number', placeholder='beta',
                      style={'width': '100%'})),
        dbc.Col(
            dcc.Input(id=GREEDY_OPTIMIZATION_CRITERIA_YEAR, type='number', placeholder='jaar',
                      style={'width': '100%'})),

    ]),
    hidden=True,
    id=DIV_NUMBERFIELD_OPTIMIZATION_STOP_CRITERIA
)

layout_button_recompute_greedy_steps = html.Div(children=[
    dbc.Button(
        "Ververs resultaten", id=BUTTON_RECOMPUTE_GREEDY_STEPS, className="ml-auto"),
    dcc.Input(id=BUTTON_RECOMPUTE_GREEDY_STEPS_NB_CLICKS, value=0, type='hidden'), ],
    hidden=True,
    id=DIV_BUTTON_RECOMPUTE_GREEDY_STEPS_ID
)

layout_button_save_run_as_json = html.Div(
    children=[
        dmc.TextInput(placeholder="Bestandsnaam", id=RUN_SAVE_NAME_ID),
        dbc.Button("Opslaan", id=BUTTON_SAVE_RUN_AS_JSON, color="primary", className="mr-1"),
        dcc.Download(id=DOWNLOAD_RUN_JSON_ID),
    ]
)

layout_traject_select = html.Div([
    html.Div("Selecteer een database en hoe de resultaten moeten worden weergegeven"),
    dcc.Upload(
        id='upload-data-config-json',
        children=html.Div([
            '',
            html.A('Importeer een configuratiebestand (config.json)')
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
                placeholder='Selecteer een berekening',  # gray, default text shown when no option is selected
                style={'width': "100%"},

            ),
            # html.Div(id='dd-output_container'),

        ],
            md=5),

    ]),
    # add vertical space
    html.Br(),
    html.Hr(style={"border-top": "2px solid black"}),
    html.Div("Geef aan welke oplossing moet worden weergegeven"),
    dbc.Row([
        dbc.Col([layout_radio_greedy_optimization_stop_criteria], md=4),
        dbc.Col([layout_number_field_optimization_stop_criteria], md=4),
        dbc.Col([layout_button_recompute_greedy_steps], md=4)

    ]),
    html.Br(),  # add vertical space
    html.Hr(style={"border-top": "2px solid black"}),
    html.Div("Opslaan van de resultaten in JSON formaat"),
    dbc.Row([layout_button_save_run_as_json]),
    #insert bold line
])
