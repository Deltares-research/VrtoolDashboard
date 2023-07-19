
from contextvars import copy_context

import pytest
from dash import html

from src.callbacks.traject_page.callback_tabs_switch import render_tab_map_content


class TestCallbackTabSwitch:

    # parametrize:
    @pytest.mark.parametrize("tab_id", ["tab-1", "tab-2", "tab-3", "tab-4", "tab-5"])
    def test_render_tab_map_content(self, tab_id: str):
        # 1. Call
        def run_callback():
            return render_tab_map_content(tab_id)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 2. Assert
        assert isinstance(output, tuple)
        assert isinstance(output[0], html.Div)
        assert isinstance(output[1], list)


