import base64
import json
from contextvars import copy_context
from pathlib import Path

from dash import html, dcc

from src.index import upload_and_save_traject_input, make_graph_overview_dike


class TestCallback:
    def test_upload_and_save_traject_input_callback(self):
        # 1. Define data
        zip_path = Path(__file__).parent.parent / 'data/TestCase1_38-1_no_housing' / '38_1_all.zip'
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
        _dike_data = json.load(open(Path(__file__).parent.parent / 'data/TestCase1_38-1_no_housing/reference' / 'dike_38_1_data.json'))

        # 2. Define callback
        def run_callback():
            return make_graph_overview_dike(_dike_data)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, dcc.Graph)



