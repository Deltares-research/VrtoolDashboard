import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable
from dash.html import Br
import dash_ag_grid as dag
import dash_mantine_components as dmc

from src.component_ids import OVERVIEW_PROJECT_MAP_ID, EDITABLE_PROJECT_TABLE_ID, \
    TABS_SWITCH_VISUALIZATION_PROJECT_PAGE, CONTENT_TABS_PROJECT_PAGE_OUTPUT_ID, TABLE_PROJECT_SUMMARY_ID, \
    MULTI_SELECT_SECTION_FOR_PROJECT_ID, ADD_PROJECT_BUTTON_ID, PROJECT_NAME_INPUT_FIELD_ID, ALERT_PROJECT_CREATION_ID

df_imported_run_table = pd.DataFrame(columns=["traject", "run_name", "active"], data=[])
df_project_summary_table = pd.DataFrame(columns=["project", "section_number", "year", "length"], data=[])

columns_defs_1 = [
    {"field": "traject",
     "headerName": "Traject",
     "editable": False,
     "initialWidth": 200},

    {"field": "run_name",
     "headerName": "Run naam",
     "editable": False,
     "initialWidth": 200},

    {"field": "active",
     "headerName": "Aktieveer",
     "cellRenderer": "DBC_Switch",
     "editable": True,
     "CellRendererParams": {"onColor": "success", "offColor": "danger"},
     "initialWidth": 200, }
]

columns_defs_2 = [
    {"field": "project",
     "headerName": "Project",
     "editable": False,
     "initialWidth": 100},

    {"field": "section_number",
     "headerName": "Dijkvakken",
     "editable": False,
     "initialWidth": 150},

    {"field": "year",
     "headerName": "Jaar",
     "editable": False,
     "initialWidth": 100},

    {"field": "length",
     "headerName": "Lengte (km)",
     "editable": False,
     "initialWidth": 150},

]

table_importe_dike_data = dag.AgGrid(
    id=EDITABLE_PROJECT_TABLE_ID,
    rowData=df_imported_run_table.to_dict('records'),
    columnDefs=columns_defs_1,
    defaultColDef={"resizable": True,
                   "wrapHeaderText": True,
                   "autoHeaderHeight": True, },
    dashGridOptions={"rowSelection": "multiple", "enableCellTextSelection": True, "ensureDomOrder": True},
    persistence=True,
    persistence_type="session",

)

table_project_summary = dag.AgGrid(
    id=TABLE_PROJECT_SUMMARY_ID,
    rowData=df_project_summary_table.to_dict('records'),
    columnDefs=columns_defs_2,
    defaultColDef={"resizable": True,
                   "wrapHeaderText": True,
                   "autoHeaderHeight": True, },
    dashGridOptions={"rowSelection": "multiple", "enableCellTextSelection": True, "ensureDomOrder": True},
    persistence=True,
    persistence_type="session",
)

multi_select = dmc.MultiSelect(
    label="Selecteer dijkvakken",
    placeholder="Select all you like!",
    id=MULTI_SELECT_SECTION_FOR_PROJECT_ID,
    value=[],
    data=[
    ],
    w=400,
    mb=10,
    clearable=True,
)

left_side = [

    dcc.Upload(
        id='upload-dike-data',
        children=html.Div([
            '',
            html.A('Selecteer een bestand dike_data.json')
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
    Br(),
    dbc.Accordion([
        dbc.AccordionItem(
            [table_importe_dike_data],
            title='Geimporteerde runs',
        ),
        dbc.AccordionItem(
            [
                dmc.Group([
                    dmc.TextInput(label="Project naam", id=PROJECT_NAME_INPUT_FIELD_ID),
                    multi_select,
                    dbc.Alert(children="", id=ALERT_PROJECT_CREATION_ID, color="danger", is_open=False, dismissable=True),
                    dmc.Button("Maak project aan", id=ADD_PROJECT_BUTTON_ID),
                    dmc.Button("Update project", id="update_project_button"),

                ]),

                table_project_summary
            ],
            title='Projects overview')
    ]),

]

right_side = [

    dbc.Tabs(
        [
            dbc.Tab(label="Map", tab_id="tab-1111"),
            dbc.Tab(label="Comparison", tab_id="tab-1112"),
            dbc.Tab(label="Time", tab_id="tab-1113"),
        ],
        id=TABS_SWITCH_VISUALIZATION_PROJECT_PAGE,
        active_tab="tab-1111",  # Set the initial active tab
    ),
    html.Div(id=CONTENT_TABS_PROJECT_PAGE_OUTPUT_ID),

]

project_definition_tab_layout = html.Div([
    dbc.Row([
        dbc.Col(left_side, md=5),
        dbc.Col(right_side, md=7),
    ]),
])
