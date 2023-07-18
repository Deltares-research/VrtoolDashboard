import base64
import json
from contextvars import copy_context
from pathlib import Path

import pytest
from dash import html, dcc
from plotly.graph_objs import Figure

from src.callbacks.callbacks_main_page import upload_and_save_traject_input, make_graph_overview_dike, \
    make_graph_map_initial_assessment, make_graph_map_measures, make_graph_pf_vs_cost, make_graph_map_urgency, \
    update_click, render_tab_map_content, toggle_collapse, toggle_collapse3, toggle_collapse2, \
    update_radio_sub_result_type
from src.constants import CalcType, ColorBarResultType, Mechanism, SubResultType, ResultType


class TestCallback:
    def test_upload_and_save_traject_input_callback(self):
        # 1. Define data
        zip_path = Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2' / '38_1_VZG2.zip'
        with open(zip_path, 'rb') as file:
            binary_content = file.read()
        content = "data:application/x-zip-compressed;base64," + base64.b64encode(binary_content).decode('utf-8')

        # 2. Define callback
        def run_callback():
            return upload_and_save_traject_input(content, '38_1_all.zip')

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, tuple)
        assert isinstance(output[0], html.Div)
        assert isinstance(output[1], bool)

    @pytest.mark.skip(reason="Avoid overcharging MapBox licence")
    def test_make_graph_overview_dike_callback(self):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))

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
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))

        # 2. Define callback
        def run_callback():
            return make_graph_map_initial_assessment(_dike_data,
                                                     2025,
                                                     ResultType.RELIABILITY.name,
                                                     Mechanism.SECTION.name)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, dcc.Graph)

    @pytest.mark.skip(reason="Avoid overcharging MapBox licence")
    def test_make_graph_map_measures_callback(self):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))

        # 2. Define callback
        def run_callback():
            return make_graph_map_measures(_dike_data,
                                           2025,
                                           ResultType.RELIABILITY.name,
                                           CalcType.VEILIGHEIDRENDEMENT.name,
                                           ColorBarResultType.RELIABILITY.name,
                                           Mechanism.SECTION.name,
                                           SubResultType.ABSOLUTE.name)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, dcc.Graph)

    @pytest.mark.skip(reason="Avoid overcharging MapBox licence")
    def test_make_graph_pf_vs_cost_callback(self):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))

        # 2. Define callback
        def run_callback():
            return make_graph_pf_vs_cost(_dike_data,
                                         2025,
                                         ResultType.RELIABILITY.name,
                                         "COST"
                                         )

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, Figure)

    @pytest.mark.skip(reason="Avoid overcharging MapBox licence")
    def test_make_graph_map_urgency(self):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))

        # 2. Define callback
        def run_callback():
            return make_graph_map_urgency(_dike_data, 2025, 10, CalcType.VEILIGHEIDRENDEMENT.name)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, dcc.Graph)

    def test_update_click(self):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))
        _click_data = {'points': [
            {'curveNumber': 1, 'pointNumber': 40, 'pointIndex': 40, 'x': 103.3, 'y': 3.5, 'customdata': '33A',
             'bbox': {'x0': 1194.28, 'x1': 1200.28, 'y0': 462.52, 'y1': 468.52}}]}

        # 2. Define callback
        def run_callback():
            return update_click(_dike_data, _click_data)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, Figure)

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
