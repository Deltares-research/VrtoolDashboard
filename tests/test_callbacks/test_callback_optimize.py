from contextvars import copy_context
from pathlib import Path

import pytest
import json

from vrtool.defaults.vrtool_config import VrtoolConfig

from src.callbacks.traject_page.callback_optimize import run_optimize_algorithm
from src.callbacks.traject_page.callbacks_main_page import toggle_collapse, toggle_collapse2, toggle_collapse3, \
    update_radio_sub_result_type, fill_traject_table_from_database
from src.constants import ColorBarResultType

optimization_table_1 = [{'section_col': '1A', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
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
                        {'section_col': '34', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2045'},
                        {'section_col': '37B', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2045'},
                        {'section_col': '40', 'reinforcement_col': 'yes', 'measure_col': 'GROUND_IMPROVEMENT',
                         'reference_year_col': '2045'},
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

    # @pytest.mark.skip(reason="slow")
    @pytest.mark.slow
    def test_run_optimize_algorithm(self):
        """
        Test if the callback filling the DataTable with the selected traject from the database returns a list.
        :return:
        """
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))
        # _path_config = Path(__file__).parent.parent / 'data/TestCase1_38-1_no_housing_test' / 'vr_config.json'
        _path_config = Path(
            r'C:\Users\hauth\OneDrive - Stichting Deltares\Documents\tempo\vr_run_optimize\vr_config.json')

        # load json:
        with open(_path_config, 'r') as f:
            decoded = f.read()
            _vr_config = json.loads(decoded)

        def run_callback():
            return run_optimize_algorithm(n_clicks=1,
                                          stored_data=_dike_data,
                                          vr_config=_vr_config,
                                          traject_optimization_table=optimization_table_1,
                                          run_name='test_run',
                                          )

        ctx = copy_context()
        output = ctx.run(run_callback)
