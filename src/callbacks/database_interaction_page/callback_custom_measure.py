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
    REMOVE_CUSTOM_MEASURE_BUTTON_ID
from src.constants import Mechanism
from src.layouts.layout_database_interaction.layout_custom_measures_table import columns_defs
from src.orm.import_database import get_all_custom_measures
from src.utils.utils import get_vr_config_from_dict


@callback(
    Output(EDITABLE_CUSTOM_MEASURE_TABLE_ID, "rowTransaction"),
    Input("add-row-button", "n_clicks"),
    prevent_initial_call=True,
)
def update_rowdata(_):
    return {
        "addIndex": 0,
        "add": [{}]
    }


@callback(
    Output(EDITABLE_CUSTOM_MEASURE_TABLE_ID, "rowData", allow_duplicate=True),
    Input("copy-row-button", "n_clicks"),
    State(EDITABLE_CUSTOM_MEASURE_TABLE_ID, 'selectedRows'),
    State(EDITABLE_CUSTOM_MEASURE_TABLE_ID, 'rowData'),
    prevent_initial_call=True,
)
def copy_row(n_click, selected_row, row_data):
    if n_click is not None and selected_row:
        row_data.append(selected_row[0])

        return row_data
    return dash.no_update


@callback(
    Output(EDITABLE_CUSTOM_MEASURE_TABLE_ID, "rowData", allow_duplicate=True),
    Input("delete-row-button", "n_clicks"),
    State(EDITABLE_CUSTOM_MEASURE_TABLE_ID, 'selectedRows'),
    State(EDITABLE_CUSTOM_MEASURE_TABLE_ID, 'rowData'),
    prevent_initial_call=True,
)
def delete_row(n_click, selected_row, row_data):
    for row in row_data:
        if row == selected_row[0]:
            row_data.remove(row)
            return row_data

    return dash.no_update


@callback(
    Output(CUSTOM_MEASURE_MODEL_ID, "is_open", allow_duplicate=True),
    Output(MESSAGE_MODAL_CUSTOM_MEASURE_ID, "children"),
    Input(ADD_CUSTOM_MEASURE_BUTTON_ID, "n_clicks"),
    State(EDITABLE_CUSTOM_MEASURE_TABLE_ID, "rowData"),
    State(STORE_CONFIG, "data"),
    prevent_initial_call=True,

)
def add_custom_measure_to_db(n_clicks: int, row_data: list[dict], vr_config: dict):
    """
    Add custom measures to the database.
    When a custom measure is added, the original database is copied and a backup is created with a different name
    "vrtool_input_backup.db" and the new database which contains custom measures is named "vrtool_input.db".
    :param n_clicks:
    :param row_data:
    :param vr_config:
    :return:
    """
    if n_clicks:

        # 1. Get VrConfig from stored_config
        _vr_config = get_vr_config_from_dict(vr_config)

        # 2. Get custom measures from the table
        custom_measure_list_1 = convert_custom_table_to_input(row_data)

        # 3. Create a copy of the database for backup
        def get_next_backup_filename(dir: Path):
            version = 1
            while True:
                if version == 1:
                    version_str = "original"
                else:
                    version_str = f"v{version}"
                backup_file_path = dir.joinpath(f"vrtool_input_backup_{version_str}.db")
                if not backup_file_path.exists():
                    return backup_file_path
                version += 1

        source_db = _vr_config.input_directory / _vr_config.input_database_name
        target_backup_db = get_next_backup_filename(_vr_config.input_directory)

        shutil.copy2(source_db, target_backup_db)
        _vr_config.input_database_name = "vrtool_input.db"

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

        return True, ["Custom measures added successfully."]
    return False, [""]


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


def convert_custom_table_to_input(row_data: list[dict]) -> list[dict]:
    """
    This function converts the custom measure table to the input format for the add_custom_measures function.
    :param row_data:
    :return:
    """
    converted_input = []
    for row in row_data:
        if row == {}:
            continue

        # Convert into mechanism enum of VRTool
        if row["mechanism"] == Mechanism.STABILITY.value:
            _mechanism = MechanismEnum.STABILITY_INNER.name
        elif row["mechanism"] == Mechanism.PIPING.value:
            _mechanism = MechanismEnum.PIPING.name
        elif row["mechanism"] == Mechanism.OVERFLOW.value:
            _mechanism = MechanismEnum.OVERFLOW.name
        elif row["mechanism"] == Mechanism.REVETMENT.value:
            _mechanism = MechanismEnum.REVETMENT.name
        else:
            raise ValueError(f"Mechanism {row['mechanism']} is not recognized")

        converted_row = {
            "MEASURE_NAME": row["measure_name"],
            "COMBINABLE_TYPE": CombinableTypeEnum.FULL.name,
            "SECTION_NAME": row["section_name"],
            "MECHANISM_NAME": _mechanism,
            "TIME": float(row["time"]),
            "COST": float(row["cost"]),
            "BETA": float(row["beta"]),
        }
        converted_input.append(converted_row)

    return converted_input


@callback(
    Output(EDITABLE_CUSTOM_MEASURE_TABLE_ID, "rowData"),
    Input(STORE_CONFIG, 'data'),
)
def fill_custom_measures_table_from_database(vr_config: dict) -> list[dict]:
    """
    Fill the custom measure table with all the custom measure present in the database.
    :return:
    """
    _vr_config = get_vr_config_from_dict(vr_config)

    custom_measures = get_all_custom_measures(_vr_config)

    df = pd.DataFrame(columns=[col["field"] for col in columns_defs], data=custom_measures)

    return df.to_dict('records')


@callback(Output(CUSTOM_MEASURE_MODEL_ID, "is_open", allow_duplicate=True),
          Input(CLOSE_CUSTOM_MEAS_MODAL_BUTTON_ID, "n_clicks"),
          prevent_initial_call=True)  # Close the modal
def close_custom_measure_modal(n_clicks):
    return False
