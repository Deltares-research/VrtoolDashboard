import dash_bootstrap_components as dbc
from dash import dcc, html
from src.component_ids import OPTIMIZE_MODAL_ID, CLOSE_OPTIMAL_MODAL_BUTTON_ID

modal_optimize = dbc.Modal(
    [
        dbc.ModalBody("VRTool optimization is running..."),
        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,  # in milliseconds
            n_intervals=0
        ),
        html.Div(id='latest-timestamp', style={"padding": "20px"}),
        dbc.ModalFooter(
            # add a button to close the modal
            dbc.Button(
                "Close", id=CLOSE_OPTIMAL_MODAL_BUTTON_ID, className="ml-auto")
        ),
    ],
    id=OPTIMIZE_MODAL_ID,
    is_open=False,
)
