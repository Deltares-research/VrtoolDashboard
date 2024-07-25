import json
from pathlib import Path
from contextvars import copy_context

import pytest
from plotly.graph_objs import Figure

from src.callbacks.traject_page.callbacks_tab_content import make_graph_measure_results_comparison, \
    open_modal_measure_reliability_time
from src.constants import Mechanism

click_data_measure_point = {'points': [
    {'curveNumber': 0, 'pointNumber': 39, 'pointIndex': 39, 'x': 4.450367300925011, 'y': 3.5090082684574213,
     'bbox': {'x0': 1041.3600000000001, 'x1': 1049.3600000000001, 'y0': 685.4300000000001, 'y1': 693.4300000000001},
     'customdata': ['Grondversterking binnenwaarts', 30, 2, 40]}]}

click_data_optimization_point = {'points': [
    {'curveNumber': 3, 'pointNumber': 0, 'pointIndex': 0, 'x': 1.5615053647848525, 'y': 4.113965013046284,
     'customdata': '9 + 45', 'bbox': {'x0': 871.8, 'x1': 879.8, 'y0': 509.27, 'y1': 517.27}}]}


class TestCallbackMeasurePlot():

    # Mechanism.SECTION.name
    @pytest.mark.parametrize("mechanism", [
        Mechanism.SECTION.name,
        Mechanism.PIPING.name,
        Mechanism.STABILITY.name,
        Mechanism.OVERFLOW.name,
        Mechanism.REVETMENT.name
    ])
    def test_make_graph_measure_results_comparison_callback(self, mechanism):
        # 1. Define data
        _dike_data = json.load(
            open(
                Path(__file__).parent.parent
                / "data/31-1 base coastal case/reference"
                / "dike_data.json"
            )
        )

        _path_config = Path(__file__).parent.parent / 'data/31-1 base coastal case' / 'config.json'

        # load json:
        with open(_path_config, 'r') as f:
            decoded = f.read()
            _vr_config = json.loads(decoded)

        _vr_config["input_directory"] = Path(__file__).parent.parent / 'data/31-1 base coastal case'

        # 2. Define callback
        def run_callback():
            return make_graph_measure_results_comparison(
                _dike_data, _vr_config, 2025, "WsNoo_Stab_011600_012000", mechanism,
            )

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, Figure)

    @pytest.mark.parametrize("click_data", [
        click_data_measure_point,
        click_data_optimization_point
    ])
    def test_open_modal_measure_reliability_time(self, click_data):
        _dike_traject_data = json.load(
            open(
                Path(__file__).parent.parent
                / "data/31-1 base coastal case/reference"
                / "dike_data.json"
            )
        )

        _path_config = Path(__file__).parent.parent / 'data/31-1 base coastal case' / 'config.json'

        # load json:
        with open(_path_config, 'r') as f:
            decoded = f.read()
            _vr_config = json.loads(decoded)

        _path_figure_dict = Path(__file__).parent.parent / 'data/31-1 base coastal case/reference' / 'figure.json'
        with open(_path_figure_dict, 'r') as f:
            decoded = f.read()
            _figure_dict = json.loads(decoded)

        _vr_config["input_directory"] = Path(__file__).parent.parent / 'data/31-1 base coastal case'

        # 2. Define callback
        def run_callback():
            # click_data: dict, selected_mechanism, vr_config, dike_traject_data: dict,
            # section_name: str, fig: dict

            return open_modal_measure_reliability_time(
                click_data, Mechanism.SECTION.name, _vr_config, _dike_traject_data, "WsNoo_Stab_011600_012000",
                _figure_dict
            )

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, tuple)
