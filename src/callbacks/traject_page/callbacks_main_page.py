from pathlib import Path

import dash
from dash import html, dcc, Output, Input, State
from vrtool.common.enums import MechanismEnum
from vrtool.defaults.vrtool_config import VrtoolConfig

from src.component_ids import STORE_CONFIG, DROPDOWN_SELECTION_RUN_ID, EDITABLE_TRAJECT_TABLE_ID
from src.constants import ColorBarResultType, SubResultType, Measures
from src.linear_objects.dike_traject import DikeTraject

from src.app import app

import base64
import json

from src.orm.import_database import get_dike_traject_from_config_ORM, get_name_optimization_runs, \
    get_run_optimization_ids


@app.callback([Output('dummy_upload_id', 'children'),
               Output("upload-toast", "is_open"),
               Output(STORE_CONFIG, "data"),
               Output(DROPDOWN_SELECTION_RUN_ID, "value"),
               Output(DROPDOWN_SELECTION_RUN_ID, "options")
               ],
              [Input('upload-data-config-json', 'contents')],
              [State('upload-data-config-json', 'filename')],
              allow_duplicate=True,
              prevent_initial_call=True,
              )
def upload_and_save_traject_input(contents: str, filename: str, dbc=None) -> tuple:
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

    if contents is not None:
        try:
            print(1)

            content_type, content_string = contents.split(',')
            print(2)

            decoded = base64.b64decode(content_string)
            json_content = json.loads(decoded)
            print(3)

            vr_config = VrtoolConfig()
            vr_config.traject = json_content['traject']
            vr_config.input_directory = json_content['input_directory']
            vr_config.input_database_name = json_content['input_database_name']
            vr_config.excluded_mechanisms = json_content['excluded_mechanisms']
            # check is key is in the json:
            if 'output_directory' in json_content.keys():
                print(9999)
            if 'output_directoryyyy' in json_content.keys():
                print(88888)

            print(4)

            # _dike_traject = get_dike_traject_from_config_ORM(vr_config, run_id_dsn=2, run_is_vr=1)
            _value_selection_run_dropwdown = "default_run"

            # Update the selection Dropwdown with all the names of the optimization runs
            print("ici")
            _names_optimization_run = get_name_optimization_runs(vr_config)
            print(_names_optimization_run)
            _options = [{"label": "Default", "value": "default_run"}, ] + [{"label": name, "value": name} for name in
                                                                           _names_optimization_run]
            print(_options)

            return html.Div(
                dcc.Store(id='stored-data',
                          data={})), True, json_content, _value_selection_run_dropwdown, _options
        except:
            return html.Div("Geen bestand geüpload"), False, {}, "", []
    else:
        return html.Div("Geen bestand geüpload"), False, {}, "", []


@app.callback(
    Output('stored-data', 'data'),
    [Input(DROPDOWN_SELECTION_RUN_ID, "value")],
    State(STORE_CONFIG, "data"),
    prevent_initial_call=True
)
def selection_traject_run(name: str, vr_config) -> dict:
    """
    Callback to select the run id for the traject.

    :param name: name of the traject
    :return: DikeTraject object
    """

    if vr_config is None or vr_config == {}:
        return dash.no_update

    _vr_config = VrtoolConfig()
    _vr_config.traject = vr_config['traject']
    _vr_config.input_directory = Path(vr_config['input_directory'])
    _vr_config.output_directory = Path(vr_config['output_directory'])
    _vr_config.input_database_name = vr_config['input_database_name']
    _vr_config.excluded_mechanisms = [MechanismEnum.REVETMENT, MechanismEnum.HYDRAULIC_STRUCTURES]

    if name == "default_run":
        _dike_traject = get_dike_traject_from_config_ORM(_vr_config, run_id_dsn=2, run_is_vr=1)

    elif name in get_name_optimization_runs(_vr_config):
        run_id_vr, run_id_dsn = get_run_optimization_ids(_vr_config, name)
        _dike_traject = get_dike_traject_from_config_ORM(_vr_config, run_id_dsn=run_id_dsn, run_is_vr=run_id_vr)
    else:
        raise ValueError("Name of the Optimization run is not correct.")
    return _dike_traject.serialize()


@app.callback(
    Output("collapse_1", "is_open"),
    [Input("collapse_button_1", "n_clicks")],
    [State("collapse_1", "is_open")],
)
def toggle_collapse(n: int, is_open: bool) -> bool:
    """
    Callback to toggle the collapse of the first section.
    :param n: dummy integer
    :param is_open: boolean indicating if the collapse is open or not.
    :return:
    """
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse_2", "is_open"),
    [Input("collapse_button_2", "n_clicks")],
    [State("collapse_2", "is_open")],
)
def toggle_collapse2(n: int, is_open: bool) -> bool:
    """
    Callback to toggle the collapse of the second section.
    :param n: dummy integer
    :param is_open: boolean indicating if the collapse is open or not.
    :return:
    """
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse_3", "is_open"),
    [Input("collapse_button_3", "n_clicks")],
    [State("collapse_3", "is_open")],
)
def toggle_collapse3(n: int, is_open: bool) -> bool:
    """
    Callback to toggle the collapse of the second section.
    :param n: dummy integer
    :param is_open: boolean indicating if the collapse is open or not.
    :return:
    """
    if n:
        return not is_open
    return is_open


@app.callback(
    [Output('select_sub_result_type_measure_map', 'options'),
     Output('select_sub_result_type_measure_map', 'value')],
    Input('select_measure_map_result_type', 'value'),
)
def update_radio_sub_result_type(result_type: str) -> list:
    """
    This is a callback to update the sub Radio list depending on the result type selected by the user.
    If the result type is "RELIABILITY" then the sub Radio list will contain the options "Absoluut" and "Ratio vr/dsn".
    If the result type is "COST" then the sub Radio list will contain the options "Absoluut" and "Verschil vr-dsn".

    :param result_type: one of "RELIABILITY" or "COST" or "MEASURE"
    :return:
    """
    if result_type == ColorBarResultType.RELIABILITY.name:
        options = [
            {'label': SubResultType.ABSOLUTE.value, 'value': SubResultType.ABSOLUTE.name},
            {'label': SubResultType.RATIO.value, 'value': SubResultType.RATIO.name},
        ]
        value = SubResultType.ABSOLUTE.name
    elif result_type == ColorBarResultType.COST.name:
        options = [
            {'label': SubResultType.ABSOLUTE.value, 'value': SubResultType.ABSOLUTE.name},
            {'label': SubResultType.DIFFERENCE.value, 'value': SubResultType.DIFFERENCE.name},
        ]
        value = SubResultType.ABSOLUTE.name
    elif result_type == ColorBarResultType.MEASURE.name:
        options = [
            {'label': SubResultType.MEASURE_TYPE.value, 'value': SubResultType.MEASURE_TYPE.name},
            {'label': SubResultType.BERM_WIDENING.value, 'value': SubResultType.BERM_WIDENING.name},
            {'label': SubResultType.CREST_HIGHTENING.value, 'value': SubResultType.CREST_HIGHTENING.name},
        ]
        value = SubResultType.MEASURE_TYPE.name
    else:
        options, value = [], None

    return options, value


@app.callback(
    Output(EDITABLE_TRAJECT_TABLE_ID, "data"),
    Input('stored-data', 'data'),
)
def fill_traject_table_from_database(dike_traject_data: dict) -> list[dict]:
    """
    This is a callback to fill the editable table with the data from the database for the selected database.

    :param selection_traject_name:
    :return:
    """
    if dike_traject_data is not None:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)

        data = []
        for section in _dike_traject.dike_sections:
            data.append({"section_col": section.name, "reinforcement_col": "yes",
                         'measure_col': Measures.GROUND_IMPROVEMENT.name, 'reference_year_col': '2045'})

        return data
