import base64
import json
from contextvars import copy_context
from pathlib import Path

import pytest
from dash import html, dcc
from plotly.graph_objs import Figure

from src.callbacks.traject_page.callbacks_tab_content import (
    make_graph_measure_results_comparison,
    make_graph_overview_dike,
    make_graph_map_initial_assessment,
    make_graph_map_measures,
    make_graph_pf_vs_cost,
    make_graph_map_urgency,
    update_click,
)
from src.constants import (
    CalcType,
    ColorBarResultType,
    Mechanism,
    SubResultType,
    ResultType,
)


class TestCallbackTabContent:

    @pytest.mark.skip(reason="Avoid overcharging MapBox licence")
    def test_make_graph_overview_dike_callback(self):
        # 1. Define data
        _dike_data = json.load(
            open(
                Path(__file__).parent.parent
                / "data/Case_38_1_sterker_VZG2/reference"
                / "dike_data.json"
            )
        )

        # 2. Define callback
        def run_callback():
            return make_graph_overview_dike(_dike_data)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, dcc.Graph)

    @pytest.mark.skip(reason="Avoid overcharging MapBox licence")
    def test_make_graph_initial_assessment_callback(self):
        # 1. Define data
        _dike_data = json.load(
            open(
                Path(__file__).parent.parent
                / "data/Case_38_1_sterker_VZG2/reference"
                / "dike_data.json"
            )
        )

        # 2. Define callback
        def run_callback():
            return make_graph_map_initial_assessment(
                _dike_data, 2025, ResultType.RELIABILITY.name, Mechanism.SECTION.name
            )

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, dcc.Graph)

    @pytest.mark.skip(reason="Avoid overcharging MapBox licence")
    def test_make_graph_map_measures_callback(self):
        # 1. Define data
        _dike_data = json.load(
            open(
                Path(__file__).parent.parent
                / "data/Case_38_1_sterker_VZG2/reference"
                / "dike_data.json"
            )
        )

        # 2. Define callback
        def run_callback():
            return make_graph_map_measures(
                _dike_data,
                2025,
                ResultType.RELIABILITY.name,
                CalcType.VEILIGHEIDSRENDEMENT.name,
                ColorBarResultType.RELIABILITY.name,
                Mechanism.SECTION.name,
                SubResultType.ABSOLUTE.name,
            )

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, dcc.Graph)

    def test_make_graph_pf_vs_cost_callback(self):
        # 1. Define data
        _dike_data = json.load(
            open(
                Path(__file__).parent.parent
                / "data/Case_38_1_sterker_VZG2/reference"
                / "dike_data.json"
            )
        )

        # 2. Define callback
        def run_callback():
            return make_graph_pf_vs_cost(
                _dike_data, 2025, ResultType.RELIABILITY.name, "COST"
            )

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, Figure)

    @pytest.mark.skip(reason="Avoid overcharging MapBox licence")
    def test_make_graph_map_urgency(self):
        # 1. Define data
        _dike_data = json.load(
            open(
                Path(__file__).parent.parent
                / "data/Case_38_1_sterker_VZG2/reference"
                / "dike_data.json"
            )
        )

        # 2. Define callback
        def run_callback():
            return make_graph_map_urgency(
                _dike_data, 2025, 10, CalcType.VEILIGHEIDSRENDEMENT.name
            )

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, dcc.Graph)

    @pytest.mark.skip(
        reason="FIx this test when the full database integration is completed"
    )
    def test_update_click(self):
        # 1. Define data
        _dike_data = json.load(
            open(
                Path(__file__).parent.parent
                / "data/Case_38_1_sterker_VZG2/reference"
                / "dike_data.json"
            )
        )
        _click_data = {
            "points": [
                {
                    "curveNumber": 1,
                    "pointNumber": 40,
                    "pointIndex": 40,
                    "x": 103.3,
                    "y": 3.5,
                    "customdata": "33A",
                    "bbox": {"x0": 1194.28, "x1": 1200.28, "y0": 462.52, "y1": 468.52},
                }
            ]
        }

        # 2. Define callback
        def run_callback():
            return update_click(_dike_data, _click_data)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, Figure)

    def test_make_graph_measure_results_comparison(self):
        # 1. Define data
        _dike_data = json.load(
            open(
                Path(__file__).parent.parent / "data/Case_38_1/reference" / "data.json"
            )
        )
        _path_config = (
            Path(__file__).parent.parent / "data/Case_38_1" / "config.json"
        )

        # load json:
        with open(_path_config, "r") as f:
            decoded = f.read()
            _vr_config = json.loads(decoded)

        _vr_config["input_directory"] = (
            Path(__file__).parent.parent / "data/Case_38_1"
        )

        # 2. Define callback
        def run_callback():
            return make_graph_measure_results_comparison(
                _dike_data, _vr_config, 2025, "37B", Mechanism.SECTION.name
            )

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, Figure)
