import dash
from dash import html, dcc
import dash_bootstrap_components as dbc


dash.register_page(__name__)


layout = html.Div([
    dcc.Tabs(
        [
            dcc.Tab(label="Project definitie",
                    id="tab-111",
                    className="custom-tab",
                    selected_className="custom-tab--selected"),
            dcc.Tab(label="Area results",
                    id="tab-112",
                    className="custom-tab",
                    selected_className="custom-tab--selected"),
        ],
        id="tabs_tab_project_page",
        value="tab-111",  # Set the initial active tab
        className="custom-tabs"
    ),
    html.Div(id="content_tab_project_page", children=[]),


])