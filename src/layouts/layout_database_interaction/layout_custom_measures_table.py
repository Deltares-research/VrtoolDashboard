import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html

from src.component_ids import (
    ADD_CUSTOM_MEASURE_BUTTON_ID,
    EDITABLE_CUSTOM_MEASURE_TABLE_ID,
    IMPORTER_CUSTOM_MEASURE_CSV_ID,
    MESSAGE_ERASE_CUSTOM_MEASURE_ID,
    REMOVE_CUSTOM_MEASURE_BUTTON_ID,
)
from src.constants import Mechanism

columns_defs = [
    {
        "field": "measure_name",
        "headerName": "Naam maatregel",
        "editable": False,
        "initialWidth": 180,
    },
    # {"field": "section_name",
    #  "headerName": "Sectie",
    #  "editable": True,
    #  "initialWidth": 100, },
    {
        "field": "section_name",
        "headerName": "Dijkvak",
        "editable": False,
        "cellEditor": "agSelectCellEditor",
        "cellEditorParams": {
            "values": [],
        },
        "initialWidth": 140,
    },
    {
        "field": "mechanism",
        "headerName": "Mechanisme",
        "editable": False,
        "cellEditor": "agSelectCellEditor",
        "cellEditorParams": {
            "values": [
                mecha.value for mecha in Mechanism if mecha != Mechanism.SECTION
            ],
        },
        "initialWidth": 140,
    },
    {
        "field": "time",
        "headerName": "Tijd",
        "editable": False,
        "initialWidth": 100,
    },
    {
        "field": "cost",
        "headerName": "Kosten (€)",
        "editable": False,
        "initialWidth": 140,
    },
    {
        "field": "beta",
        "headerName": "Betrouwbaarheid (β)",
        "editable": False,
        "initialWidth": 140,
    },
]
df = pd.DataFrame(
    columns=[col["field"] for col in columns_defs],
    data=[
        # ["Rock", "7", "Piping", 0, 2000, 3.5]
    ],
)  # empty dataframe

right_side = html.Div(
    [
        # add text
        # add white space
        html.Br(),
        dbc.Row(
            [
                # dbc.Col([dbc.Button("Custom maatregel toevoegen", id=ADD_CUSTOM_MEASURE_BUTTON_ID, color="primary",
                #                     className="mr-1")], md=3),
                dbc.Col(
                    [
                        dbc.Button(
                            "Verwijder alle custom maatregelen uit database",
                            id=REMOVE_CUSTOM_MEASURE_BUTTON_ID,
                            color="primary",
                            className="mr-1",
                        ),
                        html.Div(id=MESSAGE_ERASE_CUSTOM_MEASURE_ID, children=[""]),
                    ],
                    md=3,
                ),
            ]
        ),
    ]
)

left_side = html.Div(
    [
        dcc.Upload(
            id=IMPORTER_CUSTOM_MEASURE_CSV_ID,
            children=html.Div(["", html.A("Importeer een maatregelen bestand (.csv)")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            # Allow multiple files to be uploaded
            multiple=False,
            accept=".csv",
        ),
        dcc.Markdown(
            """
        Met de onderstaande tabel, kunt u custom maatregelen aan de database toevoegen en verwijderen.
        """
        ),
        # add white space
        html.Br(),
        dag.AgGrid(
            id=EDITABLE_CUSTOM_MEASURE_TABLE_ID,
            rowData=df.to_dict("records"),
            columnDefs=columns_defs,
            defaultColDef={
                "resizable": True,
                "wrapHeaderText": True,
                "autoHeaderHeight": True,
            },
            dashGridOptions={
                "rowSelection": "multiple",
                "enableCellTextSelection": True,
                "ensureDomOrder": True,
            },
        ),
    ]
)

custom_measure_tab_layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col([left_side], md=6),
                dbc.Col([right_side], md=6),
            ]
        ),
    ]
)
