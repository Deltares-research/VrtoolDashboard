import dash
from dash import html, dcc, callback, Output, Input

from src.component_ids import OPTIMIZE_MODAL_ID
from src.layouts.layout_vr_optimalization import dike_vr_optimization_layout_ag_grid
from src.plotly_graphs.plotly_maps import plot_default_overview_map_dummy

dash.register_page(__name__)

layout = html.Div([dike_vr_optimization_layout_ag_grid,
                   # dcc.Store(id='stored-data', data=None, storage_type="local"),
                   ],
                  )


@callback(Output(OPTIMIZE_MODAL_ID, "is_open", allow_duplicate=True),
          [Input("stored-data", "data")],
          prevent_initial_call=True,
          )
def make_test(dike_traject_data: dict) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data: The data of the dike traject to be displayed.
    """
    print("this is a test")

    return False
