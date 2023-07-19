from contextvars import copy_context

import pytest


from src.callbacks.traject_page.callbacks_main_page import toggle_collapse, toggle_collapse2, toggle_collapse3, \
    update_radio_sub_result_type
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

        assert isinstance(output, bool)

    @pytest.mark.parametrize("result_type", [ColorBarResultType.RELIABILITY, ColorBarResultType.COST])
    def test_update_radio_sub_result_type(self, result_type: ColorBarResultType):
        def run_callback():
            return update_radio_sub_result_type(result_type.name)

        ctx = copy_context()
        output = ctx.run(run_callback)

        assert isinstance(output, list)
