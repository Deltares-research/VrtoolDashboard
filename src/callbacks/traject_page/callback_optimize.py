import dash
from dash import Output, Input, State

from src.app import app
from src.component_ids import OPTIMIZE_BUTTON_ID


@app.callback(
    Output("stored-data", "data"),
    [
        Input(OPTIMIZE_BUTTON_ID, "n_clicks")],
    Input("stored-data", "data"),
    prevent_initial_call=True
)
def run_optimize_algorithm(n_clicks: int, stored_data: dict) -> dict:
    """
    This is a callback to run the optimization algorithm when the user clicks on the "Optimaliseer" button.
    :param stored_data: data from the database.
    :return:
    """
    if stored_data is None:
        return dash.no_update
    else:
        print(n_clicks)
        return stored_data
