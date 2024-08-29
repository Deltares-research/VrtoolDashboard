import json
from enum import Enum
from pathlib import Path

import pytest
from plotly.graph_objs import Figure

from src.constants import get_mapbox_token
from src.linear_objects.project import get_projects_from_saved_data
from src.plotly_graphs.project_page.plotly_maps import plot_project_overview_map


class TestPlotlyScatterMapBoxProjectPage():

    def test_plot_default_overview_map_dummy(self):
        # 1. Define data
        _imported_runs_data = json.load(
            open(Path(__file__).parent.parent.joinpath("data", "imported_runs_data.json")))
        _projects_overview_data = json.load(
            open(Path(__file__).parent.parent.joinpath("data", "projects_overview_data.json")))

        _projects = get_projects_from_saved_data(_imported_runs_data, _projects_overview_data)


        # 2. Call
        _fig = plot_project_overview_map(_projects)


        # only for testing TO BE REMOVED?COMMENTED OUT
        _fig.update_layout(mapbox={"accesstoken": get_mapbox_token()})
        _fig.show()

        # 3. Assert
        assert isinstance(_fig, Figure)


