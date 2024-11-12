from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable

from src.component_ids import OPTIMIZE_BUTTON_ID, DUMMY_OPTIMIZE_BUTTON_OUTPUT_ID, EDITABLE_TRAJECT_TABLE_ID, \
    NAME_NEW_OPTIMIZATION_RUN_ID

import dash_ag_grid as dag
import pandas as pd

from src.constants import Measures

"""
Inspiration for cell toggle: https://community.plotly.com/t/checkbox-column-in-dash-ag-grid/78670/6
"""

columns_defs = [
    {"field": "section_col",
     "headerName": "Dijkvak",
     "editable": False,
     "initialWidth": 100},

    {"field": "reinforcement_col",
     "headerName": "Versterking",
     "cellRenderer": "DBC_Switch",
     "editable": True,
     "CellRendererParams": {"onColor": "success", "offColor": "danger"},
     "initialWidth": 120, },

    {"field": "reference_year",
     "headerName": "Referentiejaar",
     "editable": True,
     "initialWidth": 160, },

    {"field": Measures.GROUND_IMPROVEMENT.name,
     "headerName": Measures.GROUND_IMPROVEMENT.value,
     "editable": True,
     "cellRenderer": "DBC_Switch",
     "CellRendererParams": {"onColor": "success", "offColor": "danger"}},

    {"field": Measures.GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN.name,
     "headerName": Measures.GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN.value,
     "cellRenderer": "DBC_Switch",
     "editable": True,
     "CellRendererParams": {"onColor": "success", "offColor": "danger"},
     "initialWidth": 160, },

    {"field": Measures.GEOTEXTILE.name,
     "headerName": Measures.GEOTEXTILE.value,
     "editable": True,
     "cellRenderer": "DBC_Switch",
     "CellRendererParams": {"onColor": "success", "offColor": "danger"},
     "initialWidth": 80, },

    {"field": Measures.DIAPHRAGM_WALL.name,
     "headerName": Measures.DIAPHRAGM_WALL.value,
     "editable": True,
     "cellRenderer": "DBC_Switch",
     "CellRendererParams": {"onColor": "success", "offColor": "danger"}},

    {"field": Measures.STABILITY_SCREEN.name,
     "headerName": Measures.STABILITY_SCREEN.value,
     "editable": True,
     "cellRenderer": "DBC_Switch",
     "CellRendererParams": {"onColor": "success", "offColor": "danger"}},

]
df = pd.DataFrame(columns=["section_col", "reinforcement_col", "reference_year",
                           Measures.GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN.value,
                           Measures.GROUND_IMPROVEMENT.value,
                           Measures.GEOTEXTILE.value,
                           Measures.DIAPHRAGM_WALL.value,
                           Measures.STABILITY_SCREEN.value

                           ])  # empty dataframe

dike_vr_optimization_layout_ag_grid = html.Div([
    # add text
    dcc.Markdown(
        '''
        Vanuit dit scherm kunnen nieuwe optimalisatieberekeningen worden gestart.

        In onderstaande tabel kan per dijkvak worden aangegeven of deze versterkt moet worden en in welk referentiejaar.

        Daarnaast kan aangegeven worden welke maatregelen moeten worden meegenomen.
        
        Door onderaan een (unieke) naam op te geven en op 'Start optimalisatie' te drukken wordt een berekening met de VRTOOL gestart.
        Let op: deze berekening kan enige tijd duren!
        '''
    ),    dag.AgGrid(
        id=EDITABLE_TRAJECT_TABLE_ID,
        rowData=df.to_dict('records'),
        columnDefs=columns_defs,
        defaultColDef={"resizable": True,
                       "wrapHeaderText": True,
                       "autoHeaderHeight": True, },
        dashGridOptions={"rowSelection": "multiple", "enableCellTextSelection": True, "ensureDomOrder": True}

    ),

    html.Div(
        [
            dbc.Input(id=NAME_NEW_OPTIMIZATION_RUN_ID, placeholder="Naam berekening", type="text"),
            dbc.Button("Start optimalisatieberekening", id=OPTIMIZE_BUTTON_ID, color="primary", className="mr-1"),
            dbc.Tooltip("Klik hier om de berekening met de geselecteerde maatregelen te starten.",
                        target=OPTIMIZE_BUTTON_ID),
            html.Div(id=DUMMY_OPTIMIZE_BUTTON_OUTPUT_ID)
        ])
])
