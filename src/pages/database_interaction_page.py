import dash
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(__name__)

layout = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Run Optimize", tab_id="tab-11"),
                dbc.Tab(label="Custom maatregelen", tab_id="tab-12"),
            ],
            id="tabs_database_interaction",
            active_tab="tab-11",  # Set the initial active tab
        ),
        html.Div(id="content_tab_database_interaction"),
    ],
)
