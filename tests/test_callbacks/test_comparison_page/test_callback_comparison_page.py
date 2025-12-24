import base64
import json
from contextvars import copy_context
from pathlib import Path

import pytest
from dash import dcc
from plotly.graph_objs import Figure

from src.callbacks.comparison_page.callback_tabs_output_switch import (
    make_graph_overview_comparison,
    make_graph_pf_project_comparison,
    make_graph_pf_time_comparison,
    make_map_comparison_measure,
    update_table_comparison_measures,
    update_table_comparison_order_measures,
)
from src.constants import ResultType


class TestCallbackComparisonPage:

    def test_make_graph_overview_comparison(self):
        # 1. Define data
        _data_base = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_base.json"
                )
            )
        )
        _data_omega = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_omega.json"
                )
            )
        )
        _data_omega_45 = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_omega_45.json"
                )
            )
        )

        _imported_runs = {
            "10-1|Basisberekening": _data_base,
            "10-1|Omega": _data_omega,
            "10-1|Omega_45": _data_omega_45,
        }

        # 2. Define callback
        def run_callback():
            return make_graph_overview_comparison(_imported_runs)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, dcc.Graph)

    def test_make_graph_pf_project_comparison(self):
        # 1. Define data
        _data_base = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_base.json"
                )
            )
        )
        _data_omega = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_omega.json"
                )
            )
        )
        _data_omega_45 = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_omega_45.json"
                )
            )
        )

        _imported_runs = {
            "10-1|Basisberekening": _data_base,
            "10-1|Omega": _data_omega,
            "10-1|Omega_45": _data_omega_45,
        }

        # 2. Define callback
        def run_callback():
            return make_graph_pf_project_comparison(
                _imported_runs, 0, ResultType.RELIABILITY.name, "COST"
            )

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, Figure)

    def test_make_graph_pf_time_comparison(self):
        # 1. Define data
        _data_base = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_base.json"
                )
            )
        )
        _data_omega = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_omega.json"
                )
            )
        )
        _data_omega_45 = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_omega_45.json"
                )
            )
        )

        _imported_runs = {
            "10-1|Basisberekening": _data_base,
            "10-1|Omega": _data_omega,
            "10-1|Omega_45": _data_omega_45,
        }

        # 2. Define callback
        def run_callback():
            return make_graph_pf_time_comparison(_imported_runs)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, Figure)

    def test_make_map_comparison_measure(self):
        # 1. Define data
        _data_base = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_base.json"
                )
            )
        )
        _data_omega = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_omega.json"
                )
            )
        )
        _data_omega_45 = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_omega_45.json"
                )
            )
        )

        _imported_runs = {
            "10-1|Basisberekening": _data_base,
            "10-1|Omega": _data_omega,
            "10-1|Omega_45": _data_omega_45,
        }

        _table_data = [
            {"traject": "10-1", "run_name": "Basisberekening_base", "active": True},
            {"traject": "10-1", "run_name": "Basisberekening_omega", "active": True},
        ]

        # 2. Define callback
        def run_callback():
            return make_map_comparison_measure(_imported_runs, _table_data, None)

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, Figure)

    def test_update_table_comparison_measures(self):
        # 1. Define data
        _data_base = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_base.json"
                )
            )
        )
        _data_omega = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_omega.json"
                )
            )
        )
        _data_omega_45 = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_omega_45.json"
                )
            )
        )

        _imported_runs = {
            "10-1|Basisberekening": _data_base,
            "10-1|Omega": _data_omega,
            "10-1|Omega_45": _data_omega_45,
        }

        _table_data = [
            {"traject": "10-1", "run_name": "Basisberekening_base", "active": True},
            {"traject": "10-1", "run_name": "Basisberekening_omega", "active": True},
        ]

        # 2. Define callback
        def run_callback():
            return update_table_comparison_measures(
                _imported_runs, _table_data, dummy={}
            )

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, tuple)

    def test_update_table_comparison_order_measures(self):
        # 1. Define data
        _data_base = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_base.json"
                )
            )
        )
        _data_omega = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_omega.json"
                )
            )
        )
        _data_omega_45 = json.load(
            open(
                Path(__file__).parent.parent.parent.joinpath(
                    "data", "10-1", "dike_traject_10-1_Basisberekening_omega_45.json"
                )
            )
        )

        _imported_runs = {
            "10-1|Basisberekening": _data_base,
            "10-1|Omega": _data_omega,
            "10-1|Omega_45": _data_omega_45,
        }

        _table_data = [
            {"traject": "10-1", "run_name": "Basisberekening_base", "active": True},
            {"traject": "10-1", "run_name": "Basisberekening_omega", "active": True},
        ]

        # 2. Define callback
        def run_callback():
            return update_table_comparison_order_measures(
                _imported_runs, _table_data, dummy={}
            )

        ctx = copy_context()
        output = ctx.run(run_callback)

        # 3. Assert
        assert isinstance(output, tuple)
