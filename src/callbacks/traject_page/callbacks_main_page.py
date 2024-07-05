from pathlib import Path

import dash
from dash import html, dcc, Output, Input, State, callback
import dash_bootstrap_components as dbc
from vrtool.common.enums import MechanismEnum
from vrtool.defaults.vrtool_config import VrtoolConfig
import pandas as pd

from src.component_ids import STORE_CONFIG, DROPDOWN_SELECTION_RUN_ID, EDITABLE_TRAJECT_TABLE_ID, \
    SLIDER_YEAR_RELIABILITY_RESULTS_ID, GREEDY_OPTIMIZATION_CRITERIA_BETA, GREEDY_OPTIMIZATION_CRITERIA_YEAR, \
    BUTTON_RECOMPUTE_GREEDY_STEPS, BUTTON_RECOMPUTE_GREEDY_STEPS_NB_CLICKS, SELECT_GREEDY_OPTIMIZATION_STOP_CRITERIA
from src.constants import ColorBarResultType, SubResultType, Measures, REFERENCE_YEAR
from src.linear_objects.dike_traject import DikeTraject

import base64
import json

from src.orm.import_database import get_dike_traject_from_config_ORM, get_name_optimization_runs, \
    get_run_optimization_ids


@callback([Output('dummy_upload_id', 'children'),
           Output("upload-toast", "is_open"),
           Output(STORE_CONFIG, "data"),
           Output(DROPDOWN_SELECTION_RUN_ID, "value"),
           Output(DROPDOWN_SELECTION_RUN_ID, "options"),
           ],
          [Input('upload-data-config-json', 'contents')],
          [State('upload-data-config-json', 'filename')],
          allow_duplicate=True,
          prevent_initial_call=True,
          )
def upload_and_save_traject_input(contents: str, filename: str) -> tuple:
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

            content_type, content_string = contents.split(',')

            decoded = base64.b64decode(content_string)
            json_content = json.loads(decoded)
            _mandatory_config_args = ['traject', 'input_directory', 'input_database_name', 'excluded_mechanisms']
            for _arg in _mandatory_config_args:
                if _arg not in json_content.keys():
                    _alert = dbc.Alert(f"Config.json file is missing argument <{_arg}>", dismissable=True, id='123456',
                                       color="danger")

                    return _alert, False, {}, "", []

            vr_config = VrtoolConfig()
            vr_config.traject = json_content['traject']
            vr_config.input_directory = json_content['input_directory']
            vr_config.input_database_name = json_content['input_database_name']
            vr_config.excluded_mechanisms = json_content['excluded_mechanisms']
            vr_config.T = vr_config["T"]

            # _dike_traject = get_dike_traject_from_config_ORM(vr_config, run_id_dsn=2, run_is_vr=1)
            _value_selection_run_dropwdown = "Basisberekening"

            # Update the selection Dropwdown with all the names of the optimization runs
            _names_optimization_run = get_name_optimization_runs(vr_config)
            _options = [{"label": name, "value": name} for name in _names_optimization_run]

            return html.Div(), True, json_content, _value_selection_run_dropwdown, _options,
        except:
            return html.Div("Geen bestand geüpload"), False, {}, "", []
    else:
        return html.Div("Geen bestand geüpload"), False, dash.no_update, "", []


@callback(
    Output('stored-data', 'data'),
    [Input(DROPDOWN_SELECTION_RUN_ID, "value")],
    State(STORE_CONFIG, "data"),
    prevent_initial_call=True,
)
def selection_traject_run(name: str, vr_config: dict) -> dict:
    """
    Callback to select the run id for the traject.

    :param name: name of the traject
    :param vr_config: dictionary with the configuration of the traject.
    :return: DikeTraject object
    """

    if vr_config is None or vr_config == {}:
        return dash.no_update

    _vr_config = VrtoolConfig()
    _vr_config.traject = vr_config['traject']
    _vr_config.input_directory = Path(vr_config['input_directory'])
    _vr_config.output_directory = Path(vr_config['output_directory'])
    _vr_config.input_database_name = vr_config['input_database_name']
    _vr_config.excluded_mechanisms = vr_config["excluded_mechanisms"]
    _vr_config.T = vr_config["T"]

    if name == '':
        return dash.no_update

    if name == "Basisberekening":
        _dike_traject = get_dike_traject_from_config_ORM(_vr_config, run_id_dsn=2, run_is_vr=1)

    elif name in get_name_optimization_runs(_vr_config):
        run_id_vr, run_id_dsn = get_run_optimization_ids(_vr_config, name)
        _dike_traject = get_dike_traject_from_config_ORM(_vr_config, run_id_dsn=run_id_dsn, run_is_vr=run_id_vr)
    else:
        raise ValueError("Name of the Optimization run is not correct.")

    _dike_traject.run_name = name
    return _dike_traject.serialize()


@callback(

    [Output('stored-data', 'data', allow_duplicate=True),
     Output(BUTTON_RECOMPUTE_GREEDY_STEPS_NB_CLICKS, 'value')],
    [
        Input(DROPDOWN_SELECTION_RUN_ID, "value"),
        Input(SELECT_GREEDY_OPTIMIZATION_STOP_CRITERIA, "value"),
        Input(GREEDY_OPTIMIZATION_CRITERIA_BETA, "value"),
        Input(GREEDY_OPTIMIZATION_CRITERIA_YEAR, "value"),
        Input(BUTTON_RECOMPUTE_GREEDY_STEPS, "n_clicks"),
        Input(BUTTON_RECOMPUTE_GREEDY_STEPS_NB_CLICKS, 'value')
    ],
    State(STORE_CONFIG, "data"),
    prevent_initial_call=True,

)
def recompute_dike_traject_with_new_greedy_criteria(name: str, name_type: str, beta: float, year: float, n_click: int,
                                                    store_n_click_button, vr_config) -> tuple[dict, int]:
    """
    Callback to recompute the dike traject with new greedy criteria.

    :param name: name of the calculation run in the database
    :param name_type: type of the greedy optimization criteria
    :param beta: value of the beta parameter for greedy optimization if criterion 'target_pf' is selected
    :param year: value of the year parameter for greedy optimization if criterion 'target_year' is selected
    :param n_click: number of clicks on the button
    :param store_n_click_button: number of clicks on the button, used to detect when the button is clicked
    :param vr_config: dictionary with the configuration of the traject.


    :return:
    """

    if n_click is None or store_n_click_button == n_click:  # update when clicking on button ONLY
        return dash.no_update

    if vr_config is None or vr_config == {}:
        return dash.no_update

    _vr_config = VrtoolConfig()
    _vr_config.traject = vr_config['traject']
    _vr_config.input_directory = Path(vr_config['input_directory'])
    _vr_config.output_directory = Path(vr_config['output_directory'])
    _vr_config.input_database_name = vr_config['input_database_name']
    _vr_config.excluded_mechanisms = vr_config["excluded_mechanisms"]
    _vr_config.T = vr_config["T"]



    if name == "Basisberekening":
        _dike_traject = get_dike_traject_from_config_ORM(_vr_config, run_id_dsn=2, run_is_vr=1,
                                                         greedy_optimization_criteria=name_type,
                                                         greedy_criteria_beta=beta, greedy_criteria_year=int(year))

    elif name in get_name_optimization_runs(_vr_config):
        run_id_vr, run_id_dsn = get_run_optimization_ids(_vr_config, name)
        _dike_traject = get_dike_traject_from_config_ORM(_vr_config, run_id_dsn=run_id_dsn, run_is_vr=run_id_vr,
                                                         greedy_optimization_criteria=name_type,
                                                         greedy_criteria_beta=beta, greedy_criteria_year=int(year))
    else:
        raise ValueError("Name of the Optimization run is not correct.")

    _dike_traject.run_name = name
    return _dike_traject.serialize(), n_click


@callback(
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


@callback(
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


@callback(
    Output("collapse_3", "is_open"),
    Output("left-column", 'md'),
    Output("right-column", 'md'),
    [Input("collapse_button_3", "n_clicks")],
    [State("collapse_3", "is_open")],
)
def toggle_collapse3(n: int, is_open: bool):
    """
    Callback to toggle the collapse of the second section.
    :param n: dummy integer
    :param is_open: boolean indicating if the collapse is open or not.
    :return:
    """
    if n:
        if n % 2 == 1:
            return True, 8, 4
        return False, 4, 8
    return is_open, 4, 8


@callback(
    [Output('select_sub_result_type_measure_map', 'options'),
     Output('select_sub_result_type_measure_map', 'value')],
    Input('select_measure_map_result_type', 'value'),
)
def update_radio_sub_result_type(result_type: str) -> tuple[list, str]:
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
            {'label': SubResultType.INVESTMENT_YEAR.value, 'value': SubResultType.INVESTMENT_YEAR.name},
        ]
        value = SubResultType.MEASURE_TYPE.name
    else:
        options, value = [], None

    return options, value


@callback(
    Output(EDITABLE_TRAJECT_TABLE_ID, "rowData"),
    Input('stored-data', 'data'),
)
def fill_traject_table_from_database(dike_traject_data: dict) -> list[dict]:
    """
    This is a callback to fill the editable table with the data from the database for the selected database.
    By default all toggle are set to True.
    :param dike_traject_data: the data of the dike traject

    :return:
    """

    df = pd.DataFrame(columns=["section_col", "reinforcement_col"])

    if dike_traject_data is not None:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)

        for section in _dike_traject.dike_sections:
            df_add = pd.DataFrame.from_records([{"section_col": section.name,
                            "reinforcement_col": True,
                            "reference_year": 2025,
                            Measures.GROUND_IMPROVEMENT.name: True,
                            Measures.GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN.name: True,
                            Measures.GEOTEXTILE.name: True,
                            Measures.DIAPHRAGM_WALL.name: True,
                            Measures.STABILITY_SCREEN.name: True,
                            }])
            df = pd.concat([df, df_add], ignore_index=True)

        bool_columns = ["reinforcement_col", Measures.GROUND_IMPROVEMENT.name,
                        Measures.GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN.name,
                        Measures.GEOTEXTILE.name, Measures.DIAPHRAGM_WALL.name,
                        Measures.STABILITY_SCREEN.name]
        df[bool_columns] = df[bool_columns].astype(bool)


        return df.to_dict('records')


@callback(
    Output(SLIDER_YEAR_RELIABILITY_RESULTS_ID, "marks"),
    Input('stored-data', 'data'),
)
def update_slider_years_from_database(dike_traject_data: dict):
    if dike_traject_data is None:
        marks = {
            2025: {'label': '2025'},
            2045: {'label': '2045'},
            2075: {'label': '2075'},
            2125: {'label': '2125'}
        }
        return marks
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        _assessment_years = _dike_traject.dike_sections[0].years  # all sections should have the same assessment years
        _marks = {year + REFERENCE_YEAR: {'label': f"{year + REFERENCE_YEAR}"} for year in _assessment_years}
        return _marks
