import dash_bootstrap_components as dbc
from dash import dcc, html
from src.component_ids import OPTIMIZE_MODAL_ID, CLOSE_OPTIMAL_MODAL_BUTTON_ID

modal_optimize = dbc.Modal(
    [
        dbc.ModalBody("Berekening met VRTool draait..."),
        dcc.Interval(
            id="interval-component", interval=1 * 1000, n_intervals=0  # in milliseconds
        ),
        html.Div(
            [
                html.P(id="latest-timestamp", children=["Nog geen feedback van de berekening"]),
            ],
            style={"padding": "20px"},
        ),
        dbc.ModalFooter(
            # add a button to close the modal
            dbc.Button("Close", id=CLOSE_OPTIMAL_MODAL_BUTTON_ID, className="ml-auto")
        ),
    ],
    id=OPTIMIZE_MODAL_ID,
    is_open=False,
    size="lg",
)
