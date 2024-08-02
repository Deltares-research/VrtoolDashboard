import pandas as pd
from dash import html, dcc
import dash_ag_grid as dag
import dash_bootstrap_components as dbc

from src.component_ids import EDITABLE_CUSTOM_MEASURE_TABLE_ID, ADD_CUSTOM_MEASURE_BUTTON_ID
from src.constants import Mechanism

columns_defs = [
    {"field": "measure_name",
     "headerName": "Maatregel naam",
     "editable": True,
     "initialWidth": 180},

    {"field": "section_name",
     "headerName": "Sectie",
     "editable": True,
     "initialWidth": 100, },

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

custom_measure_tab_layout = html.Div([
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

    dbc.Button("Custom maatregel toevoegen", id=ADD_CUSTOM_MEASURE_BUTTON_ID, color="primary", className="mr-1"),
    # dash_table.DataTable(
    #     columns=[
    #         {"name": ["", "Year"], "id": "year" },
    #         {"name": ["City", "Montreal"], "id": "montreal", "deletable": [False, True]},
    #         {"name": ["City", "Toronto"], "id": "toronto", "renamable": True },
    #         {"name": ["City", "Ottawa"], "id": "ottawa", "hideable": "last"},
    #         {"name": ["City", "Vancouver"], "id": "vancouver"},
    #         {"name": ["Climate", "Temperature"], "id": "temp"},
    #         {"name": ["Climate", "Humidity"], "id": "humidity"},
    #     ],
    #     data=[
    #         {
    #             "year": i,
    #             "montreal": i * 10,
    #             "toronto": i * 100,
    #             "ottawa": i * -1,
    #             "vancouver": i * -10,
    #             "temp": i * -100,
    #             "humidity": i * 5,
    #         }
    #         for i in range(10)
    #     ],
    #     editable=True,
    #
    #     export_format='xlsx',
    #     export_headers='display',
    #     merge_duplicate_headers=True
    # )

])
