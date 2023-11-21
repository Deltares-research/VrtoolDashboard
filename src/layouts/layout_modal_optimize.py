import dash_bootstrap_components as dbc

from src.component_ids import OPTIMIZE_MODAL_ID

modal_optimize = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Header")),
        dbc.ModalBody("VRTool optimization is running..."),
        dbc.ModalFooter(
            dbc.Button(
                "Close", id="close", className="ms-auto", n_clicks=0
            )
        ),
    ],
    id=OPTIMIZE_MODAL_ID,
    is_open=False,
)
