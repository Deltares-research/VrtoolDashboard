import dash_bootstrap_components as dbc
from dash import html

from src.component_ids import MEASURE_MODAL_ID, CLOSE_MEASURE_MODAL_BUTTON_ID

modal_measure_reliability = dbc.Modal(
    [
        dbc.ModalBody("Maateregelen"),

        html.Div(
            children=[]
        ),
        dbc.ModalFooter(
            # add a button to close the modal
            dbc.Button("Close", id=CLOSE_MEASURE_MODAL_BUTTON_ID, className="ml-auto")
        ),
    ],
    id=MEASURE_MODAL_ID,
    is_open=False,
)
