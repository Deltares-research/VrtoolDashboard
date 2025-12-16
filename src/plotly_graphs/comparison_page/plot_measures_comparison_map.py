import numpy as np
import plotly.graph_objects as go
from matplotlib import colors
from matplotlib import pyplot as plt

from src.constants import (
    REFERENCE_YEAR,
    CalcType,
    ColorBarResultType,
    Mechanism,
    ResultType,
    SubResultType,
)
from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject
from src.plotly_graphs.plotly_maps import (
    add_measure_type_trace,
    get_middle_point,
    place_legend_left_top_corner,
    place_legend_right_top_corner,
    update_layout_map_box,
)
from src.utils.gws_convertor import GWSRDConvertor
from src.utils.utils import beta_to_pf, get_beta, pf_to_beta, to_million_euros

color_dict = {""}


def plot_comparison_measures_map(
    imported_runs: dict, activated_runs: list[str]
) -> go.Figure:
    fig = go.Figure()

    for index, dike_traject in enumerate(activated_runs):
        # dike_traject = DikeTraject.deserialize(dike_traject_data)

        if index >= 2:  # only display the first two trajects
            break
        run_id = f"{dike_traject.name}|{dike_traject.run_name}"
        # if run_id not in activated_runs:
        #     continue

        _legend_display = {
            "ground_reinforcement": True,
            "VZG": True,
            "screen": True,
            "diaphram wall": True,
            "sheetpile": True,
            "crest_heightening": True,
            "berm_widening": True,
            "revetment": True,
            "custom": True,
        }
        i = 0
        for section in dike_traject.dike_sections:
            side = "left" if index == 0 else "right"
            section.shift_trajectory_sideways(100, side)

            # if a section is not in analyse, skip it, and it turns blank on the map.
            if not section.in_analyse:
                continue

            _measure_results = section.final_measure_veiligheidsrendement

            if _measure_results is not None:
                if _measure_results["investment_year"] == None:
                    _measure_results = None
                else:
                    add_measure_type_trace(
                        fig,
                        section,
                        _measure_results,
                        _legend_display,
                        legendgroup=dike_traject.run_name,
                    )

    _middle_point = get_middle_point(dike_traject.dike_sections)
    update_layout_map_box(fig, _middle_point)
    place_legend_right_top_corner(fig)

    return fig
