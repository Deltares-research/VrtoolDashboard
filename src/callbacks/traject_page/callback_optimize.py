from dash import Output, Input, State

from src.app import app


@app.callback(
    Output("stored-data-dike-traject", "data"),
    [
        Input("optimize-button", "n_clicks")],
    State("stored-data-dike-traject", "data"),
)
def run_optimize_algorithm(n_clicks: int, stored_data: dict) -> dict:
    """
    This is a callback to run the optimization algorithm when the user clicks on the "Optimaliseer" button.

    :param stored_data: data from the database.
    :return:
    """
    print(n_clicks)
