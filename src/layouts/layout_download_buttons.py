from dash import dcc, html
import dash_bootstrap_components as dbc
from src.component_ids import DOWNLOAD_OVERVIEW_BUTTON_ID, DOWNLOAD_OVERVIEW_ID

layout_download_overview = html.Div(
    [
        # vertical spacing
        html.Br(),
        dbc.Button("Download geojson", id=DOWNLOAD_OVERVIEW_BUTTON_ID, color="primary", className="mr-1"),
        dcc.Download(id=DOWNLOAD_OVERVIEW_ID),
    ]
)
