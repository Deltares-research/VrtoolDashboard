from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from src.component_ids import DOWNLOAD_OVERVIEW_BUTTON_ID, DOWNLOAD_OVERVIEW_ID, DOWNLOAD_ASSESSMENT_BUTTON_ID, \
    DOWNLOAD_ASSESSMENT_ID, DOWNLOAD_REINFORCED_SECTIONS_BUTTON_ID, DOWNLOAD_REINFORCED_SECTIONS_ID, \
    BUTTON_DOWNLOAD_OVERVIEW_NB_CLICKS, BUTTON_DOWNLOAD_ASSESSMENT_NB_CLICKS, \
    BUTTON_DOWNLOAD_REINFORCED_SECTIONS_NB_CLICKS, EXPORT_PROJECTS_TO_JSON_ID, BUTTON_DOWNLOAD_PROJECTS_EXPORT, \
    BUTTON_DOWNLOAD_PROJECTS_EXPORT_NB_CLICKS, SAVE_PROJECTS_NAME_ID

layout_download_overview = html.Div(
    [
        # vertical spacing
        html.Br(),
        dbc.Button("Download geojson", id=DOWNLOAD_OVERVIEW_BUTTON_ID, color="primary", className="mr-1"),
        dcc.Download(id=DOWNLOAD_OVERVIEW_ID),
        dcc.Input(id=BUTTON_DOWNLOAD_OVERVIEW_NB_CLICKS, value=0, type='hidden')
    ]
)

layout_download_assessment = html.Div(
    [
        # vertical spacing
        html.Br(),
        dbc.Button("Download geojson", id=DOWNLOAD_ASSESSMENT_BUTTON_ID, color="primary", className="mr-1"),
        dcc.Download(id=DOWNLOAD_ASSESSMENT_ID),
        dcc.Input(id=BUTTON_DOWNLOAD_ASSESSMENT_NB_CLICKS, value=0, type='hidden')
    ]
)

layout_download_reinforced_sections = html.Div(
    [
        # vertical spacing
        html.Br(),
        dbc.Button("Download geojson", id=DOWNLOAD_REINFORCED_SECTIONS_BUTTON_ID, color="primary", className="mr-1"),
        dcc.Download(id=DOWNLOAD_REINFORCED_SECTIONS_ID),
        dcc.Input(id=BUTTON_DOWNLOAD_REINFORCED_SECTIONS_NB_CLICKS, value=0, type='hidden')
    ]
)

layout_download_projects = html.Div([

    # vertical spacing
    html.Br(),
    dbc.Button("Opslaan projects", id=BUTTON_DOWNLOAD_PROJECTS_EXPORT, color="primary", className="mr-1"),
    dmc.TextInput(id=SAVE_PROJECTS_NAME_ID , placeholder="Naam"),
    dcc.Download(id=EXPORT_PROJECTS_TO_JSON_ID),
    dcc.Input(id=BUTTON_DOWNLOAD_PROJECTS_EXPORT_NB_CLICKS, value=0, type='hidden')
]
)
