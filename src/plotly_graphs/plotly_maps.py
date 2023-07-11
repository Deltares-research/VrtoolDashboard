from bisect import bisect_right
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from matplotlib import pyplot as plt, colors
from pandas import DataFrame

from src.constants import REFERENCE_YEAR, ColorBarResultType, Mechanism
from src.layouts.layout_main_page import CalcType, ResultType
from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject
from src.utils.gws_convertor import GWSRDConvertor
from src.utils.utils import to_million_euros, beta_to_pf, pf_to_beta

color_dict = {""}


def plot_default_overview_map_dummy() -> go.Figure:
    """
    This function plots the default empty overview Map
    """
    fig = go.Figure()

    fig.add_trace(go.Scattermapbox(
        mode="lines",
        lat=[],
        lon=[],
        showlegend=False))

    # this is centered on the Netherlands and zoomed out
    update_layout_map_box(fig, center=(51.798160177811454, 5.200357914732026), zoom=8)
    return fig


def plot_overview_map_dummy(dike_traject: DikeTraject, selected_result_type: str) -> go.Figure:
    """
    This function plots an overview Map of the current dike in data. It uses plotly Mapbox for the visualization.

    :param dike_traject: DikeTraject object with the data of the dike.
    :param selected_result_type: string of the selected result type in the select dropdown field.

    :return:
    """
    fig = go.Figure()

    for section in dike_traject.dike_sections:
        coordinates_wgs = [GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in
                           section.coordinates_rd]  # convert in GWS coordinates:

        # if a section is not in analyse, skip it, and it turns blank on the map.
        if not section.in_analyse:
            continue

        _measure_results = section.final_measure_doorsnede if selected_result_type == CalcType.DOORSNEDE_EISEN.name else section.final_measure_veiligheidrendement
        if _measure_results is not None:

            color = 'green' if _measure_results[
                                   'name'] == "Grondversterking binnenwaarts 2025" else 'red'
            hovertemplate = f'Vaknaam {section.name}<br>' \
                            f'Maatregel: {_measure_results["name"]} m<br>' \
                            f'LCC: {to_million_euros(_measure_results["LCC"])} M€<br>'
        else:
            color = 'grey'
            hovertemplate = f'Vaknaam {section.name}<br>' \
                            f'Maatregel: {None} m<br>' \
                            f'LCC: {0} €<br>'

        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lat=[x[0] for x in coordinates_wgs],
            lon=[x[1] for x in coordinates_wgs],
            marker={'size': 10, 'color': color},
            line={'width': 5, 'color': color},
            name='Traject 38-1',
            hovertemplate=hovertemplate,
            showlegend=False))

    # Update layout of the figure and add token for mapbox
    _middle_point = get_middle_point(dike_traject.dike_sections)
    update_layout_map_box(fig, _middle_point)

    return fig


def plot_dike_traject_reliability_initial_assessment_map(dike_traject: DikeTraject, selected_year: float,
                                                         result_type: str, mechanism_type: str) -> go.Figure:
    """
    This function plots a Map displaying the initial reliability of the dike traject.
    :param dike_traject:
    :param selected_year: selected year by the user for which results must be displayed
    :param result_type: one of "Reliability" or "Probability"
    :param mechanism_type: Selected mechanism type by the user from the OptionField, one of "PIPING", "STABILITY",
    "OVERFLOW" or "SECTION"

    :return:
    """
    fig = go.Figure()

    for section in dike_traject.dike_sections:
        _coordinates_wgs = [GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in
                            section.coordinates_rd]  # convert in GWS coordinates:

        # if a section is not in analyse, skip it, and it turns blank on the map.
        if not section.in_analyse:
            continue

        _initial_results = section.initial_assessment

        if _initial_results is not None:
            _year_index = bisect_right(section.years, selected_year - REFERENCE_YEAR) - 1
            _beta_section = get_betas(_initial_results, _year_index, mechanism_type)
            _beta_dict = {meca: beta[_year_index] for meca, beta in _initial_results.items() if meca != "Section"}
            _color = get_reliability_color(_beta_section)

            if result_type == ResultType.RELIABILITY.name:
                _hover_res = f'Betas section: {_beta_section:.2}<br>'
            else:
                _hover_res = f'Pf section: {beta_to_pf(_beta_section):.2e}<br>'

            _hovertemplate = f'Vaknaam {section.name}<br>' + _hover_res

            if mechanism_type == Mechanism.SECTION.name:
                _mechanism = min(_beta_dict, key=_beta_dict.get) # mechanism with lowest beta
                _hovertemplate += f"Lowest beta: {_mechanism}<br>"

        else:
            _color = 'grey'
            _hovertemplate = f'Vaknaam {section.name}<br>' \
                             f'Betas: NO DATA<br>'

        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lat=[x[0] for x in _coordinates_wgs],
            lon=[x[1] for x in _coordinates_wgs],
            marker={'size': 10, 'color': _color},
            line={'width': 5, 'color': _color},
            name='Traject 38-1',
            hovertemplate=_hovertemplate,
            showlegend=False))

    add_colorscale_bar(fig, result_type, ColorBarResultType.RELIABILITY.name)

    # Update layout of the figure and add token for mapbox
    _middle_point = get_middle_point(dike_traject.dike_sections)
    update_layout_map_box(fig, _middle_point)

    return fig


def plot_dike_traject_reliability_measures_assessment_map(dike_traject: DikeTraject, selected_year: float,
                                                          result_type: str, calc_type: str,
                                                          colorbar_result_type: str, mechanism_type: str) -> go.Figure:
    """
    This function plots a Map displaying the reliability of the dike traject after measures.
    :param dike_traject:
    :param selected_year: selected year by the user for which results must be displayed
    :param result_type: one of "RELIABILITY" or "PROBABILITY"
    :param calc_type: one of "VEILIGHEIDRENDEMENT" or "DOORSNEDE"
    :param colorbar_result_type: one of "RELIABILITY" or "COST" or "MEASURE"
    :param mechanism_type: Selected mechanism type by the user from the OptionField, one of "PIPING", "STABILITY",
    "OVERFLOW" or "SECTION".

    """
    fig = go.Figure()
    for section in dike_traject.dike_sections:
        _coordinates_wgs = [GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in
                            section.coordinates_rd]  # convert in GWS coordinates:

        # if a section is not in analyse, skip it, and it turns blank on the map.
        if not section.in_analyse:
            continue

        _initial_results = section.initial_assessment

        _measure_results = section.final_measure_veiligheidrendement if calc_type == CalcType.VEILIGHEIDRENDEMENT.name else section.final_measure_doorsnede

        if _measure_results is not None:

            _year_index = bisect_right(section.years, selected_year - REFERENCE_YEAR) - 1
            _beta_section = get_betas(_measure_results, _year_index, mechanism_type)

            _beta_dict = {key: value[_year_index] for key, value in _measure_results.items() if
                          key in ["StabilityInner", "Piping", "Overflow"]}

            if colorbar_result_type == ColorBarResultType.RELIABILITY.name:
                _color = get_reliability_color(_beta_section)

            elif colorbar_result_type == ColorBarResultType.COST.name:
                _color = get_cost_color(to_million_euros(_measure_results["LCC"]))

            elif colorbar_result_type == ColorBarResultType.MEASURE.name:
                pass
            else:
                raise NotImplementedError("This result type is not implemented yet")

            _hovertemplate = f'Vaknaam {section.name}<br>' \
                             f'Maatregel: {_measure_results["name"]} m<br>' \
                             f'LCC: {to_million_euros(_measure_results["LCC"])} M€<br>' \
                             f'Betas section: {_beta_section:.2}<br>' \
                             f'Pf section: {beta_to_pf(_beta_section):.2e}<br>'
            if mechanism_type == Mechanism.SECTION.name:
                _mechanism = min(_beta_dict, key=_beta_dict.get)  # mechanism with lowest beta
                _hovertemplate += f"Lowest beta: {_mechanism}<br>"

        else:
            _color = 'grey'
            _hovertemplate = f'Vaknaam {section.name}<br>' \
                             f'Betas: NO DATA<br>'

        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lat=[x[0] for x in _coordinates_wgs],
            lon=[x[1] for x in _coordinates_wgs],
            marker={'size': 10, 'color': _color},
            line={'width': 5, 'color': _color},
            name='Traject 38-1',
            hovertemplate=_hovertemplate,
            showlegend=False))

    add_colorscale_bar(fig, result_type, colorbar_result_type)

    # Update layout of the figure and add token for mapbox
    _middle_point = get_middle_point(dike_traject.dike_sections)
    update_layout_map_box(fig, _middle_point)

    return fig


def get_middle_point(sections: list[DikeSection]) -> tuple[float, float]:
    """Return the middle point in GWS coordinates of the dik trajectory.

    :param sections: list of DikeSection objects.

    :return: tuple of the middle point in GWS coordinates.

    """
    first_point = sections[0].coordinates_rd[0]
    last_point = sections[-1].coordinates_rd[-1]

    middle_point_rd = ((first_point[0] + last_point[0]) / 2, (first_point[1] + last_point[1]) / 2)
    # convert in gws coordinates:
    middle_point_gws = GWSRDConvertor().to_wgs(middle_point_rd[0], middle_point_rd[1])
    return middle_point_gws


def update_layout_map_box(fig: go.Figure, center: tuple[float, float], zoom: int = 11):
    """Update layout of Mapbox figure.

    :param fig: go.Figure object.
    :param center: tuple of the center point in GWS coordinates.
    :param zoom: int of the zoom level of the map.

    """
    _mapbox_access_token = open(Path(__file__).parent.parent / "assets" / "mapbox_token.txt").read()
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        mapbox=dict(
            accesstoken=_mapbox_access_token,
            center=dict(lat=center[0], lon=center[1]),
            zoom=zoom,
        ))


def add_colorscale_bar(fig: go.Figure, result_type: str, colorbar_result_type: str):
    """Add a dummy scatter trace to the figure to show the colorscale bar

    :param fig: go.Figure object.
    :param result_type: type of results to show: "PROBABILITY" or "RELIABILITY".
    :param colorbar_result_type: type of colorbar to show: "RELIABILITY", "COST" or "MEASURE".
    """

    if colorbar_result_type == ColorBarResultType.RELIABILITY.name and result_type == ResultType.PROBABILITY.name:
        marker = dict(
            colorscale='RdYlGn',
            colorbar=dict(
                title="Faalkans",
                titleside='right',
                tickmode='array',
                tickvals=[2.3263478740408408, 3.090232306167813, 3.7190164854556804, 4.264890793922825,
                          4.753424308822899],
                ticktext=['1e-2', '1e-3', '1e-4', '1e-5', '1e-6'],
                ticks='outside',
                len=0.5,
            ),
            showscale=True,
            cmin=2,
            cmax=5,
        )
    elif colorbar_result_type == ColorBarResultType.RELIABILITY.name and result_type == ResultType.RELIABILITY.name:
        marker = dict(
            colorscale='RdYlGn',
            colorbar=dict(
                title="Betrouwbaarheid index",
                titleside='right',
                tickmode='array',
                tickvals=[2, 3, 4, 5],
                ticktext=['2', '3', '4', '5'],
                ticks='outside',
                len=0.5,
            ),
            showscale=True,
            cmin=2,
            cmax=5,
        )

    elif colorbar_result_type == ColorBarResultType.COST.name:
        marker = dict(
            colorscale='RdYlGn',
            reversescale=True,
            colorbar=dict(
                title="Kost (M€)",
                titleside='right',
                tickmode='array',
                tickvals=[0, 5, 10, 15, 20],
                ticktext=['0', '5', '10', '15', '20'],
                ticks='outside',
                len=0.5,
            ),
            showscale=True,
            cmin=0,
            cmax=20,
        )

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            showlegend=False,
            marker=marker,
            hoverinfo='none'
        )
    )

    # remove ticks from dummy scatter plot
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)


def get_reliability_color(reliability_value: float) -> str:
    """
    Return the color of the reliability value Beta on a colorscale from 2 (scarlet) to 5 (green), as a rgb string.
    :param reliability_value:
    :return:
    """
    cmap = plt.cm.RdYlGn  # theme of the colorscale
    norm = colors.Normalize(vmin=2, vmax=5)  # Hardcoded boundaries
    rgb = cmap(norm(reliability_value))
    return f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})'


def get_cost_color(cost_value) -> str:
    """
    Return the color of the cost value  on a colorscale from 0M€ (green) to 20M€ (scarlet), as a rgb string.
    :param cost_value:
    :return:
    """
    cmap = plt.cm.RdYlGn  # theme of the colorscale
    cmap = cmap.reversed()
    norm = colors.Normalize(vmin=0, vmax=20)  # Hardcoded boundaries
    rgb = cmap(norm(cost_value))
    return f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})'


def get_betas(results: dict, _year_index: int, mechanism: str):
    if mechanism == Mechanism.SECTION.name:
        return results["Section"][_year_index]
    elif mechanism == Mechanism.PIPING.name:
        return results["Piping"][_year_index]
    elif mechanism == Mechanism.OVERFLOW.name:
        return results["Overflow"][_year_index]
    elif mechanism == Mechanism.STABILITY.name:
        return results["StabilityInner"][_year_index]
