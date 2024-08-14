import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable
from dash.html import Br
import dash_ag_grid as dag

from src.component_ids import OVERVIEW_PROJECT_MAP_ID, EDITABLE_PROJECT_TABLE_ID

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
        persistence=True

    ),

]

right_side = [
    html.H2("Project overzicht"),
    html.Div(id=OVERVIEW_PROJECT_MAP_ID,
             style={'width': '100vh', 'height': '90vh', 'border': "2px solid black"}),
]

project_definition_tab_layout = html.Div([
    dbc.Row([
        dbc.Col(left_side, md=5),
        dbc.Col(right_side, md=7),
    ]),
])
