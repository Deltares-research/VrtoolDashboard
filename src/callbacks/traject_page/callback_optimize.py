import logging

from pathlib import Path

import dash
from dash import Output, Input, html
from vrtool.api import ApiRunWorkflows
from vrtool.common.enums import MechanismEnum
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.vrtool_logger import VrToolLogger

from src.app import app
from src.component_ids import (
    OPTIMIZE_BUTTON_ID,
    STORE_CONFIG,
    DUMMY_OPTIMIZE_BUTTON_OUTPUT_ID,
    NAME_NEW_OPTIMIZATION_RUN_ID,
    EDITABLE_TRAJECT_TABLE_ID,
    DROPDOWN_SELECTION_RUN_ID,
    OPTIMIZE_MODAL_ID,
    CLOSE_OPTIMAL_MODAL_BUTTON_ID,
)
from src.constants import REFERENCE_YEAR, Measures
from src.orm.import_database import (
    get_measure_result_ids_per_section,
    get_name_optimization_runs,
    get_all_default_selected_measure,
)


@app.callback(
    output=[Output(component_id="latest-timestamp", component_property="children")],
    inputs=[Input("interval-component", "n_intervals")],
    cancel=[Input(CLOSE_OPTIMAL_MODAL_BUTTON_ID, "n_clicks")],
    prevent_initial_call=True,
)
def update_timestamp(interval):
    _path_log = Path().joinpath("vrtool_dashboard.log")
    with open(_path_log, "r") as f:
        # Read the last line of the log
        _latest_log = f.readlines()[-1]

    return [html.Span(f"{_latest_log}")]


@app.callback(
    output=[Output(OPTIMIZE_MODAL_ID, "is_open", allow_duplicate=True)],
    inputs=[
        Input(OPTIMIZE_BUTTON_ID, "n_clicks"),
        Input(CLOSE_OPTIMAL_MODAL_BUTTON_ID, "n_clicks"),
    ],
    prevent_initial_call=True,
)
def open_canvas_logging_and_cancel(
    optimize_n_click: int, close_n_click: int
) -> tuple[bool]:
    """
    Dummy call to trigger the opening of the canvas so the `update_timestamp`
    can output the vrtool logging.
    """
    if close_n_click and close_n_click > 0:
        return [False]
    return [True]


@app.callback(
    output=[
        Output(DUMMY_OPTIMIZE_BUTTON_OUTPUT_ID, "children"),
        Output(DROPDOWN_SELECTION_RUN_ID, "options", allow_duplicate=True),
        Output(OPTIMIZE_MODAL_ID, "is_open", allow_duplicate=True),
    ],
    inputs=[
        Input(OPTIMIZE_BUTTON_ID, "n_clicks"),
        Input(NAME_NEW_OPTIMIZATION_RUN_ID, "value"),
        Input("stored-data", "data"),
        Input(STORE_CONFIG, "data"),
        Input(EDITABLE_TRAJECT_TABLE_ID, "rowData"),
    ],
    background=True,
    cancel=[Input(CLOSE_OPTIMAL_MODAL_BUTTON_ID, "n_clicks")],
    prevent_initial_call=True,
)
def run_optimize_algorithm(
    n_clicks: int,
    optimization_run_name: str,
    stored_data: dict,
    vr_config: dict,
    traject_optimization_table: list[dict],
) -> tuple:
    """
    This is a callback to run the optimization algorithm when the user clicks on the "Optimaliseer" button.

    :param n_clicks: dummy input to trigger the callback upon clicking.
    :param optimization_run_name: name of the optimization run.
    :param stored_data: data from the database.
    :param vr_config: serialized VrConfig object.
    :param traject_optimization_table: data from the optimization table on the dashboard.

    :return:
    """

    if stored_data is None:
        return dash.no_update

    elif n_clicks is None:
        return dash.no_update
    elif n_clicks == 0:
        return dash.no_update

    elif traject_optimization_table == []:
        return dash.no_update

    else:
        # 1. Get VrConfig from stored_config
        _vr_config = VrtoolConfig()
        _vr_config.traject = vr_config["traject"]
        _vr_config.input_directory = Path(vr_config["input_directory"])
        _vr_config.output_directory = Path(vr_config["output_directory"])
        _vr_config.input_database_name = vr_config["input_database_name"]
        _vr_config.excluded_mechanisms = [MechanismEnum.HYDRAULIC_STRUCTURES]

        # 2. Get all selected measures ids from optimization table in the dashboard
        selected_measures = get_selected_measure(_vr_config, traject_optimization_table)

        # 3. Run optimization in a separate thread, so that the user can continue using the app while the optimization
        # is running.
        _path_log = Path().joinpath("vrtool_dashboard.log")
        VrToolLogger.init_file_handler(_path_log, logging.INFO)
        run_vrtool_optimization(_vr_config, optimization_run_name, selected_measures)

        # 4. Update the selection Dropwdown with all the names of the optimization runs
        _names_optimization_run = get_name_optimization_runs(_vr_config)
        _options = [{"label": name, "value": name} for name in _names_optimization_run]

        return [], _options, False


def run_vrtool_optimization(
    _vr_config: VrtoolConfig, optimization_run_name: str, selected_measures: list[tuple]
):
    """Runs the optimization algorithm in a separate thread of the VRTool core"""

    api = ApiRunWorkflows(_vr_config)
    api.run_optimization(optimization_run_name, selected_measures)


def get_selected_measure(
    vr_config: VrtoolConfig, dike_traject_table: list
) -> list[tuple[int, int]]:
    """Returns the input selected measures for the optimization algorithm as a list of tuples
    (measure_result_id, investment_year).

    :param vr_config: VrConfig object.
    :param dike_traject_table: list of dictionaries containing the data from the editable traject table.

    :return: list of tuples (measure_result_id, investment_year).

    """
    if dike_traject_table is None:
        raise NotImplementedError()
    else:

        list_selected_measures = []
        for section_row in dike_traject_table:
            _investment_year = int(section_row["reference_year"]) - REFERENCE_YEAR

            # if the section is not reinforced, don't add the corresponding MeasureResult for the optimization
            if section_row["reinforcement_col"] == "no":
                continue
            for measure in Measures:
                _measure_result_ids = get_measure_result_ids_per_section(
                    vr_config, section_row["section_col"], measure.name
                )

                for measure_result_id in _measure_result_ids:
                    list_selected_measures.append((measure_result_id, _investment_year))

        return list_selected_measures
