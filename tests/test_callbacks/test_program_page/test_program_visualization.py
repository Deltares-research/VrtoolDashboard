import json
from contextvars import copy_context
from pathlib import Path

from plotly.graph_objs import Figure

from src.callbacks.project_page.callback_tabs_switch_project_page import update_project_page_visualization
from src.constants import ResultType


class TestCallbackProgramPageVisualization:

    def test_update_project_page_visualization(self):
        # 1. Define data
        _data = json.load(
            open(Path(__file__).parent.parent.parent.joinpath("data", "programmering_WDOD", "Programmering WDOD.json"))
        )

        _imported_runs_data = _data['imported_runs_data']
        _projects_overview_data = _data['project_data']


        # 2. Define callback
        def run_callback():
            return update_project_page_visualization("tab-112", ResultType.PROBABILITY.name, _imported_runs_data,
                                                      _projects_overview_data)

        ctx = copy_context()
        # output = ctx.run(run_callback)
        cost_fig, reliability_fig, map_fig, project_overview_table, cost, damage, risk = ctx.run(run_callback)


        # 3. Assert
        assert isinstance(cost_fig, Figure)
        assert isinstance(reliability_fig, Figure)
        assert isinstance(map_fig, Figure)
        assert isinstance(project_overview_table, list)
        assert isinstance(cost, str)
        assert isinstance(damage, str)
        assert isinstance(risk, str)