import numpy as np
import plotly.graph_objects as go
from matplotlib import pyplot as plt, colors
from shapely import Polygon, MultiPolygon, LineString

from src.constants import (
    REFERENCE_YEAR,
    ColorBarResultType,
    Mechanism,
    SubResultType,
    CalcType,
    ResultType,
)
from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject
from src.plotly_graphs.plotly_maps import update_layout_map_box, add_section_trace, get_middle_point
from src.utils.gws_convertor import GWSRDConvertor
from src.utils.utils import to_million_euros, beta_to_pf, pf_to_beta, get_beta


def plot_project_overview_map(project_data: dict) -> go.Figure:
    """
    This function plots an overview Map of the current dike in data. It uses plotly Mapbox for the visualization.

    :param dike_traject: DikeTraject object with the data of the dike.
    :param selected_result_type: string of the selected result type in the select dropdown field.

    :return:
    """
    fig = go.Figure()
    traject_plotted = []
    for _, dike_traject_data in project_data.items():
        dike_traject = DikeTraject.deserialize(dike_traject_data)
        if dike_traject.name in traject_plotted:
            continue

        for index, section in enumerate(dike_traject.dike_sections):

            # if a section is not in analyse, skip it, and it turns blank on the map.
            _hovertemplate = (
                    f"Vaknaam {section.name}<br>" + f"Lengte: {section.length}m <extra></extra>"
            )

            if not section.in_analyse:
                _color = "black"
                _hovertemplate += f"<br>Niet in analyse"
            else:
                _color = "grey"

            add_section_trace(
                fig,
                section,
                name=dike_traject.name,
                color=_color,
                hovertemplate=_hovertemplate,
            )
            traject_plotted.append(dike_traject.name)

        # Update layout of the figure and add token for mapbox
        _middle_point = (52.155170, 5.387207)  # lat/lon of Amersfoort
        update_layout_map_box(fig, _middle_point, zoom=7)

    return fig
