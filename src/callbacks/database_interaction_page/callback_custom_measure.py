import base64
import io
import json
import logging
import shutil
from pathlib import Path

import dash
import pandas as pd
from dash import callback, Input, Output, State
from vrtool.common.enums import MechanismEnum, CombinableTypeEnum
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.orm_controllers import add_custom_measures, safe_clear_custom_measure
from vrtool.vrtool_logger import VrToolLogger

from src.component_ids import EDITABLE_CUSTOM_MEASURE_TABLE_ID, ADD_CUSTOM_MEASURE_BUTTON_ID, STORE_CONFIG, \
    CUSTOM_MEASURE_MODEL_ID, CLOSE_CUSTOM_MEAS_MODAL_BUTTON_ID, MESSAGE_MODAL_CUSTOM_MEASURE_ID, \
    REMOVE_CUSTOM_MEASURE_BUTTON_ID, IMPORTER_CUSTOM_MEASURE_CSV_ID
from src.constants import Mechanism
from src.layouts.layout_database_interaction.layout_custom_measures_table import columns_defs
from src.linear_objects.dike_traject import DikeTraject
from src.orm.import_database import get_all_custom_measures
from src.utils.utils import get_vr_config_from_dict


@callback(
    Output(CUSTOM_MEASURE_MODEL_ID, "is_open", allow_duplicate=True),
    Output(MESSAGE_MODAL_CUSTOM_MEASURE_ID, "children"),
    Output(EDITABLE_CUSTOM_MEASURE_TABLE_ID, "rowData", allow_duplicate=True),
    [Input(IMPORTER_CUSTOM_MEASURE_CSV_ID, 'contents')],
    State(STORE_CONFIG, "data"),
    State("stored-data", "data"),
    allow_duplicate=True,
    prevent_initial_call=True,
)
def upload_csv_and_add_measure(contents: str, vr_config: dict, dike_traject_data: dict) -> tuple[bool, list[str], list[dict]]:
    # 1. Get VrConfig from stored_config
    _vr_config = get_vr_config_from_dict(vr_config)

    # 2. Get custom measures from the table
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')

        # Try tab-separated first
        try:
            df = pd.read_csv(io.StringIO(decoded), sep='\t')
        except Exception as e:
            return f"Error parsing file: {e}"

        # Convert to list of lists (including headers)
        row_data = [df.columns.tolist()] + df.values.tolist()
        custom_measure_list_1 = convert_custom_table_to_input(row_data)


        # 3. Create a copy of the database for backup
        def get_next_backup_filename(dir: Path):
            version = 1
            while True:
                if version == 1:
                    version_str = "original"
                else:
                    version_str = f"v{version}"
                backup_file_path = dir.joinpath(f"{_vr_config.input_database_name}_backup_{version_str}.db")
                if not backup_file_path.exists():
                    return backup_file_path
                version += 1

        source_db = _vr_config.input_directory / _vr_config.input_database_name
        target_backup_db = get_next_backup_filename(_vr_config.input_directory)

        shutil.copy2(source_db, target_backup_db)
        _vr_config.input_database_name = f"{_vr_config.input_database_name}"

        # 4. Add custom measures to the initial database, backup is left untouched.
        class ModalPopupLogHandler(logging.StreamHandler):
            """
            Custom handler declared within this method so it is aware of the provided context
            and able to trigger the `set_progress` method whilst running in the background.
            """

            def __enter__(self):
                """
                This is required for the `with` statement that allows disposal of the object.
                """
                # Add this handler to the VrToolLogger to trace the messages
                # of the given logging level.
                VrToolLogger.add_handler(self, logging.INFO)
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                """
                We are only interested into closing the handler stream.
                This needs to be done here explicitely.
                """
                self.close()

            def emit(self, record):
                return self.format(record)

        with ModalPopupLogHandler() as handler:
            _added_measures = add_custom_measures(
                _vr_config, custom_measure_list_1
            )

        # %. Update table on the right side displaying ALL custom measures
        _vr_config = get_vr_config_from_dict(vr_config)

        custom_measures = get_all_custom_measures(_vr_config)

        df = pd.DataFrame(columns=[col["field"] for col in columns_defs], data=custom_measures)

        new_columns_defs = columns_defs.copy()
        new_columns_defs[1]["cellEditorParams"]["values"] = [section.name for section in
                                                             DikeTraject.deserialize(dike_traject_data).dike_sections]

        return True, ["Custom measures added successfully."], df.to_dict('records')
    return dash.no_update, dash.no_update, dash.no_update


@callback(
    Output(EDITABLE_CUSTOM_MEASURE_TABLE_ID, "rowData", allow_duplicate=True),

    Input(REMOVE_CUSTOM_MEASURE_BUTTON_ID, "n_clicks"),
    State(STORE_CONFIG, "data"),
    prevent_initial_call=True

)
def remove_all_custom_measure_in_db(n_clicks, vr_config: dict):
    """
    Apply the safe_clear_custom_measure function to remove all custom measures from the database which do not have
    OptimizeRun associated with them.
    :param n_clicks:
    :param vr_config:
    :return:
    """
    _vr_config = get_vr_config_from_dict(vr_config)
    safe_clear_custom_measure(_vr_config)
    custom_measures = get_all_custom_measures(_vr_config)

    df = pd.DataFrame(columns=[col["field"] for col in columns_defs], data=custom_measures)

    return df.to_dict('records')


def convert_custom_table_to_input(row_data: list) -> list[dict]:
    """
    This function converts the csv custom measure table into a list ready to be used as input for the VrTool API.
    :param row_data:
    :return:
    """
    converted_input = []
    for row in row_data[1:]:
        splitted_row = row[0].split(',')

        if len(splitted_row) != 6:
            raise ValueError(f"Row {row} does not have 6 columns, found {len(splitted_row)} columns.")

        # Convert into mechanism enum of VRTool
        if splitted_row[2] == Mechanism.STABILITY.value:
            _mechanism = MechanismEnum.STABILITY_INNER.name
        elif splitted_row[2] == Mechanism.PIPING.value:
            _mechanism = MechanismEnum.PIPING.name
        elif splitted_row[2] == Mechanism.OVERFLOW.value:
            _mechanism = MechanismEnum.OVERFLOW.name
        elif splitted_row[2] == Mechanism.REVETMENT.value:
            _mechanism = MechanismEnum.REVETMENT.name
        else:
            raise ValueError(f"Mechanism {row['mechanism']} is not recognized")

        converted_row = {
            "MEASURE_NAME": splitted_row[0],
            "COMBINABLE_TYPE": CombinableTypeEnum.FULL.name,
            "SECTION_NAME": splitted_row[1],
            "MECHANISM_NAME": _mechanism,
            "TIME": float(splitted_row[3]),
            "COST": float(splitted_row[4]),
            "BETA": float(splitted_row[5]),
        }
        converted_input.append(converted_row)
    return converted_input


@callback(
    Output(EDITABLE_CUSTOM_MEASURE_TABLE_ID, "rowData"),
    Output(EDITABLE_CUSTOM_MEASURE_TABLE_ID, "columnDefs"),
    Input(STORE_CONFIG, 'data'),
    Input("stored-data", "data")
)
def fill_custom_measures_table_from_database(vr_config: dict, dike_traject_data: dict) -> list[dict, dict]:
    """
    Fill the custom measure table with all the custom measure present in the database.
    :return:
    """
    _vr_config = get_vr_config_from_dict(vr_config)

    custom_measures = get_all_custom_measures(_vr_config)

    df = pd.DataFrame(columns=[col["field"] for col in columns_defs], data=custom_measures)

    new_columns_defs = columns_defs.copy()
    new_columns_defs[1]["cellEditorParams"]["values"] = [section.name for section in
                                                         DikeTraject.deserialize(dike_traject_data).dike_sections]

    return df.to_dict('records'), new_columns_defs


@callback(Output(CUSTOM_MEASURE_MODEL_ID, "is_open", allow_duplicate=True),
          Input(CLOSE_CUSTOM_MEAS_MODAL_BUTTON_ID, "n_clicks"),
          prevent_initial_call=True)  # Close the modal
def close_custom_measure_modal(n_clicks):
    return False
