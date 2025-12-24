import base64
import json
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, callback, dcc, html
from vrtool.common.enums import MechanismEnum
from vrtool.defaults.vrtool_config import VrtoolConfig

from src.component_ids import EDITABLE_COMPARISON_TABLE_ID, STORED_RUNS_COMPARISONS_DATA
from src.constants import REFERENCE_YEAR, ColorBarResultType, Measures, SubResultType
from src.linear_objects.dike_traject import DikeTraject
from src.orm.import_database import (
    get_dike_traject_from_config_ORM,
    get_name_optimization_runs,
    get_run_optimization_ids,
)
from src.utils.utils import export_to_json, get_vr_config_from_dict


@callback(
    Output(STORED_RUNS_COMPARISONS_DATA, "data"),
    [Input("upload-dike-data-comparison", "contents")],
    [
        State("upload-dike-data-comparison", "filename"),
        State(STORED_RUNS_COMPARISONS_DATA, "data"),
    ],
    allow_duplicate=True,
    prevent_initial_call=True,
)
def upload_and_save_in_project_data(
    contents: str, filename: str, stored_imported_runs_data: dict
):
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

            content_type, content_string = contents.split(",")

            decoded = base64.b64decode(content_string)
            json_content = json.loads(decoded)
            traject_name, run_name = json_content["name"], json_content["run_name"]
            stored_imported_runs_data[f"{traject_name}|{run_name}"] = json_content
            return stored_imported_runs_data

        except:
            return dash.no_update
    else:
        return dash.no_update


#
@callback(
    Output(EDITABLE_COMPARISON_TABLE_ID, "rowData"),
    Input(STORED_RUNS_COMPARISONS_DATA, "data"),
)
def fill_table_project_overview(imported_runs_data: dict) -> list[dict]:
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
        traject, run = traject_run.split("|")
        row_data.append({"traject": traject, "run_name": run, "active": False})

    return row_data
