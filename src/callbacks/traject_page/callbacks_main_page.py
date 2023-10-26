import base64
import json
from pathlib import Path
from dash import html, dcc, Output, Input, State
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.orm_controllers import open_database

from src.constants import ColorBarResultType, SubResultType, Measures
from src.linear_objects.dike_traject import DikeTraject

from src.app import app
from src.orm.import_database import get_dike_traject_from_ORM

import base64
import json

from src.orm.importers.dike_traject_importer import DikeTrajectImporter
from src.orm import models as orm_model


@app.callback([Output('dummy_upload_id', 'children'),
               Output("upload-toast", "is_open"), ],
              [Input('upload-data-zip', 'contents')],
              [State('upload-data-zip', 'filename')])
def upload_and_save_traject_input(contents: str, filename: str, dbc=None) -> tuple:
    """This is the callback for the upload of the zip files of the traject data.

    :param contents: string content of the uploaded zip file. The zip should content at least:
        - a geojson file with the dike data
        - a csv file with the results of the Veiligheidrendement method.

    :param filename: name of the uploaded zip file.

    :return: Return a tuple with:
        - html.Div with the serialized dike traject data.
        - boolean indicating if the upload was successful.
    """
    if contents is not None:

        try:

            content_type, content_string = contents.split(',')

            decoded = base64.b64decode(content_string)
            json_content = json.loads(decoded)

            vr_config = VrtoolConfig()
            vr_config.traject = json_content['traject']
            vr_config.input_directory = json_content['input_directory']
            vr_config.input_database_name = json_content['input_database_name']
            vr_config.excluded_mechanisms = json_content['excluded_mechanisms']

            _path_dir = Path(vr_config.input_directory)
            _path_database = _path_dir.joinpath(vr_config.input_database_name)

            open_database(_path_database)

            _dike_traject = DikeTrajectImporter(path_dir=_path_dir, traject_name=vr_config.traject).import_orm(
                orm_model)
            print(_dike_traject)

            return html.Div(
                dcc.Store(id='stored-data', data=_dike_traject.serialize())), True
        except:
            return html.Div("Geen bestand geüpload"), False
    else:
        return html.Div("Geen bestand geüpload"), False


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
    Output("editable_traject_table", "data"),
    Input('selection_traject_name', 'value'),
)
def fill_traject_table_from_database(selection_traject_name: str) -> list[dict]:
    """
    This is a callback to fill the editable table with the data from the database for the selected database.

    :param selection_traject_name:
    :return:
    """

    if selection_traject_name is not None:
        _traject_db = get_dike_traject_from_ORM(selection_traject_name)

        data = []
        for section in _traject_db.dike_sections:
            data.append({"section_col": section.name, "reinforcement_col": "yes",
                         'measure_col': Measures.GROUND_IMPROVEMENT.name, 'reference_year_col': '2045'})

        return data
