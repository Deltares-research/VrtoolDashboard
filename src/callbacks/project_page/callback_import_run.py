from pathlib import Path

import dash
from dash import html, dcc, Output, Input, State, callback
import dash_bootstrap_components as dbc
from vrtool.common.enums import MechanismEnum
from vrtool.defaults.vrtool_config import VrtoolConfig
import pandas as pd

from src.component_ids import STORE_CONFIG, DROPDOWN_SELECTION_RUN_ID, EDITABLE_TRAJECT_TABLE_ID, \
    SLIDER_YEAR_RELIABILITY_RESULTS_ID, GREEDY_OPTIMIZATION_CRITERIA_BETA, GREEDY_OPTIMIZATION_CRITERIA_YEAR, \
    BUTTON_RECOMPUTE_GREEDY_STEPS, BUTTON_RECOMPUTE_GREEDY_STEPS_NB_CLICKS, SELECT_GREEDY_OPTIMIZATION_STOP_CRITERIA, \
    STORED_PROJECT_DATA, EDITABLE_PROJECT_TABLE_ID
from src.constants import ColorBarResultType, SubResultType, Measures, REFERENCE_YEAR
from src.linear_objects.dike_traject import DikeTraject

import base64
import json

from src.orm.import_database import get_dike_traject_from_config_ORM, get_name_optimization_runs, \
    get_run_optimization_ids
from src.utils.utils import get_vr_config_from_dict, export_to_json


@callback(
    Output(STORED_PROJECT_DATA, "data"),
    [Input('upload-dike-data', 'contents')],
    [State('upload-dike-data', 'filename'),
     State(STORED_PROJECT_DATA, "data")],
    allow_duplicate=True,
    prevent_initial_call=True,
)
def upload_and_save_in_project_data(contents: str, filename: str, stored_project_data: dict):
    """This is the callback for the upload of the config.json file.

    :param contents: string content of the uploaded json. The file should content at least:
        - traject: name of the traject
        - input_directory: directory where the input database is located.
        - input_database_name: name of the input database.
        - excluded_mechanisms: list of mechanisms to be excluded from the analysis.

    :param filename: name of the uploaded file.

    :return:
    """
    if stored_project_data is None:
        stored_project_data = dict()
    if contents is not None:
        try:

            content_type, content_string = contents.split(',')

            decoded = base64.b64decode(content_string)
            json_content = json.loads(decoded)
            traject_name, run_name = json_content["name"], json_content["run_name"]

            stored_project_data[f"{traject_name}|{run_name}"] = json_content
            return stored_project_data

        except:
            return dash.no_update
    else:
        return dash.no_update


#
@callback(
    Output(EDITABLE_PROJECT_TABLE_ID, "rowData"),
    Input(STORED_PROJECT_DATA, "data"),
    Input("tabs_tab_project_page", "active_tab")
)
def fill_table_project_overview(project_data: dict, dummy: str) -> list[dict]:
    """
    Fill the overview table with the project data wth the imported dike traject data.
    :param project_data:
    :param dummy: Dummy to keep the table displayed when switching tabs and pages.

    :return:
    """
    row_data = []
    if project_data is None:
        return dash.no_update
    if project_data == {}:
        return dash.no_update

    for traject_run in project_data.keys():
        traject, run = traject_run.split("|")
        row_data.append({"traject": traject, "run_name": run, "active": False})

    return row_data
