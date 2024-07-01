import shutil
from pathlib import Path

import dash
from dash import callback, Input, Output, State
from vrtool.common.enums import MechanismEnum, CombinableTypeEnum
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.orm_controllers import add_custom_measures

from src.component_ids import EDITABLE_CUSTOM_MEASURE_TABLE_ID, ADD_CUSTOM_MEASURE_BUTTON_ID, STORE_CONFIG
from src.constants import Mechanism


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
    Input(ADD_CUSTOM_MEASURE_BUTTON_ID, "n_clicks"),
    State(EDITABLE_CUSTOM_MEASURE_TABLE_ID, "rowData"),
    State(STORE_CONFIG, "data"),
    prevent_initial_call=True,

)
def add_custom_measure_to_db(n_clicks: int, row_data: list[dict], vr_config: dict):
    if n_clicks:

        # 1. Get VrConfig from stored_config
        _vr_config = VrtoolConfig()
        _vr_config.traject = vr_config["traject"]
        _vr_config.input_directory = Path(vr_config["input_directory"])
        _vr_config.output_directory = Path(vr_config["output_directory"])
        _vr_config.input_database_name = vr_config["input_database_name"]

        for meca in MechanismEnum:
            if meca.name in vr_config["excluded_mechanisms"]:
                _vr_config.excluded_mechanisms.append(meca)

        # 2. Get custom measures from the table
        custom_measure_list_1 = convert_custom_table_to_input(row_data)

        # 3. Create a copy of the database
        source_db = _vr_config.input_directory / _vr_config.input_database_name
        target_db = _vr_config.input_directory / "vrtool_input_modified.db"
        shutil.copy2(source_db, target_db)
        _vr_config.input_database_name = "vrtool_input_modified.db"

        # 4. Add custom measures to the modified database, the initial remains intact
        _added_measures = add_custom_measures(
            _vr_config, custom_measure_list_1
        )


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
