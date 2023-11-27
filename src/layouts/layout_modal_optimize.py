import dash_bootstrap_components as dbc
from dash import dcc, html
from src.component_ids import OPTIMIZE_MODAL_ID

modal_optimize = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("")),
        dbc.ModalBody("VRTool optimization is running..."),
        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,  # in milliseconds
            n_intervals=0
        ),
        html.Div(id='latest-timestamp', style={"padding": "20px"}),
        dbc.ModalFooter(
        ),
    ],
    id=OPTIMIZE_MODAL_ID,
    is_open=False,
)
