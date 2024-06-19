import dash
from dash import callback, Input, Output, State

from src.component_ids import EDITABLE_CUSTOM_MEASURE_TABLE_ID


@callback(
    Output(EDITABLE_CUSTOM_MEASURE_TABLE_ID, "rowTransaction"),
    Input("add-row-button", "n_clicks"),
    prevent_initial_call=True,
)
def update_rowdata(_):
    return {
        "addIndex": 0,
        "add": [{"make": None, "model": None, "price": None}]
    }


@callback(
    Output(EDITABLE_CUSTOM_MEASURE_TABLE_ID, "rowData"),
    Input("copy-row-button", "n_clicks"),
    State(EDITABLE_CUSTOM_MEASURE_TABLE_ID, 'selectedRows'),
    State(EDITABLE_CUSTOM_MEASURE_TABLE_ID, 'rowData'),
    prevent_initial_call=True,
)
def copy_row(n_click, selected_row, row_data):
    if n_click is not None and selected_row:
        row_data.append(selected_row[0])

        return row_data
    return dash.no_update
