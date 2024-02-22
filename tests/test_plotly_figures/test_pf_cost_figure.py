import json
from enum import Enum
from pathlib import Path

import pytest
from plotly.graph_objs import Figure

from src.constants import ResultType
from src.linear_objects.dike_traject import DikeTraject
from src.plotly_graphs.pf_length_cost import plot_pf_length_cost


class TestPlotlyScatter:
    @pytest.mark.parametrize("result_type", [ResultType.RELIABILITY, ResultType.PROBABILITY])
    @pytest.mark.parametrize("cost_length_switch", ["COST", "LENGTH"])
    def test_plot_pf_length_cost_economic_optimum(self, result_type: Enum, cost_length_switch: str):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))
        _dike_traject = DikeTraject.deserialize(_dike_data)

        # 2. Call
        _fig = plot_pf_length_cost(_dike_traject, 2025, result_type.name, cost_length_switch)

        # 3. Assert
        assert isinstance(_fig, Figure)
