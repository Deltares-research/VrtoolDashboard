import dash
from dash import html, dcc

from src.layouts.layout_vr_optimalization import dike_vr_optimization_layout_ag_grid

dash.register_page(__name__)

layout = html.Div([dike_vr_optimization_layout_ag_grid,
                   ],
                  )
