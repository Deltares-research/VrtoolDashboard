from dash import html
import dash_bootstrap_components as dbc

from src.component_ids import OVERVIEW_PROJECT_MAP_ID
def layout_project_output_tab_one() -> html.Div:
    return html.Div(
        children=[
            dbc.Row([
                dbc.Col([html.H2("Overzicht Project")], md=10),
            ]),

            html.H2("Project overzicht"),
            html.Div(id=OVERVIEW_PROJECT_MAP_ID,
                     style={'width': '90vh', 'height': '60vh', 'border': "2px solid black"}),

        ])