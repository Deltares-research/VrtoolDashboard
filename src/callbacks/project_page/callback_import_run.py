import dash
from dash import html, dcc, Output, Input, State, callback
import plotly.graph_objects as go

from src.component_ids import STORED_IMPORTED_RUNS_DATA, EDITABLE_IMPORTED_RUNS_TABLE_ID, OVERVIEW_PROJECT_MAP_ID_2

import base64
import json

from src.plotly_graphs.project_page.plotly_maps import plot_comparison_runs_overview_map


@callback(
    Output(STORED_IMPORTED_RUNS_DATA, "data"),
    [Input('upload-dike-data', 'contents')],
    [State('upload-dike-data', 'filename'),
     State(STORED_IMPORTED_RUNS_DATA, "data")],
    allow_duplicate=True,
    prevent_initial_call=True,
)
def upload_and_save_in_project_data(contents: str, filename: str, stored_imported_runs_data: dict):
    """This is the callback for the upload of the config.json file.

    :param contents: string content of the uploaded json. The file should content at least:
        - traject: name of the traject
        - input_directory: directory where the input database is located.
        - input_database_name: name of the input database.
        - excluded_mechanisms: list of mechanisms to be excluded from the analysis.

    :param filename: name of the uploaded file.

    :return:
    """
    if stored_imported_runs_data is None:
        stored_imported_runs_data = dict()
    if contents is not None:
        try:

            content_type, content_string = contents.split(',')

            decoded = base64.b64decode(content_string)
            json_content = json.loads(decoded)
            traject_name, run_name = json_content["name"], json_content["run_name"]
            stored_imported_runs_data[f"{traject_name}"] = json_content
            return stored_imported_runs_data

        except:
            return dash.no_update
    else:
        return dash.no_update


#
@callback(
    Output(EDITABLE_IMPORTED_RUNS_TABLE_ID, "rowData"),
    # Output(OVERVIEW_PROJECT_MAP_ID_2, "figure"),
    Input(STORED_IMPORTED_RUNS_DATA, "data"),
    Input("tabs_tab_project_page", "active_tab")
)
def fill_table_project_overview_and_update_map(imported_runs_data: dict, dummy: str) -> list[dict]:
    """
    Fill the overview table with the project data wth the imported dike traject data.
    :param project_data:
    :param dummy: Dummy to keep the table displayed when switching tabs and pages.

    :return:
    """
    row_data = []

    if imported_runs_data is None:
        return dash.no_update
    if imported_runs_data == {}:
        return dash.no_update

    for traject_run in imported_runs_data.keys():
        traject = traject_run
        run = imported_runs_data[traject_run]["run_name"]
        row_data.append({"traject": traject, "run_name": run, "active": False})
    # _fig = plot_comparison_runs_overview_map(imported_runs_data)

    return row_data
