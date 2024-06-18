from contextvars import copy_context
from pathlib import Path

import pytest
import json

from src.callbacks.traject_page.callbacks_main_page import toggle_collapse, toggle_collapse2, toggle_collapse3, \
    update_radio_sub_result_type, fill_traject_table_from_database, update_slider_years_from_database
from src.constants import ColorBarResultType


class TestCallback:

    def test_toggle_collapse(self):
        def run_callback():
            return toggle_collapse(1, True)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 2. Assert

        assert isinstance(output, bool)
        assert output == False

    def test_toggle_collapse2(self):
        def run_callback():
            return toggle_collapse2(1, True)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 2. Assert

        assert isinstance(output, bool)

    def test_toggle_collapse3(self):
        def run_callback():
            return toggle_collapse3(1, True)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 2. Assert

        assert isinstance(output, tuple)
        assert isinstance(output[0], bool)

    @pytest.mark.parametrize("result_type", [ColorBarResultType.RELIABILITY, ColorBarResultType.COST])
    def test_update_radio_sub_result_type(self, result_type: ColorBarResultType):
        def run_callback():
            return update_radio_sub_result_type(result_type.name)

        ctx = copy_context()
        output = ctx.run(run_callback)

        assert isinstance(output, tuple)
        assert isinstance(output[0], list)
        assert isinstance(output[1], str)

    def test_fill_traject_table_from_database(self):
        """
        Test if the callback filling the DataTable with the selected traject from the database returns a list.
        :return:
        """
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/31-1 base coastal case/reference' / 'dike_data.json'))

        def run_callback():
            return fill_traject_table_from_database(_dike_data)

        ctx = copy_context()
        output = ctx.run(run_callback)

        assert isinstance(output, list)

    def test_update_slider_years_from_database(self):
        """
        Test if the callback filling the slider with the years from the database returns a dictionary.
        :return:
        """

        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/31-1 base coastal case/reference' / 'dike_data.json'))

        def run_callback():
            return update_slider_years_from_database(_dike_data)

        ctx = copy_context()
        output = ctx.run(run_callback)

        assert isinstance(output, dict)
        assert 2025 in output.keys()
        assert output[2025] == {'label': '2025'}
