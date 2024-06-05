# 1. Get VrConfig from stored_config
import json
from pathlib import Path

from vrtool.api import ApiRunWorkflows
from vrtool.common.enums import MechanismEnum
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.orm_controllers import clear_assessment_results, clear_measure_results, clear_optimization_results, \
    open_database

from src.callbacks.database_interaction_page.callback_optimize import get_selected_measure
from src.orm.import_database import get_name_optimization_runs
from tests.test_callbacks.test_callback_optimize import optimization_table_1, optimization_table_2
from src.orm import models as orm_model


def custom_selected_measure(_vr_config: VrtoolConfig) -> list[tuple]:
    _path_dir = Path(_vr_config.input_directory)
    _path_database = _path_dir.joinpath(_vr_config.input_database_name)

    open_database(_path_database)

    _selected_optimization_measure = orm_model.OptimizationSelectedMeasure.select()
    _meas_list = []
    for meas in _selected_optimization_measure:
        if meas.optimization_run_id == 1:
            _meas_list.append((meas.measure_result_id, meas.investment_year))

    return _meas_list

### Load data
# _path_config = Path(r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\TestCase1_38-1_no_housing_testingonly/vr_config.json")
_path_config = Path(r"C:\Users\hauth\OneDrive - Stichting Deltares\Documents\tempo\VRM\test_run_optimize/config38.json")

# load json:
with open(_path_config, 'r') as f:
    decoded = f.read()
    vr_config = json.loads(decoded)

traject_optimization_table = optimization_table_2
optimization_run_name = 'test_optimization_run11111'

### run_optimize_algorithm

_vr_config = VrtoolConfig()
_vr_config.traject = vr_config['traject']
_vr_config.input_directory = Path(vr_config['input_directory'])
_vr_config.output_directory = Path(vr_config['output_directory'])
_vr_config.input_database_name = vr_config['input_database_name']
_vr_config.excluded_mechanisms = [MechanismEnum.REVETMENT, MechanismEnum.HYDRAULIC_STRUCTURES]

# 2. Get all selected measures ids from optimization table in the dashboard
selected_measures = get_selected_measure(_vr_config, traject_optimization_table)
print(len(selected_measures), selected_measures)
# stop
selected_measures2 = custom_selected_measure(_vr_config)
print(len(selected_measures2), selected_measures2)


# 3. Run optimization
api = ApiRunWorkflows(_vr_config)
# clear_assessment_results(_vr_config)
# clear_measure_results(_vr_config)
# clear_optimization_results(_vr_config)

# api.run_all()

api.run_optimization(optimization_run_name, selected_measures)
#
# 4. Update the selection Dropwdown with all the names of the optimization runs
# _names_optimization_run = get_name_optimization_runs(_vr_config)
# _options = [{"label": name, "value": name} for name in _names_optimization_run]