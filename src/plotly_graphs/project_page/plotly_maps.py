from typing import Optional

import numpy as np
import plotly.graph_objects as go

from src.constants import PROJECTS_COLOR_SEQUENCE, Mechanism, ResultType, ColorBarResultType, SubResultType
from src.linear_objects.dike_traject import DikeTraject
from src.linear_objects.project import DikeProject
from src.plotly_graphs.plotly_maps import update_layout_map_box, add_section_trace, plot_default_overview_map_dummy, \
    get_middle_point, get_average_point, get_reliability_color, add_colorscale_bar, place_legend_left_top_corner, \
    place_legend_right_top_corner
from src.utils.gws_convertor import GWSRDConvertor
from src.utils.utils import get_beta, beta_to_pf


def plot_project_overview_map(projects: list[DikeProject], trajects: Optional[list[DikeTraject]]=None) -> go.Figure:
    """
    This function plots an overview Map of the current dike in data. It uses plotly Mapbox for the visualization.

    :param dike_traject: DikeTraject object with the data of the dike.
    :param selected_result_type: string of the selected result type in the select dropdown field.

    :return:
    """
    fig = go.Figure()
    sections = []
    if len(projects) == 0:
        return plot_default_overview_map_dummy()
    for i, project in enumerate(projects):
        _color = PROJECTS_COLOR_SEQUENCE[i]
        for index, section in enumerate(project.dike_sections):
            sections.append(section)
            # if a section is not in analyse, skip it, and it turns blank on the map.
            _hovertemplate = (
                    f"Traject {project.name}<br>" +
                    f"Vaknaam {section.name}<br>" + f"Lengte: {section.length}m <extra></extra>"
            )
            _coordinates_wgs = [
                GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in section.coordinates_rd
            ]  # convert in GWS coordinates:

            fig.add_trace(
                go.Scattermap(
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
                fig.add_trace(go.Scattermap(
                    mode="text",
                    lat=[[x[0] for x in _coordinates_wgs][0]],
                    lon=[[x[1] for x in _coordinates_wgs][0]],
                    showlegend=False,
                    text=project.name,
                    textfont=dict(size=15)

                ))

        _middle_point = get_average_point(sections)
        update_layout_map_box(fig, _middle_point, zoom=10)

    if trajects is not None:
        _color = "grey"
        for traject in trajects:
            for index, section in enumerate(traject.dike_sections):
                sections.append(section)
                # if a section is not in analyse, skip it, and it turns blank on the map.
                _hovertemplate = (
                        f"Traject {traject.name}<br>" +
                        f"Vaknaam {section.name}<br>" + f"Lengte: {section.length}m <extra></extra>"
                )
                _coordinates_wgs = [
                    GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in section.coordinates_rd
                ]  # convert in GWS coordinates:

                fig.add_trace(
                    go.Scattermap(
                        mode="lines",
                        lat=[x[0] for x in _coordinates_wgs],
                        lon=[x[1] for x in _coordinates_wgs],
                        marker={"size": 10, "color": _color},
                        line={"width": 4, "color": _color},
                        name=traject.name,
                        legendgroup=traject.name,
                        hovertemplate=_hovertemplate,
                        opacity=0.9,
                        showlegend=True if index == 0 else False,
                    )
                )
    place_legend_right_top_corner(fig)
    return fig

def plot_comparison_runs_overview_map_projects(projects: list[DikeProject], trajects: list[DikeTraject])-> go.Figure:
    return plot_project_overview_map(projects, trajects)

def plot_comparison_runs_overview_map_assessment(trajects: list[DikeTraject])-> go.Figure:

    fig = go.Figure()
    sections = []  # add section to a list to find the middle point for all trajects
    for dike_traject in trajects:
        for section in dike_traject.dike_sections:
            sections.append(section)
            _coordinates_wgs = [
                GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in section.coordinates_rd
            ]  # convert in GWS coordinates:

            # if a section is not in analyse, skip it, and it turns blank on the map.
            if not section.in_analyse:
                continue

            _initial_results = section.initial_assessment

            if _initial_results is not None:
                _year_index = 0
                _beta = get_beta(_initial_results, _year_index, Mechanism.SECTION.name)
                _beta_dict = {
                    meca: beta[_year_index]
                    for meca, beta in _initial_results.items()
                    if meca != "Section"
                }
                _color = get_reliability_color(_beta, dike_traject.lower_bound_value)


                _hover_res = f"Pf sectie: {beta_to_pf(_beta):.2e}<br>"

                _hovertemplate = (
                        f"Vaknaam {section.name}<br>" + _hover_res + "<extra></extra>"
                )

                _mechanism = min(
                    _beta_dict, key=_beta_dict.get
                )  # mechanism with lowest beta
                _hovertemplate = (
                        _hovertemplate[:-15]
                        + f"Laagste beta: {_mechanism}<br>"
                        + "<extra></extra>"
                )  # :-15 to remove <extra></extra> from string

            else:
                _color = "grey"
                _hovertemplate = (
                        f"Vaknaam {section.name}<br>" f"Beta: NO DATA<br>" + "<extra></extra>"
                )

            add_section_trace(
                fig,
                section,
                name=dike_traject.name,
                color=_color,
                hovertemplate=_hovertemplate,
            )

    # Add colorscale bar, /!\ This will be centered around the lower bound value of the LAST dike traject
    add_colorscale_bar(
        fig,
        ResultType.PROBABILITY.name,
        ColorBarResultType.RELIABILITY.name,
        SubResultType.ABSOLUTE.name,
        dike_traject.lower_bound_value,
    )

    # Update layout of the figure and add token for mapbox
    _middle_point = get_middle_point(sections)
    update_layout_map_box(fig, _middle_point)
    place_legend_right_top_corner(fig)

    return fig

def plot_comparison_runs_overview_map_simple(trajects: list[DikeTraject], selected_sections)-> go.Figure:
    """
    This function plots an overview Map of the current dike in data. It uses plotly Mapbox for the visualization.


    :return:
    """
    fig = go.Figure()
    sections = []

    if trajects is not None:
        for traject in trajects:
            for index, section in enumerate(traject.dike_sections):
                sections.append(section)

                if f"{section.name}|{traject.name}" in selected_sections:
                    _color = "red"
                else:
                    _color = "grey"
                # if a section is not in analyse, skip it, and it turns blank on the map.
                _hovertemplate = (
                        f"Traject {traject.name}<br>" +
                        f"Vaknaam {section.name}<br>" + f"Lengte: {section.length}m <extra></extra>"
                )
                _coordinates_wgs = [
                    GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in section.coordinates_rd
                ]  # convert in GWS coordinates:

                fig.add_trace(
                    go.Scattermap(
                        mode="lines",
                        lat=[x[0] for x in _coordinates_wgs],
                        lon=[x[1] for x in _coordinates_wgs],
                        marker={"size": 10, "color": _color},
                        line={"width": 4, "color": _color},
                        name=traject.name,
                        legendgroup=traject.name,
                        hovertemplate=_hovertemplate,
                        opacity=0.9,
                        showlegend=True if index == 0 else False,
                    )
                )

    _middle_point = get_average_point(sections)
    update_layout_map_box(fig, _middle_point, zoom=10)
    place_legend_right_top_corner(fig)

    return fig


def plot_cost_vs_time_projects(projects: list[DikeProject]):
    fig = go.Figure()
    start_program = 2025
    end_program = 2100
    years = list(range(start_program, end_program + 1))

    for i, project in enumerate(projects):
        _color = PROJECTS_COLOR_SEQUENCE[i]

        # Split the cost equally over the duration of the project
        cost = project.calc_project_cost()
        cost_yearly = cost / (project.end_year - project.start_year + 1)
        cost_list = np.zeros(len(years))
        for year in range(project.start_year, project.end_year):
            cost_list[year - start_program] = cost_yearly

        fig.add_trace(go.Bar(
            name=project.name,
            x=years,
            y=cost_list,
            offset=0,
            marker=dict(color=_color, pattern_shape='/'),

            # hovertemplate with start and end year, total cost cost of project
            hovertemplate=f"{project.name}<br>Startjaar: {project.start_year}<br>"
                          f"Eindjaar: {project.end_year}<br>"
                          f"Jaarlijkse Kosten: {cost_yearly / 1e6:.2f} mln €<br>"
                          f"Totaal Kosten: {cost / 1e6:.1f} mln €<extra></extra>"
        ))

    fig.update_layout(template='plotly_white')
    fig.update_yaxes(title="Jaarlijkse Kosten (mln €)")
    fig.update_xaxes(title="Jaar")

    # no gap between bars
    fig.update_layout(barmode='stack', bargap=0)

    return fig
