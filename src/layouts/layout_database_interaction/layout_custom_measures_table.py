import pandas as pd
from dash import html, dcc
import dash_ag_grid as dag
import dash_bootstrap_components as dbc

from src.component_ids import EDITABLE_CUSTOM_MEASURE_TABLE_ID, ADD_CUSTOM_MEASURE_BUTTON_ID, \
    REMOVE_CUSTOM_MEASURE_BUTTON_ID
from src.constants import Mechanism

columns_defs = [
    {"field": "measure_name",
     "headerName": "Naam maatregel",
     "editable": True,
     "initialWidth": 180},

    # {"field": "section_name",
    #  "headerName": "Sectie",
    #  "editable": True,
    #  "initialWidth": 100, },
    {"field": "section_name",
     "headerName": "Dijkvak",
     "editable": True,
     'cellEditor': 'agSelectCellEditor',
     'cellEditorParams': {
         'values': [],
     },
     "initialWidth": 140, },

    {"field": "mechanism",
     "headerName": "Mechanisme",
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
     "headerName": "Kosten (€)",
     "editable": True,
     "initialWidth": 140, },

    {"field": "beta",
     "headerName": "Betrouwbaarheid (β)",
     "editable": True,
     "initialWidth": 140, },

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
        Met de onderstaande tabel, kunt u custom maatregelen aan de database toevoegen en verwijderen.
        '''
    ),
    dbc.Row([
        dbc.Col(dbc.Button("Voeg rij toe", id="add-row-button", color="light", className="me-2", style={"width": "100%", "height": "60px"}), md=2),
        dbc.Col(dbc.Button("Kopieer geselecteerde rij", id="copy-row-button", color="light", className="me-2", style={"width": "100%", "height": "60px"}), md=2),
        dbc.Col(dbc.Button("Verwijder rij", id="delete-row-button", color="light", className="me-2", style={"width": "100%", "height": "60px"}), md=2),
    ]),
    #add white space
    html.Br(),
    dag.AgGrid(
        id=EDITABLE_CUSTOM_MEASURE_TABLE_ID,
        rowData=df.to_dict('records'),
        columnDefs=columns_defs,
        defaultColDef={"resizable": True,
                       "wrapHeaderText": True,
                       "autoHeaderHeight": True, },
        dashGridOptions={"rowSelection": "multiple", "enableCellTextSelection": True, "ensureDomOrder": True},

    ),
    #add white space
    html.Br(),
    dbc.Row([
        dbc.Col([dbc.Button("Custom maatregel toevoegen", id=ADD_CUSTOM_MEASURE_BUTTON_ID, color="primary",
                            className="mr-1")], md=3),
        dbc.Col([dbc.Button("Verwijder custom maatregelen uit database", id=REMOVE_CUSTOM_MEASURE_BUTTON_ID,
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
