import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dash_table import DataTable
from dash.html import Br
import dash_ag_grid as dag
import dash_mantine_components as dmc

from src.component_ids import EDITABLE_IMPORTED_RUNS_TABLE_ID, TABLE_PROJECT_SUMMARY_ID, \
    MULTI_SELECT_SECTION_FOR_PROJECT_ID, ADD_PROJECT_BUTTON_ID, PROJECT_NAME_INPUT_FIELD_ID, ALERT_PROJECT_CREATION_ID, \
    UPDATE_PROJECT_BUTTON_ID, PROJECT_START_YEAR_INPUT_FIELD_ID, DELETE_PROJECT_BUTTON_ID, \
    PROJECT_END_YEAR_INPUT_FIELD_ID, EXPORT_PROJECTS_TO_JSON_ID, BUTTON_DOWNLOAD_PROJECTS_EXPORT, UPLOAD_SAVED_PROJECTS, \
    CONTENT_TABS_COMPARISON_PAGE_ID, OVERVIEW_COMPARISON_MAP_ID, OVERVIEW_PROJECT_MAP_ID_2
from src.layouts.layout_traject_page.layout_download_buttons import layout_download_projects
from src.plotly_graphs.plotly_maps import plot_default_overview_map_dummy

df_imported_run_table = pd.DataFrame(columns=["traject", "run_name", "active"], data=[])
df_project_summary_table = pd.DataFrame(columns=["project", "section_number", "start_year", "end_year" "length"],
                                        data=[])

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

    {"field": "start_year",
     "headerName": "Jaar begin",
     "editable": False,
     "initialWidth": 100},

    {"field": "end_year",
     "headerName": "Jaar eind",
     "editable": False,
     "initialWidth": 100},

]

table_importe_dike_data = dag.AgGrid(
    id=EDITABLE_IMPORTED_RUNS_TABLE_ID,
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

    # Add text in Dutch: "or" centered in the middle of the page
    html.P("of", style={"text-align": "center"}),

    dcc.Upload(
        id=UPLOAD_SAVED_PROJECTS,
        children=html.Div([
            '',
            html.A('Upload een project bestand .json')
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
                    dmc.TextInput(label="Project naam", id=PROJECT_NAME_INPUT_FIELD_ID, style={"width": "15%"}),
                    multi_select,
                    dmc.NumberInput(id=PROJECT_START_YEAR_INPUT_FIELD_ID, min=2025, max=2125, step=5,
                                    label="Jaar begin",
                                    style={"width": "11%"}),
                    dmc.NumberInput(id=PROJECT_END_YEAR_INPUT_FIELD_ID, min=2025, max=2125, step=5, label="Jaar eind",
                                    style={"width": "11%"}),
                    dbc.Alert(children="", id=ALERT_PROJECT_CREATION_ID, color="danger", is_open=False,
                              dismissable=True),
                    dmc.Button("Maak project aan", id=ADD_PROJECT_BUTTON_ID),
                    dmc.Button("Update project", id=UPDATE_PROJECT_BUTTON_ID),
                    dmc.Button("Verwijder project", id=DELETE_PROJECT_BUTTON_ID),

                ]),
                dmc.Group([
                    table_project_summary,
                    layout_download_projects,

                ])

            ],
            title='Projects overzicht')
    ]),

]

right_side = [

    html.Div(
        children=[

            html.Div(
                style={'width': '90vh', 'height': '60vh', 'border': "2px solid black"},
                children=dcc.Graph(
                    id=OVERVIEW_PROJECT_MAP_ID_2,
                    figure=plot_default_overview_map_dummy(),
                    style={"width": "100%", "height": "100%"},
                )
            ),

        ])

]

project_definition_tab_layout = html.Div([
    dbc.Row([
        dbc.Col(left_side, md=5),
        dbc.Col(right_side, md=7),
    ]),
])
