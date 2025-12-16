import base64
import json
from contextvars import copy_context
from pathlib import Path

import pytest
from dash import dcc
from plotly.graph_objs import Figure

from src.callbacks.project_page.callback_create_projects import (
    update_map_project_definition_page,
)
from src.constants import ProgramDefinitionMapType


class TestCallbackCreateProjects:

    @pytest.mark.parametrize(
        "map_type",
        [
            ProgramDefinitionMapType.SIMPLE.name,
            ProgramDefinitionMapType.PROJECTS.name,
            ProgramDefinitionMapType.ASSESSMENT_PROBABILITIES.name,
            ProgramDefinitionMapType.VEILIGHEIDSRENDEMENT_INDEX.name,
        ],
    )
    def test_update_map_project_definition_page(self, map_type):
        # 1. Define data
        _data = json.load(
            open(
                Path(__file__).parent.parent.joinpath(
                    "data", "programmering_WDOD", "Programmering WDOD.json"
                )
            )
        )

        _imported_runs_data = _data["imported_runs_data"]
        _projects_overview_data = _data["project_data"]
        _dummy = "tab1234"
        _selected_sections = [
            "1|10-3",
            "2|10-3",
            "3|10-3",
            "4|10-3",
            "5|10-3",
            "7|10-3",
            "6|10-3",
            "9|10-3",
            "10|10-3",
            "11|10-3",
            "12|10-3",
            "13|10-3",
            "14|10-3",
            "15|10-3",
            "16|10-3",
            "17|10-3",
            "18|10-3",
            "19|10-3",
            "20|10-3",
        ]

        # 2. Define callback
        def run_callback():
            return update_map_project_definition_page(
                _dummy,
                _selected_sections,
                map_type,
                _imported_runs_data,
                _projects_overview_data,
            )

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, Figure)
