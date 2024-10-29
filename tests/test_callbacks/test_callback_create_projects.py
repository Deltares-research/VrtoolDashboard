import base64
import json
from contextvars import copy_context
from pathlib import Path

import pytest
from dash import dcc
from plotly.graph_objs import Figure

from src.callbacks.project_page.callback_create_projects import update_map_project_definition_page


class TestCallbackCreateProjects:

    def test_update_map_project_definition_page(self):
        # 1. Define data
        _dummy = "tab1234"
        _selected_sections = [
            "1|7-2",
            "3|7-2",
            "5|7-2",
            "6|7-2",
            "7|7-2",
            "8|7-2",
            "9|7-2",
            "10|7-2",
            "vak 01|24-3",
            "vak 02|24-3"
        ]

        _imported_runs_data = json.load(
            open(Path(__file__).parent.parent.joinpath("data", "imported_runs_data.json")))
        _projects_overview_data = json.load(
            open(Path(__file__).parent.parent.joinpath("data", "projects_overview_data_new.json")))

        # 2. Define callback
        def run_callback():
            return update_map_project_definition_page(_dummy, _selected_sections, _imported_runs_data,
                                                      _projects_overview_data)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, Figure)
