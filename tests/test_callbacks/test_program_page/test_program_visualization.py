import json
from contextvars import copy_context
from pathlib import Path

from plotly.graph_objs import Figure

from src.callbacks.project_page.callback_tabs_switch_project_page import (
    update_project_page_visualization,
)
from src.constants import ResultType
from src.linear_objects.reinforcement_program import (
    DikeProgram,
    get_projects_from_saved_data,
)
from src.plotly_graphs.project_page.plotly_plots import (
    plot_cost_vs_time_projects,
    projects_reliability_over_time,
)


class TestCallbackProgramPageVisualization:

    def test_update_project_page_visualization(self):
        # 1. Define data
        _data = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "programmering_WDOD", "Programmering WDOD.json"
                )
            )
        )

        _imported_runs_data = _data["imported_runs_data"]
        _projects_overview_data = _data["project_data"]

        # 2. Define callback
        def run_callback():
            return update_project_page_visualization(
                "tab-112",
                ResultType.PROBABILITY.name,
                _imported_runs_data,
                _projects_overview_data,
            )

        ctx = copy_context()
        # output = ctx.run(run_callback)
        cost_fig, reliability_fig, map_fig, project_overview_table, cost, risk_table = (
            ctx.run(run_callback)
        )

        # 3. Assert
        assert isinstance(cost_fig, Figure)
        assert isinstance(reliability_fig, Figure)
        assert isinstance(map_fig, Figure)
        assert isinstance(project_overview_table, list)
        assert isinstance(cost, str)
        assert isinstance(risk_table, list)

    def test_plot_projects_reliability_over_time_figure_reliability(self):
        # 1. Define data
        # 1. Define data
        _data = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "programmering_WDOD", "Programmering WDOD.json"
                )
            )
        )

        _imported_runs_data = _data["imported_runs_data"]
        _projects_overview_data = _data["project_data"]
        program = DikeProgram(_imported_runs_data, _projects_overview_data)

        # 2. Call
        _fig = projects_reliability_over_time(program, ResultType.RELIABILITY.name)

        # 3. Assert
        assert isinstance(_fig, Figure)

    def test_plot_projects_reliability_over_time_figure_risk(self):
        # 1. Define data
        _data = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "programmering_WDOD", "Programmering WDOD.json"
                )
            )
        )

        _imported_runs_data = _data["imported_runs_data"]
        _projects_overview_data = _data["project_data"]

        program = DikeProgram(_imported_runs_data, _projects_overview_data)

        # 2. Call
        _fig = projects_reliability_over_time(program, ResultType.RISK.name)

        # 3. Assert
        assert isinstance(_fig, Figure)

    def test_plot_projects_reliability_over_time_figure_risk_factor(self):
        # 1. Define data
        _data = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "programmering_WDOD", "Programmering WDOD.json"
                )
            )
        )

        _imported_runs_data = _data["imported_runs_data"]
        _projects_overview_data = _data["project_data"]
        program = DikeProgram(_imported_runs_data, _projects_overview_data)

        # 2. Call
        _fig = projects_reliability_over_time(program, ResultType.RISK_FACTOR.name)

        # 3. Assert
        assert isinstance(_fig, Figure)

    def test_plot_projects_cost_over_time(self):
        # 1. Define data
        _data = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "programmering_WDOD", "Programmering WDOD.json"
                )
            )
        )

        _imported_runs_data = _data["imported_runs_data"]
        _projects_overview_data = _data["project_data"]

        _projects, _ = get_projects_from_saved_data(
            _imported_runs_data, _projects_overview_data
        )

        # 2. Call
        _fig = plot_cost_vs_time_projects(_projects)

        # 3. Assert
        assert isinstance(_fig, Figure)
