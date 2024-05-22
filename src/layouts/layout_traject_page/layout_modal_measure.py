import dash_bootstrap_components as dbc
from dash import dcc, html
from src.component_ids import OPTIMIZE_MODAL_ID, CLOSE_OPTIMAL_MODAL_BUTTON_ID, CLOSE_OPTIMAL_MEASURE_BUTTON_ID, \
    OPTIMIZE_MEASURE_ID

modal_optimize = dbc.Modal(
    [
        dbc.ModalBody("Maateregelen"),

        html.Div(
            children=[]
        ),
        dbc.ModalFooter(
            # add a button to close the modal
            dbc.Button("Close", id=CLOSE_OPTIMAL_MEASURE_BUTTON_ID, className="ml-auto")
        ),
    ],
    id=OPTIMIZE_MEASURE_ID,
    is_open=False,
)
