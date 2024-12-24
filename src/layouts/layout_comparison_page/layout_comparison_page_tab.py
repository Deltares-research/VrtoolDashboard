import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable
from dash.html import Br
import dash_ag_grid as dag
import dash_mantine_components as dmc

from src.component_ids import EDITABLE_COMPARISON_TABLE_ID, TABS_SWITCH_VISUALIZATION_COMPARISON_PAGE, \
    CONTENT_TABS_COMPARISON_PAGE_ID

df_imported_run_table = pd.DataFrame(columns=["traject", "run_name", "active"], data=[])

columns_defs_1 = [
    {"field": "traject",
     "headerName": "Traject",
     "editable": False,
     "initialWidth": 200},

    {"field": "run_name",
     "headerName": "Naam berekening",
     "editable": True,
     "initialWidth": 200},

    {"field": "active",
     "headerName": "Activeer",
     "cellRenderer": "DBC_Switch",
     "editable": True,
     "CellRendererParams": {"onColor": "success", "offColor": "danger"},
     "initialWidth": 200, }
]

table_imported_dike_data = dag.AgGrid(
    id=EDITABLE_COMPARISON_TABLE_ID,
    rowData=df_imported_run_table.to_dict('records'),
    columnDefs=columns_defs_1,
    defaultColDef={"resizable": True,
                   "wrapHeaderText": True,
                   "autoHeaderHeight": True, },
    dashGridOptions={"rowSelection": "multiple", "enableCellTextSelection": True, "ensureDomOrder": True},


    # persistence=True,
    # persistence_type="session",

)





left_side = [
    #add some explanation text
    dcc.Upload(
        id='upload-dike-data-comparison',
        children=html.Div([
            '',
            html.A('Selecteer een json-bestand van een traject')
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
            [table_imported_dike_data],
            title='Geimporteerde berekeningen',
        ),
    ]),

]

right_side = [

    dbc.Tabs(
        [
            dbc.Tab(label="Kaart", tab_id="tab-11111"),
            dbc.Tab(label="Resultaten optimalisatie", tab_id="tab-11112"),
            dbc.Tab(label="Faalkans in tijd", tab_id="tab-11113"),
            dbc.Tab(label="Maatregelen op kaart", tab_id="tab-11114"),
            dbc.Tab(label="Overzichtstabel maatregelen", tab_id="tab-11115"),
            dbc.Tab(label="Volgorde dijkvakken", tab_id="tab-11116"),
        ],
        id=TABS_SWITCH_VISUALIZATION_COMPARISON_PAGE,
        active_tab="tab-11111",  # Set the initial active tab
    ),
    html.Div(id=CONTENT_TABS_COMPARISON_PAGE_ID),

]

project_definition_tab_layout = html.Div([
    dbc.Row([
        dbc.Col(left_side, md=4),
        dbc.Col(right_side, md=8),
    ]),
])
