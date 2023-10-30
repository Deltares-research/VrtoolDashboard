from contextvars import copy_context
from pathlib import Path

import pytest
import json

from vrtool.defaults.vrtool_config import VrtoolConfig

from src.callbacks.traject_page.callback_optimize import run_optimize_algorithm
from src.callbacks.traject_page.callbacks_main_page import toggle_collapse, toggle_collapse2, toggle_collapse3, \
    update_radio_sub_result_type, fill_traject_table_from_database
from src.constants import ColorBarResultType


class TestCallbackOptimize:
    def test_run_optimize_algorithm(self):
        """
        Test if the callback filling the DataTable with the selected traject from the database returns a list.
        :return:
        """
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))
        _path_config = Path(__file__).parent.parent / 'data/TestCase1_38-1_no_housing' / 'vr_config.json'

        # load json:
        with open(_path_config, 'r') as f:
            decoded = f.read()
            _vr_config = json.loads(decoded)

        def run_callback():
            return run_optimize_algorithm(n_clicks=1, stored_data=_dike_data, vr_config=_vr_config)

        ctx = copy_context()
        output = ctx.run(run_callback)

        assert isinstance(output, dict)
