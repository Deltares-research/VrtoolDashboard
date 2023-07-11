import base64
import json
from contextvars import copy_context
from pathlib import Path

from dash import html, dcc

from src.callbacks.callbacks_main_page import upload_and_save_traject_input, make_graph_overview_dike, \
    make_graph_map_initial_assessment, make_graph_map_measures, make_graph_pf_vs_cost
from src.constants import CalcType, ColorBarResultType, Mechanism
from src.layouts.layout_main_page import ResultType


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

    def test_make_graph_overview_dike_callback(self):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))

        # 2. Define callback
        def run_callback():
            return make_graph_overview_dike(_dike_data, "VEILIGHEIDRENDEMENT")

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, dcc.Graph)

    def test_make_graph_initial_assessment_callback(self):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))

        # 2. Define callback
        def run_callback():
            return make_graph_map_initial_assessment(_dike_data, 2025, ResultType.RELIABILITY.name,
                                                     Mechanism.SECTION.name)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, dcc.Graph)

    def test_make_graph_map_measures_callback(self):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))

        # 2. Define callback
        def run_callback():
            return make_graph_map_measures(_dike_data, 2025, ResultType.RELIABILITY.name,
                                           CalcType.VEILIGHEIDRENDEMENT.name, ColorBarResultType.RELIABILITY.name,
                                           Mechanism.SECTION.name)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, dcc.Graph)

    def test_make_graph_pf_vs_cost_callback(self):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))

        # 2. Define callback
        def run_callback():
            return make_graph_pf_vs_cost(_dike_data, 2025, ResultType.RELIABILITY.name)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, dcc.Graph)
