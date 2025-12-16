import dash_bootstrap_components as dbc
from dash import dcc, html

from src.component_ids import (
    CLOSE_CUSTOM_MEAS_MODAL_BUTTON_ID,
    CUSTOM_MEASURE_MODEL_ID,
    MESSAGE_MODAL_CUSTOM_MEASURE_ID,
)

modal_custom_measure = dbc.Modal(
    [
        dbc.ModalBody("Custom maatregelen toevoegen"),
        html.Div(
            [
                html.P(
                    id=MESSAGE_MODAL_CUSTOM_MEASURE_ID,
                    children=["Custom maatregelen toegevoegd!"],
                ),
            ],
            style={"padding": "20px"},
        ),
        dbc.ModalFooter(
            # add a button to close the modal
            dbc.Button(
                "Afsluiten", id=CLOSE_CUSTOM_MEAS_MODAL_BUTTON_ID, className="ml-auto"
            )
        ),
    ],
    id=CUSTOM_MEASURE_MODEL_ID,
    is_open=False,
)
