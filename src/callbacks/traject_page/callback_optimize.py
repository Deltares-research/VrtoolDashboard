from pathlib import Path

import dash
from dash import Output, Input, State
from dash.long_callback import DiskcacheLongCallbackManager
from vrtool.api import ApiRunWorkflows
from vrtool.common.enums import MechanismEnum
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.orm_controllers import export_results_optimization, clear_optimization_results, open_database

from src.app import app, background_callback_manager
from src.component_ids import OPTIMIZE_BUTTON_ID, STORE_CONFIG, DUMMY_OPTIMIZE_BUTTON_OUTPUT_ID, \
    EDITABLE_TRAJECT_TABLE_ID, DROPDOWN_SELECTION_RUN_ID, NAME_NEW_OPTIMIZATION_RUN_ID
    EDITABLE_TRAJECT_TABLE_ID, DROPDOWN_SELECTION_RUN_ID, OPTIMIZATION_NEW_RUN_NAME_ID
from src.constants import REFERENCE_YEAR
from src.orm.import_database import get_dike_traject_from_config_ORM, get_measure_result_ids_per_section, \
    get_name_optimization_runs, get_all_default_selected_measure




@app.callback(
    output=[Output(DUMMY_OPTIMIZE_BUTTON_OUTPUT_ID, 'children'),
            Output(DROPDOWN_SELECTION_RUN_ID, "options", allow_duplicate=True)
            ],
    inputs=[
        Input(OPTIMIZE_BUTTON_ID, "n_clicks"),
        Input(NAME_NEW_OPTIMIZATION_RUN_ID, "value"),
        Input("stored-data", "data"),
        Input(STORE_CONFIG, "data"),
        Input(EDITABLE_TRAJECT_TABLE_ID, "data"),
    ],
    prevent_initial_call=True,
    background=True,
    manager=background_callback_manager,
    running=[
        (Output(OPTIMIZE_BUTTON_ID, 'disabled'), True, False),
    ],

)
def run_optimize_algorithm(n_clicks: int, optimization_run_name: str, stored_data: dict, vr_config: dict,
                           traject_optimization_table: list[dict]) -> tuple:
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
        _vr_config.traject = vr_config['traject']
        _vr_config.input_directory = Path(vr_config['input_directory'])
        _vr_config.output_directory = Path(vr_config['output_directory'])
        _vr_config.input_database_name = vr_config['input_database_name']
        _vr_config.excluded_mechanisms = [MechanismEnum.REVETMENT, MechanismEnum.HYDRAULIC_STRUCTURES]

        # 2. Get all selected measures ids from optimization table in the dashboard
        selected_measures = get_selected_measure(_vr_config, traject_optimization_table)
        selected_measures = get_all_default_selected_measure(_vr_config)

        # 3. Run optimization
        api = ApiRunWorkflows(_vr_config)
        api.run_optimization(optimization_run_name, selected_measures)

        # 4. Update the selection Dropwdown with all the names of the optimization runs
        _names_optimization_run = get_name_optimization_runs(_vr_config)
        _options = [{"label": name, "value": name} for name in _names_optimization_run]

        return [], _options


def get_selected_measure(vr_config: VrtoolConfig, dike_traject_table: list) -> list[tuple[int, int]]:
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

            # if the section is not reinforced, don't add the corresponding MeasureResult for the optimization
            if section_row['reinforcement_col'] == 'no':
                continue

            measure_result_ids = get_measure_result_ids_per_section(vr_config, section_row["section_col"],
                                                                    section_row["measure_col"])

            _investment_year = int(section_row['reference_year_col']) - REFERENCE_YEAR

            for measure_result_id in measure_result_ids:
                list_selected_measures.append((measure_result_id, _investment_year))

        return list_selected_measures

