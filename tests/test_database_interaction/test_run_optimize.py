import json
import shutil
from pathlib import Path

from vrtool.common.enums import MechanismEnum
from vrtool.defaults.vrtool_config import VrtoolConfig

from src.callbacks.database_interaction_page.callback_optimize import get_selected_measure, run_vrtool_optimization
from tests import test_data
from tests.test_callbacks.test_callback_optimize import optimization_table_38_1, \
    optimization_table_31_1


class TestRunOptimize:

    def test_traject_optimization_table(self):
        traject_optimization_table = optimization_table_38_1

        row_1 = traject_optimization_table[0]
        expected_keys = ["section_col", 'reinforcement_col', 'reference_year', "GROUND_IMPROVEMENT",
                         "GROUND_IMPROVEMENT_WITH_STABILITY_SCREEN", "GEOTEXTILE", "DIAPHRAGM_WALL", "STABILITY_SCREEN"]
        assert isinstance(traject_optimization_table, list)
        assert isinstance(row_1, dict)
        assert all([key in row_1.keys() for key in expected_keys])
        assert all(
            [isinstance(row_1[key], bool) for key in expected_keys if key not in ["section_col", "reference_year"]])
        assert isinstance(row_1["section_col"], str)
        assert isinstance(row_1["reference_year"], int)

    def test_get_selected_measure(self):
        traject_optimization_table = optimization_table_38_1

        _test_input_directory = Path.joinpath(test_data, "38-1 base river case/config.json")

        # load json:
        with open(_test_input_directory, 'r') as f:
            decoded = f.read()
            vr_config = json.loads(decoded)

        _vr_config = VrtoolConfig()
        _vr_config.traject = vr_config['traject']
        _vr_config.input_directory = Path.joinpath(test_data, "38-1 base river case")

        _vr_config.output_directory = Path(vr_config['output_directory'])

        _vr_config.input_database_name = vr_config['input_database_name']
        _vr_config.excluded_mechanisms = [MechanismEnum.REVETMENT, MechanismEnum.HYDRAULIC_STRUCTURES]

        selected_measures = get_selected_measure(
            _vr_config, traject_optimization_table
        )
        print(traject_optimization_table)
        assert isinstance(selected_measures, list)

    def test_run_optimize_no_revetment(self):
        traject_optimization_table = optimization_table_38_1

        _test_input_directory = Path.joinpath(test_data, "38-1 base river case/config.json")

        # load json:
        with open(_test_input_directory, 'r') as f:
            decoded = f.read()
            vr_config = json.loads(decoded)

        _vr_config = VrtoolConfig()
        _vr_config.traject = vr_config['traject']
        _vr_config.input_directory = Path.joinpath(test_data, "38-1 base river case")
        _vr_config.output_directory = Path(vr_config['output_directory'])
        _vr_config.input_database_name = "copy_" + vr_config['input_database_name']

        # Create a copy of the database file:
        shutil.copyfile(Path.joinpath(_vr_config.input_directory, vr_config['input_database_name']),
                        Path.joinpath(_vr_config.input_directory, "copy_" + vr_config['input_database_name']))

        _vr_config.excluded_mechanisms = [MechanismEnum.REVETMENT, MechanismEnum.HYDRAULIC_STRUCTURES]

        selected_measures = get_selected_measure(
            _vr_config, traject_optimization_table
        )

        optimization_run_name = "test_optimization"

        run_vrtool_optimization(
            _vr_config, optimization_run_name, selected_measures
        )
        Path.joinpath(_vr_config.input_directory, "copy_" + vr_config['input_database_name']).unlink()

    def test_run_optimize_with_revetment(self):
        traject_optimization_table = optimization_table_31_1

        _test_input_directory = Path.joinpath(test_data, "31-1 base coastal case/config.json")

        # load json:
        with open(_test_input_directory, 'r') as f:
            decoded = f.read()
            vr_config = json.loads(decoded)

        _vr_config = VrtoolConfig()
        _vr_config.traject = vr_config['traject']
        _vr_config.input_directory = Path.joinpath(test_data, "31-1 base coastal case")
        _vr_config.output_directory = Path(vr_config['output_directory'])
        _vr_config.input_database_name = "copy_" + vr_config['input_database_name']

        # Create a copy of the database file:
        shutil.copyfile(Path.joinpath(_vr_config.input_directory, vr_config['input_database_name']),
                        Path.joinpath(_vr_config.input_directory, "copy_" + vr_config['input_database_name']))

        _vr_config.excluded_mechanisms = [MechanismEnum.HYDRAULIC_STRUCTURES]

        selected_measures = get_selected_measure(
            _vr_config, traject_optimization_table
        )

        optimization_run_name = "test_optimization"

        run_vrtool_optimization(
            _vr_config, optimization_run_name, selected_measures
        )
        Path.joinpath(_vr_config.input_directory, "copy_" + vr_config['input_database_name']).unlink()
