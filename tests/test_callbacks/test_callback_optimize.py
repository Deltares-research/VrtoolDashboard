from contextvars import copy_context
from pathlib import Path

import pytest
import json

from src.callbacks.traject_page.callback_optimize import run_optimize_algorithm

optimization_table_1 = [{'section_col': '1A', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2025'},
                        {'section_col': '1B', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2025'},
                        {'section_col': '4', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2025'},
                        {'section_col': '12', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2025'},
                        {'section_col': '15', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2025'},
                        {'section_col': '33A', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2025'},
                        {'section_col': '34', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2025'},
                        {'section_col': '37B', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2025'},
                        {'section_col': '40', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2025'},
                        {'section_col': '50', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2045'}]

optimization_table_2 = [{'section_col': '1A', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2045'},
                        {'section_col': '1B', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2045'},
                        {'section_col': '4', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2045'},
                        {'section_col': '12', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2045'},
                        {'section_col': '15', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2045'},
                        {'section_col': '33A', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2045'},
                        {'section_col': '34', 'reinforcement_col': 'no', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2045'},
                        {'section_col': '37B', 'reinforcement_col': 'no', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2045'},
                        {'section_col': '40', 'reinforcement_col': 'no', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2045'},
                        {'section_col': '50', 'reinforcement_col': 'no', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2045'}]


class TestCallbackOptimize:

    @pytest.mark.skip(reason="can't test Background callback")
    @pytest.mark.slow
    def test_run_optimize_algorithm(self):
        """
        Test if the callback filling the DataTable with the selected traject from the database returns a list.
        :return:
        """
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))
        _path_config = Path(__file__).parent.parent / 'data/TestCase1_38-1_no_housing_testingonly' / 'vr_config.json'

        # load json:
        with open(_path_config, 'r') as f:
            decoded = f.read()
            _vr_config = json.loads(decoded)

        def run_callback():
            return run_optimize_algorithm(
                set_progress=None,
                n_clicks=1,
                optimization_run_name="nametest",
                stored_data=_dike_data,
                vr_config=_vr_config,
                traject_optimization_table=optimization_table_1,
            )

        ctx = copy_context()
        output = ctx.run(run_callback)
