import numpy as np
import plotly.graph_objects as go

from src.constants import PROJECTS_COLOR_SEQUENCE
from src.linear_objects.dike_traject import DikeTraject
from src.linear_objects.project import DikeProject
from src.plotly_graphs.plotly_maps import update_layout_map_box, add_section_trace, plot_default_overview_map_dummy
from src.utils.gws_convertor import GWSRDConvertor


def plot_project_overview_map(projects: list[DikeProject]) -> go.Figure:
    """
    This function plots an overview Map of the current dike in data. It uses plotly Mapbox for the visualization.

    :param dike_traject: DikeTraject object with the data of the dike.
    :param selected_result_type: string of the selected result type in the select dropdown field.

    :return:
    """
    fig = go.Figure()
    if len(projects) == 0:
        return plot_default_overview_map_dummy()
    for i, project in enumerate(projects):

        _color = PROJECTS_COLOR_SEQUENCE[i]
        for index, section in enumerate(project.dike_sections):
            # if a section is not in analyse, skip it, and it turns blank on the map.
            _hovertemplate = (
                    f"Traject {project.name}<br>" +
                    f"Vaknaam {section.name}<br>" + f"Lengte: {section.length}m <extra></extra>"
            )
            _coordinates_wgs = [
                GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in section.coordinates_rd
            ]  # convert in GWS coordinates:

            fig.add_trace(
                go.Scattermapbox(
                    mode="lines+text",
                    lat=[x[0] for x in _coordinates_wgs],
                    lon=[x[1] for x in _coordinates_wgs],
                    marker={"size": 10, "color": _color},
                    line={"width": 10, "color": _color},
                    name=project.name,
                    legendgroup=project.name,
                    hovertemplate=_hovertemplate,
                    showlegend=True if index == 0 else False,
                )
            )
            if index == int(len(project.dike_sections) / 2):
                fig.add_trace(go.Scattermapbox(
                    mode="text",
                    lat=[[x[0] for x in _coordinates_wgs][index]],
                    lon=[[x[1] for x in _coordinates_wgs][index]],
                    showlegend=False,
                    text=project.name,
                    textfont=dict(size=15)

                ))

        _middle_point = (52.155170, 5.387207)  # lat/lon of Amersfoort
        update_layout_map_box(fig, _middle_point, zoom=7)

    return fig


def plot_comparison_runs_overview_map(project_data: dict) -> go.Figure:
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

        # pick a random color for the dike traject
        _color = f"rgb({np.random.randint(0, 255)}, {np.random.randint(0, 255)}, {np.random.randint(0, 255)})"
        showlegend = True
        for index, section in enumerate(dike_traject.dike_sections):
            # if a section is not in analyse, skip it, and it turns blank on the map.
            _hovertemplate = (
                    f"Traject {dike_traject.name}<br>" +
                    f"Vaknaam {section.name}<br>" + f"Lengte: {section.length}m <extra></extra>"
            )

            add_section_trace(
                fig,
                section,
                name=dike_traject.name,
                color=_color,
                hovertemplate=_hovertemplate,
                showlegend=showlegend,
                legendgroup=dike_traject.name
            )
            showlegend = False
            traject_plotted.append(dike_traject.name)

    # Update layout of the figure and add token for mapbox
    _middle_point = (52.155170, 5.387207)  # lat/lon of Amersfoort
    update_layout_map_box(fig, _middle_point, zoom=7)

    # move legend to the left
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
        )
    )

    return fig
