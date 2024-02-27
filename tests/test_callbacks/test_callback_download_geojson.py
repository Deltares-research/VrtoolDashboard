import json
from contextvars import copy_context
from pathlib import Path

import pytest
from dash import dcc

from src.callbacks.traject_page.callback_download_geojson import download_assessment_geojson, download_overview_geojson
from src.callbacks.traject_page.callbacks_tab_content import make_graph_overview_dike


class TestCallbackDownloadGeojson:

    def test_download_overview_geojson(self):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))

        # 2. Define callback
        def run_callback():
            return download_overview_geojson(_dike_data, 2)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, dict)

    def test_download_assessment_geojson(self):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/Case_38_1_sterker_VZG2/reference' / 'dike_data.json'))

        # 2. Define callback
        def run_callback():
            return download_assessment_geojson(_dike_data, 2045, 2)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, dict)
