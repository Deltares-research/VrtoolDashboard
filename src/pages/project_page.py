import dash
from dash import html
import dash_bootstrap_components as dbc


dash.register_page(__name__)


layout = html.Div([
    dbc.Tabs(
        [
            dbc.Tab(label="Project definitie", tab_id="tab-111"),
            dbc.Tab(label="Visualizatie", tab_id="tab-112"),
        ],
        id="tabs_tab_project_page",
        active_tab="tab-111",  # Set the initial active tab
    ),
    html.Div(id="content_tab_project_page"),


])