import dash
from dash import html, dcc, callback, Output, Input

from src.component_ids import OPTIMIZE_MODAL_ID
from src.layouts.layout_database_interaction.layout_vr_optimalization import dike_vr_optimization_layout_ag_grid

dash.register_page(__name__)

layout = html.Div([dike_vr_optimization_layout_ag_grid,
                   ],
                  )


