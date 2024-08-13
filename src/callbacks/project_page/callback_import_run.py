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
    STORED_PROJECT_DATA
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

    :param filename: name of the uploaded zip file.

    :return: Return a tuple with:
        - html.Div with the serialized dike traject data.
        - html.Div with the toast message.
        - boolean indicating if the upload was successful.
        - value of the dropdown selection run id.
    """
    print(1)
    if stored_project_data is None:
        stored_project_data = dict()
    if contents is not None:
        print(2)
        try:

            content_type, content_string = contents.split(',')

            decoded = base64.b64decode(content_string)
            json_content = json.loads(decoded)
            print(3)
            print(stored_project_data)
            traject_name, run_name = json_content["name"], json_content["run_name"]
            print(4)

            stored_project_data[f"{traject_name}_{run_name}"] = json_content
            print(stored_project_data.keys())
            print(5)
            return stored_project_data

        except:
            return dash.no_update
    else:
        return dash.no_update
