import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable
from dash.html import Br
import dash_ag_grid as dag

from src.component_ids import OVERVIEW_PROJECT_MAP_ID, EDITABLE_PROJECT_TABLE_ID, \
    TABS_SWITCH_VISUALIZATION_PROJECT_PAGE, CONTENT_TABS_PROJECT_PAGE_OUTPUT_ID

df_imported_run_table = pd.DataFrame(columns=["traject", "run_name", "active"], data=[])

columns_defs = [
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

    dag.AgGrid(
        id=EDITABLE_PROJECT_TABLE_ID,
        rowData=df_imported_run_table.to_dict('records'),
        columnDefs=columns_defs,
        defaultColDef={"resizable": True,
                       "wrapHeaderText": True,
                       "autoHeaderHeight": True, },
        dashGridOptions={"rowSelection": "multiple", "enableCellTextSelection": True, "ensureDomOrder": True},
        persistence=True,
        persistence_type="session",

    ),

]

right_side = [

    dbc.Tabs(
        [
            dbc.Tab(label="Map", tab_id="tab-1111"),
            dbc.Tab(label="Comparison", tab_id="tab-1112"),
            dbc.Tab(label="Time",    tab_id="tab-1113"),
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
