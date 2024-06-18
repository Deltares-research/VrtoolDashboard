import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

from src.component_ids import OPTIMIZE_MODAL_ID
from src.layouts.layout_database_interaction.layout_vr_optimalization import dike_vr_optimization_layout_ag_grid

dash.register_page(__name__)

layout = html.Div([

    dbc.Tabs(
        [
            dbc.Tab(label="Run Optimize", tab_id="tab-11"),
            dbc.Tab(label="Custom maatregelen", tab_id="tab-12"),
        ],
        id="tabs_database_interaction",
        active_tab="tab-11",  # Set the initial active tab
    ),
    html.Div(id="content_tab_database_interaction"),

    # dike_vr_optimization_layout_ag_grid,
],
)
