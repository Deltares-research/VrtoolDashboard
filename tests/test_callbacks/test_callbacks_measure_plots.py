import json
from pathlib import Path
from contextvars import copy_context

import pytest
from plotly.graph_objs import Figure

from src.callbacks.traject_page.callbacks_tab_content import make_graph_measure_results_comparison
from src.constants import Mechanism


class TestCallbackMeasurePlot():

    # Mechanism.SECTION.name
    @pytest.mark.parametrize("mechanism", [
        Mechanism.SECTION.name,
        Mechanism.PIPING.name,
        Mechanism.STABILITY.name,
        Mechanism.OVERFLOW.name
    ])
    def test_make_graph_pf_vs_cost_callback(self, mechanism):
        # 1. Define data
        _dike_data = json.load(
            open(
                Path(__file__).parent.parent
                / "data/Case_38_1_sterker_VZG2/reference"
                / "dike_data.json"
            )
        )

        _path_config = Path(__file__).parent.parent / 'data/TestCase1_38-1_no_housing_testingonly' / 'vr_config.json'

        # load json:
        with open(_path_config, 'r') as f:
            decoded = f.read()
            _vr_config = json.loads(decoded)

        # 2. Define callback
        def run_callback():
            return make_graph_measure_results_comparison(
                _dike_data, _vr_config, 2025, "1A", mechanism
            )

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, Figure)
