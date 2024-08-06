import pandas as pd
from dash import html, dcc
import dash_ag_grid as dag
import dash_bootstrap_components as dbc

from src.component_ids import EDITABLE_CUSTOM_MEASURE_TABLE_ID, ADD_CUSTOM_MEASURE_BUTTON_ID, \
    REMOVE_CUSTOM_MEASURE_BUTTON_ID
from src.constants import Mechanism

columns_defs = [
    {"field": "measure_name",
     "headerName": "Maatregel naam",
     "editable": True,
     "initialWidth": 180},

    # {"field": "section_name",
    #  "headerName": "Sectie",
    #  "editable": True,
    #  "initialWidth": 100, },
    {"field": "section_name",
     "headerName": "Sectie",
     "editable": True,
     'cellEditor': 'agSelectCellEditor',
     'cellEditorParams': {
         'values': [],
     },
     "initialWidth": 140, },

    {"field": "mechanism",
     "headerName": "Mechanism",
     "editable": True,
     'cellEditor': 'agSelectCellEditor',
     'cellEditorParams': {
         'values': [mecha.value for mecha in Mechanism if mecha != Mechanism.SECTION],
     },
     "initialWidth": 140, },

    {"field": "time",
     "headerName": "Tijd",
     "editable": True,
     "initialWidth": 100, },

    {"field": "cost",
     "headerName": "Kost (€)",
     "editable": True,
     "initialWidth": 140, },

    {"field": "beta",
     "headerName": "Beta",
     "editable": True,
     "initialWidth": 100, },

]
df = pd.DataFrame(columns=[col["field"] for col in columns_defs],
                  data=[
                      # ["Rock", "7", "Piping", 0, 2000, 3.5]
                  ]
                  )  # empty dataframe

left_side = html.Div([
    # add text
    dcc.Markdown(
        '''
        Met de onderstaande tabel, kunt u custom maatregelen aan de database toevoegen.

        Geef een naam voor de optimizatie run en klik op de knop "Custom maatregel toevoegen" om de optimalisatie te starten.
        '''
    ),
    dbc.Row([
        dbc.Col([html.Button("Add Row", id="add-row-button")], md=1),
        dbc.Col([html.Button("Copy Row", id="copy-row-button")], md=1),
        dbc.Col([html.Button("Del Row", id="delete-row-button")]),
    ]),

    dag.AgGrid(
        id=EDITABLE_CUSTOM_MEASURE_TABLE_ID,
        rowData=df.to_dict('records'),
        columnDefs=columns_defs,
        defaultColDef={"resizable": True,
                       "wrapHeaderText": True,
                       "autoHeaderHeight": True, },
        dashGridOptions={"rowSelection": "multiple", "enableCellTextSelection": True, "ensureDomOrder": True},

    ),
    dbc.Row([
        dbc.Col([dbc.Button("Custom maatregel toevoegen", id=ADD_CUSTOM_MEASURE_BUTTON_ID, color="primary",
                            className="mr-1")], md=3),
        dbc.Col([dbc.Button("Remove custom maatereglen from database", id=REMOVE_CUSTOM_MEASURE_BUTTON_ID,
                            color="primary", className="mr-1")], md=3),
    ]),

])

right_side = html.Div([])

custom_measure_tab_layout = html.Div([
    dbc.Row([
        dbc.Col([left_side], md=6),
        dbc.Col([right_side], md=6),
    ]),
])
