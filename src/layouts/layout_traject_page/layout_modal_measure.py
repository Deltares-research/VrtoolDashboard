import dash_bootstrap_components as dbc
from dash import html, dcc

from src.component_ids import MEASURE_MODAL_ID, CLOSE_MEASURE_MODAL_BUTTON_ID, GRAPH_MEASURE_RELIABILITY_TIME_ID
from src.plotly_graphs.pf_length_cost import plot_default_scatter_dummy

modal_measure_reliability = dbc.Modal(
    [
        dbc.ModalBody("Maateregelen"),

        html.Div(
            children=[
                dcc.Graph(id=GRAPH_MEASURE_RELIABILITY_TIME_ID, figure=plot_default_scatter_dummy(),
                          style={'width': '100%', 'height': '100%'},
                          )
            ]
        ),
        dbc.ModalFooter(
            # add a button to close the modal
            dbc.Button("Close", id=CLOSE_MEASURE_MODAL_BUTTON_ID, className="ml-auto")
        ),
    ],
    id=MEASURE_MODAL_ID,
    is_open=False,
)
