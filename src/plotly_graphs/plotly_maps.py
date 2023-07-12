from bisect import bisect_right
from pathlib import Path
from typing import Tuple

import numpy as np
import plotly.graph_objects as go
from matplotlib import pyplot as plt, colors
from pandas import DataFrame

from src.constants import REFERENCE_YEAR, ColorBarResultType, Mechanism, SubResultType
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
            _beta_section = get_beta(_initial_results, _year_index, mechanism_type)
            _beta_dict = {meca: beta[_year_index] for meca, beta in _initial_results.items() if meca != "Section"}
            _color = get_reliability_color(_beta_section)

            if result_type == ResultType.RELIABILITY.name:
                _hover_res = f'Beta sectie: {_beta_section:.2}<br>'
            else:
                _hover_res = f'Pf sectie: {beta_to_pf(_beta_section):.2e}<br>'

            _hovertemplate = f'Vaknaam {section.name}<br>' + _hover_res

            if mechanism_type == Mechanism.SECTION.name:
                _mechanism = min(_beta_dict, key=_beta_dict.get)  # mechanism with lowest beta
                _hovertemplate += f"Laagste beta: {_mechanism}<br>"

        else:
            _color = 'grey'
            _hovertemplate = f'Vaknaam {section.name}<br>' \
                             f'Beta: NO DATA<br>'

        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lat=[x[0] for x in _coordinates_wgs],
            lon=[x[1] for x in _coordinates_wgs],
            marker={'size': 10, 'color': _color},
            line={'width': 5, 'color': _color},
            name='Traject 38-1',
            hovertemplate=_hovertemplate,
            showlegend=False))

    add_colorscale_bar(fig, result_type, ColorBarResultType.RELIABILITY.name, SubResultType.ABSOLUTE.name)

    # Update layout of the figure and add token for mapbox
    _middle_point = get_middle_point(dike_traject.dike_sections)
    update_layout_map_box(fig, _middle_point)

    return fig


def plot_dike_traject_reliability_measures_assessment_map(dike_traject: DikeTraject, selected_year: float,
                                                          result_type: str, calc_type: str,
                                                          colorbar_result_type: str, mechanism_type: str,
                                                          sub_result_type: str) -> go.Figure:
    """
    This function plots a Map displaying the reliability of the dike traject after measures.
    :param dike_traject:
    :param selected_year: selected year by the user for which results must be displayed
    :param result_type: one of "RELIABILITY" or "PROBABILITY"
    :param calc_type: one of "VEILIGHEIDRENDEMENT" or "DOORSNEDE"
    :param colorbar_result_type: one of "RELIABILITY" or "COST" or "MEASURE"
    :param mechanism_type: Selected mechanism type by the user from the OptionField, one of "PIPING", "STABILITY",
    "OVERFLOW" or "SECTION".
    :param sub_result_type: Selected sub result type by the user from the OptionField, one of "ABSOLUTE" or "DIFFERENCE"
    or "RATIO"

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
            _beta_section = get_beta(_measure_results, _year_index, mechanism_type)

            if colorbar_result_type == ColorBarResultType.RELIABILITY.name and sub_result_type == SubResultType.ABSOLUTE.name:
                _color, _hovertemplate = get_color_hover_absolute_reliability(section, _beta_section, _measure_results)

            elif colorbar_result_type == ColorBarResultType.RELIABILITY.name and sub_result_type == SubResultType.RATIO.name:
                _color, _hovertemplate = get_color_hover_prob_ratio(section, _year_index, mechanism_type)

            elif colorbar_result_type == ColorBarResultType.COST.name and sub_result_type == SubResultType.ABSOLUTE.name:
                _color, _hovertemplate = get_color_hover_absolute_cost(section, _beta_section, _measure_results)

            elif colorbar_result_type == ColorBarResultType.COST.name and sub_result_type == SubResultType.DIFFERENCE.name:
                _color, _hovertemplate = get_color_hover_difference_cost(section)

            elif colorbar_result_type == ColorBarResultType.MEASURE.name:
                raise NotImplementedError("This result type is not implemented yet")

            else:
                raise ValueError("Wrong combination of settings? or not implemented yet")

            if mechanism_type == Mechanism.SECTION.name and sub_result_type == SubResultType.ABSOLUTE.name:
                _beta_dict = {key: value[_year_index] for key, value in _measure_results.items() if
                              key in ["StabilityInner", "Piping", "Overflow"]}
                _mechanism = min(_beta_dict, key=_beta_dict.get)  # mechanism with lowest beta
                _hovertemplate += f"Laagste beta: {_mechanism}<br>"

        # If no results are available for the dijkvak, return blank data.
        else:
            _color = 'grey'
            _hovertemplate = f'Vaknaam {section.name}<br>' \
                             f'Beta: NO DATA<br>'

        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lat=[x[0] for x in _coordinates_wgs],
            lon=[x[1] for x in _coordinates_wgs],
            marker={'size': 10, 'color': _color},
            line={'width': 5, 'color': _color},
            name='Traject 38-1',
            hovertemplate=_hovertemplate,
            showlegend=False))

    add_colorscale_bar(fig, result_type, colorbar_result_type, sub_result_type)

    # Update layout of the figure and add token for mapbox
    _middle_point = get_middle_point(dike_traject.dike_sections)
    update_layout_map_box(fig, _middle_point)

    return fig


def plot_dike_traject_urgency(dike_traject: DikeTraject, selected_year: float, length_urgency: float,
                              calc_type: str) -> go.Figure:
    """
    This function plots a Map displaying the urgency of the dike traject after measures based on the length of the dijvak.

    :param dike_traject:
    :param selected_year: Selected year by the user for which results must be displayed
    :param length_urgency: Selected length of the urgency by the user
    :param calc_type: one of "VEILIGHEIDRENDEMENT" or "DOORSNEDE"
    :return:
    """
    fig = go.Figure()

    _year_index = bisect_right(dike_traject.dike_sections[0].years, selected_year - REFERENCE_YEAR) - 1

    if calc_type == CalcType.VEILIGHEIDRENDEMENT.name:
        _section_index = bisect_right(dike_traject.get_cum_length("vr"), length_urgency * 1e3)
        _ordered_sections = dike_traject.reinforcement_order_vr[:_section_index]

    elif calc_type == CalcType.DOORSNEDE_EISEN.name:
        _section_index = bisect_right(dike_traject.get_cum_length("dsn"), length_urgency * 1e3)
        _ordered_sections = dike_traject.reinforcement_order_dsn[:_section_index]
    else:
        raise ValueError("Wrong calc type")

    cum_length = 0  # cumulative length of the sections
    added_to_legend = {}

    for section_name in _ordered_sections:
        section = dike_traject.get_section(section_name)

        _coordinates_wgs = [GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in
                            section.coordinates_rd]  # convert in GWS coordinates:

        if cum_length < 5000:  # first 5 km
            _color = "#f46e88"
            _group = "<5km"
        elif cum_length < 10000:  # next 5 km
            _color = '#94a329'
            _group = "<10km"
        elif cum_length < 15000:  # next 5 km
            _color = '#a38af6'
            _group = "<15km"
        else:  # last 5 km
            _color = 'yellow'
            _group = ">15km"

        _hovertemplate = f'Vaknaam {section.name}<br>' \
                         f'Length: {section.length}m <br>'

        showlegend = _group not in added_to_legend

        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lat=[x[0] for x in _coordinates_wgs],
            lon=[x[1] for x in _coordinates_wgs],
            marker={'size': 10, 'color': _color},
            line={'width': 5, 'color': _color},
            name=_group,
            legendgroup=_group,
            hovertemplate=_hovertemplate,
            showlegend=showlegend))

        cum_length += section.length
        added_to_legend[_group] = True

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


def add_colorscale_bar(fig: go.Figure, result_type: str, colorbar_result_type: str, sub_result_type: str):
    """Add a dummy scatter trace to the figure to show the colorscale bar

    :param fig: go.Figure object.
    :param result_type: type of results to show: "PROBABILITY" or "RELIABILITY".
    :param colorbar_result_type: type of colorbar to show: "RELIABILITY", "COST" or "MEASURE".
    """

    if colorbar_result_type == ColorBarResultType.RELIABILITY.name and result_type == ResultType.PROBABILITY.name \
            and sub_result_type == SubResultType.ABSOLUTE.name:
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
    elif colorbar_result_type == ColorBarResultType.RELIABILITY.name and result_type == ResultType.RELIABILITY.name \
            and sub_result_type == SubResultType.ABSOLUTE.name:
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
    elif colorbar_result_type == ColorBarResultType.RELIABILITY.name and sub_result_type == SubResultType.RATIO.name:
        marker = dict(
            colorscale='BrBG',
            reversescale=True,
            colorbar=dict(
                title="Verhouding pf vr/dsn",
                titleside='right',
                tickmode='array',
                tickvals=[0, 1, 2, 3],
                ticktext=['1', '10', '10', '100'],
                ticks='outside',
                len=0.5,
            ),
            showscale=True,
            cmin=0,
            cmax=3,
        )

    elif colorbar_result_type == ColorBarResultType.COST.name and sub_result_type == SubResultType.ABSOLUTE.name:
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

    elif colorbar_result_type == ColorBarResultType.COST.name and sub_result_type == SubResultType.DIFFERENCE.name:
        marker = dict(
            colorscale='RdYlGn',
            reversescale=True,
            colorbar=dict(
                title="Kost (M€)",
                titleside='right',
                tickmode='array',
                tickvals=[-10, 0, 1],
                ticktext=['-10', '0', '1'],
                ticks='outside',
                len=0.5,
            ),
            showscale=True,
            cmin=-10,
            cmax=1,
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


def get_color(value: float, cmap, vmin: float, vmax: float) -> str:
    """
    Return the color of the value on a colorscale, as a rgb string.
    :param value: value for which a color must be assigned
    :param cmap: color scale theme
    :param vmin: min value of the color scale
    :param vmax: max value of the color scale
    :return: color as rbg string
    """
    norm = colors.Normalize(vmin=vmin, vmax=vmax)  # Hardcoded boundaries
    rgb = cmap(norm(value))
    return f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})'


def get_reliability_color(reliability_value: float) -> str:
    """
    Return the color of the reliability value Beta on a colorscale from 2 (scarlet) to 5 (green), as a rgb string.
    :param reliability_value:
    :return:
    """
    return get_color(reliability_value, plt.cm.RdYlGn, 2, 5)


def get_probability_ratio_color(probability_ratio: float) -> str:
    cmap = plt.cm.BrBG  # theme of the colorscale
    cmap = cmap.reversed()
    return get_color(np.log(probability_ratio), cmap, 0, 3)


def get_cost_color(cost_value) -> str:
    """
    Return the color of the cost value  on a colorscale from 0M€ (green) to 20M€ (scarlet), as a rgb string.
    :param cost_value:
    :return:
    """
    cmap = plt.cm.RdYlGn  # theme of the colorscale
    cmap = cmap.reversed()
    return get_color(cost_value, cmap, 0, 20)


def get_color_diff_cost(cost_value) -> str:
    """
    return the color of the difference of cost between Veiligheidsrendement and Doorsnede.
    :param cost_value: diff cost
    :return:
    """
    cmap = plt.cm.RdYlGn  # theme of the colorscale
    cmap = cmap.reversed()
    return get_color(cost_value, cmap, -10, 10)  # center on 0 so that yellow is at 0 and very few section turn red


def get_beta(results: dict, year_index: int, mechanism: str) -> float:
    """Get the reliability value of a mechanism for a given year index.

    :param results: dict of results.
    :param year_index: int of the year index.
    :param mechanism: str of the mechanism.
    :return: float of the reliability value.

    """
    if mechanism == Mechanism.SECTION.name:
        return results["Section"][year_index]
    elif mechanism == Mechanism.PIPING.name:
        return results["Piping"][year_index]
    elif mechanism == Mechanism.OVERFLOW.name:
        return results["Overflow"][year_index]
    elif mechanism == Mechanism.STABILITY.name:
        return results["StabilityInner"][year_index]


def get_color_hover_prob_ratio(section: DikeSection, year_index: int, mechanism_type: str) -> Tuple[str, str]:
    _beta_vr = get_beta(section.final_measure_veiligheidrendement, year_index, mechanism_type)
    _beta_dsn = get_beta(section.final_measure_doorsnede, year_index, mechanism_type)
    _ratio_pf = beta_to_pf(_beta_vr) / beta_to_pf(_beta_dsn)
    _color = get_probability_ratio_color(_ratio_pf)

    _hovertemplate = f'Vaknaam {section.name}<br>' \
                     f'Pf Veiligheidsrendement: {beta_to_pf(_beta_vr):.2e}<br>' \
                     f'Pf Doorsnede: {beta_to_pf(_beta_dsn):.2e}<br>' \
                     f'Ratio Pf vr/dsn: {round(_ratio_pf, 1)}<br>'

    return _color, _hovertemplate


def get_color_hover_absolute_reliability(section: DikeSection, beta_section: float, measure_results: dict) -> Tuple[
    str, str]:
    _color = get_reliability_color(beta_section)

    _hovertemplate = f'Vaknaam {section.name}<br>' \
                     f'Maatregel: {measure_results["name"]} m<br>' \
                     f'LCC: {to_million_euros(measure_results["LCC"])} M€<br>' \
                     f'Beta sectie: {beta_section:.2}<br>' \
                     f'Pf sectie: {beta_to_pf(beta_section):.2e}<br>'

    return _color, _hovertemplate


def get_color_hover_absolute_cost(section: DikeSection, beta_section: float, measure_results: dict) -> Tuple[str, str]:
    _color = get_cost_color(to_million_euros(measure_results["LCC"]))
    _hovertemplate = f'Vaknaam {section.name}<br>' \
                     f'Maatregel: {measure_results["name"]} m<br>' \
                     f'LCC: {to_million_euros(measure_results["LCC"])} M€<br>' \
                     f'Beta sectie: {beta_section:.2}<br>' \
                     f'Pf sectie: {beta_to_pf(beta_section):.2e}<br>'

    return _color, _hovertemplate


def get_color_hover_difference_cost(section: DikeSection) -> Tuple[str, str]:
    _cost_vr = section.final_measure_veiligheidrendement["LCC"]
    _cost_dsn = section.final_measure_doorsnede["LCC"]
    _diff = _cost_vr - _cost_dsn

    _color = get_color_diff_cost(to_million_euros(_diff))

    _hovertemplate = f'Vaknaam {section.name}<br>' \
                     f'Kosten Veiligheidsrendement: {to_million_euros(_cost_vr)} M€<br>' \
                     f'Kosten Doorsnede: {to_million_euros(_cost_dsn)} M€<br>' \
                     f'Kostenverschil: {to_million_euros(_diff)} M€<br>'

    return _color, _hovertemplate
