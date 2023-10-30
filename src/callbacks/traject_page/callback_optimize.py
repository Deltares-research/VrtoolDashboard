from pathlib import Path

import dash
from dash import Output, Input, State
from vrtool.api import ApiRunWorkflows
from vrtool.common.enums import MechanismEnum
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.orm_controllers import export_results_optimization

from src.app import app
from src.component_ids import OPTIMIZE_BUTTON_ID, STORE_CONFIG, DUMMY_OPTIMIZE_BUTTON_OUTPUT_ID


@app.callback(
    Output(DUMMY_OPTIMIZE_BUTTON_OUTPUT_ID, 'children'),
    [
        Input(OPTIMIZE_BUTTON_ID, "n_clicks"),
        Input("stored-data", "data"),
        Input(STORE_CONFIG, "data")
    ],
    prevent_initial_call=True
)
def run_optimize_algorithm(n_clicks: int, stored_data: dict, vr_config: dict) -> dict:
    """
    This is a callback to run the optimization algorithm when the user clicks on the "Optimaliseer" button.

    :param n_clicks: dummy input to trigger the callback upon clicking.
    :param stored_data: data from the database.
    :param vr_config: serialized VrConfig object.

    :return:
    """
    print(n_clicks)

    if stored_data is None:
        return dash.no_update

    elif n_clicks is None:
        return dash.no_update
    elif n_clicks == 0:
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
        selected_measures = get_selected_measure(None)

        # 3. Run optimization
        api = ApiRunWorkflows(_vr_config)
        # clear_optimization_results(_vr_config)
        print('Lets-gooooo')

        results_optimization = api.run_optimization(selected_measures)
        export_results_optimization(results_optimization, [1 * n_clicks, 2 * n_clicks])
        print("finitooooo")

        # # 4. Parse the modified db and replace stored-data
        # _dike_traject = get_dike_traject_from_config_ORM(_vr_config, run_id_dsn=2*n_clicks, run_is_vr=1*n_clicks)
        #
        # return _dike_traject.serialize()


def get_selected_measure(dike_traject_table: list) -> list[tuple[int, int]]:
    if dike_traject_table is None:
        selected_measure_ids = [(i, 0) for i in range(1, 1631)]
        return selected_measure_ids
    else:
        return []
