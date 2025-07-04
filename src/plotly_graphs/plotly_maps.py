from bisect import bisect_right
from typing import Tuple, Optional

import numpy as np
import plotly.graph_objects as go
import plotly.colors
from matplotlib import pyplot as plt, colors
import plotly.express as px

from shapely import LineString
from vrtool.common.enums import MeasureTypeEnum

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
from src.utils.gws_convertor import GWSRDConvertor
from src.utils.utils import to_million_euros, beta_to_pf, pf_to_beta, get_beta

color_dict = {""}


def plot_default_overview_map_dummy() -> go.Figure:
    """
    This function plots the default empty overview Map
    """
    fig = go.Figure()

    fig.add_trace(go.Scattermap(mode="lines", lat=[], lon=[], showlegend=False))

    # this is centered on the Netherlands and zoomed out
    update_layout_map_box(fig, center=(51.798160177811454, 5.200357914732026), zoom=8)
    return fig


def plot_overview_map(dike_traject: DikeTraject) -> go.Figure:
    """
    This function plots an overview Map of the current dike in data. It uses plotly Mapbox for the visualization.

    :param dike_traject: DikeTraject object with the data of the dike.
    :param selected_result_type: string of the selected result type in the select dropdown field.

    :return:
    """
    fig = go.Figure()

    for index, section in enumerate(dike_traject.dike_sections):

        # if a section is not in analyse, skip it, and it turns blank on the map.
        _hovertemplate = (
                f"Vaknaam {section.name}<br>" + f"Lengte: {section.length}m <extra></extra>"
        )

        if not section.in_analyse:
            _color = "black"
            _hovertemplate += f"<br>Niet in analyse"
        else:
            _color = "rgb(253, 216, 53)" if index % 2 == 0 else "rgb(0, 172, 193)"

        add_section_trace(
            fig,
            section,
            name=dike_traject.name,
            color=_color,
            hovertemplate=_hovertemplate,
        )

    # Update layout of the figure and add token for mapbox
    _middle_point = get_middle_point(dike_traject.dike_sections)
    update_layout_map_box(fig, _middle_point)

    return fig


def plot_dike_traject_reliability_initial_assessment_map(
        dike_traject: DikeTraject,
        selected_year: float,
        result_type: str,
        mechanism_type: str,
) -> go.Figure:
    """
    This function plots a Map displaying the initial reliability of the dike traject.
    :param dike_traject:
    :param selected_year: selected year by the user for which results must be displayed
    :param result_type: one of "Reliability" or "Probability" or "InterpretationClass"
    :param mechanism_type: Selected mechanism type by the user from the OptionField, one of "PIPING", "STABILITY",
    "OVERFLOW", "REVETMENT" or "SECTION"

    :return:
    """
    fig = go.Figure()

    for section in dike_traject.dike_sections:
        _coordinates_wgs = [
            GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in section.coordinates_rd
        ]  # convert in GWS coordinates:

        # if a section is not in analyse, skip it, and it turns blank on the map.
        if not section.in_analyse:
            continue

        _initial_results = section.initial_assessment

        if _initial_results is not None:
            # TODO: Refactor this when moving to database format and handling mechanism types
            if mechanism_type == Mechanism.REVETMENT.name and not section.revetment:
                _color = "grey"
                _hovertemplate = (
                        f"Vaknaam {section.name}<br>"
                        f"Beta: NO DATA<br>" + "<extra></extra>"
                )
            else:
                _year_index = (
                        bisect_right(section.years, selected_year - REFERENCE_YEAR) - 1
                )
                _beta = get_beta(_initial_results, _year_index, mechanism_type)
                _beta_dict = {
                    meca: beta[_year_index]
                    for meca, beta in _initial_results.items()
                    if meca != "Section"
                }
                _color = get_reliability_color(_beta, dike_traject.lower_bound_value)

                if result_type == ResultType.RELIABILITY.name:
                    _hover_res = f"Beta sectie: {_beta:.2e}<br>"
                elif result_type == ResultType.PROBABILITY.name:
                    _hover_res = f"Pf sectie: {beta_to_pf(_beta):.2e}<br>"
                elif result_type == ResultType.INTERPRETATION_CLASS.name:
                    _color, _class = get_color_class_WBI(_beta)
                    _hover_res = f"WBI klass: {_class}<br>"
                    # _color = get_interpretation_class_color(_beta, dike_traject.signalering_value,
                    #                                         dike_traject.lower_bound_value)
                else:
                    raise ValueError("Unrecognized result type")

                _hovertemplate = (
                        f"Vaknaam {section.name}<br>" + _hover_res + "<extra></extra>"
                )

                if mechanism_type == Mechanism.SECTION.name:
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
    add_colorscale_bar(
        fig,
        result_type,
        ColorBarResultType.RELIABILITY.name,
        SubResultType.ABSOLUTE.name,
        dike_traject.lower_bound_value,
    )

    # Update layout of the figure and add token for mapbox
    _middle_point = get_middle_point(dike_traject.dike_sections)
    update_layout_map_box(fig, _middle_point)
    place_legend_right_top_corner(fig)

    return fig


def plot_dike_traject_reliability_measures_assessment_map(
        dike_traject: DikeTraject,
        selected_year: float,
        result_type: str,
        calc_type: str,
        colorbar_result_type: str,
        mechanism_type: str,
        sub_result_type: str,
) -> go.Figure:
    """
    This function plots a Map displaying the reliability of the dike traject after measures.
    :param dike_traject:
    :param selected_year: selected year by the user for which results must be displayed
    :param result_type: one of "RELIABILITY" or "PROBABILITY"
    :param calc_type: one of "VEILIGHEIDSRENDEMENT" or "DOORSNEDE"
    :param colorbar_result_type: one of "RELIABILITY" or "COST" or "MEASURE"
    :param mechanism_type: Selected mechanism type by the user from the OptionField, one of "PIPING", "STABILITY",
    "OVERFLOW" or "SECTION".
    :param sub_result_type: Selected sub result type by the user from the OptionField, one of "ABSOLUTE" or "DIFFERENCE"
    or "RATIO"

    """
    fig = go.Figure()

    if colorbar_result_type == ColorBarResultType.MEASURE.name:
        # In this case, returns a totally different figure
        return plot_dike_traject_measures_map(
            dike_traject, sub_result_type, calc_type, selected_year
        )

    for section in dike_traject.dike_sections:

        # if a section is not in analyse, skip it, and it turns blank on the map.
        if not section.in_analyse:
            continue

        _initial_results = section.initial_assessment

        _measure_results = (
            section.final_measure_veiligheidsrendement
            if calc_type == CalcType.VEILIGHEIDSRENDEMENT.name
            else section.final_measure_doorsnede
        )

        if _measure_results is not None:

            # TODO: Refactor this when moving to database format and handling mechanism types
            if mechanism_type == Mechanism.REVETMENT.name and not section.revetment:
                _color = "grey"
                _hovertemplate = (
                        f"Vaknaam {section.name}<br>"
                        f"Beta: NO DATA<br>" + "<extra></extra>"
                )
            else:

                _year_index = (
                        bisect_right(section.years, selected_year - REFERENCE_YEAR) - 1
                )
                _beta_section = get_beta(_measure_results, _year_index, mechanism_type)
                if _beta_section is None:
                    _color, _hovertemplate = get_no_data_info(section)

                elif (
                        colorbar_result_type == ColorBarResultType.RELIABILITY.name
                        and sub_result_type == SubResultType.ABSOLUTE.name
                        and result_type != ResultType.INTERPRETATION_CLASS.name
                ):
                    _color, _hovertemplate = get_color_hover_absolute_reliability(
                        section,
                        _beta_section,
                        _measure_results,
                        dike_traject.lower_bound_value,
                    )

                elif (
                        colorbar_result_type == ColorBarResultType.RELIABILITY.name
                        and sub_result_type == SubResultType.RATIO.name
                ):
                    _color, _hovertemplate = get_color_hover_prob_ratio(
                        section, _year_index, mechanism_type
                    )

                elif (
                        colorbar_result_type == ColorBarResultType.COST.name
                        and sub_result_type == SubResultType.ABSOLUTE.name
                ):
                    _color, _hovertemplate = get_color_hover_absolute_cost(
                        section, _beta_section, _measure_results
                    )

                elif (
                        colorbar_result_type == ColorBarResultType.COST.name
                        and sub_result_type == SubResultType.DIFFERENCE.name
                ):
                    _color, _hovertemplate = get_color_hover_difference_cost(section)

                elif (
                        colorbar_result_type == ColorBarResultType.RELIABILITY.name
                        and result_type == ResultType.INTERPRETATION_CLASS.name
                        and sub_result_type == SubResultType.ABSOLUTE.name
                ):
                    _color, _class = get_color_class_WBI(_beta_section)
                    _hovertemplate = (
                            f"Vaknaam {section.name}<br>"
                            f"WBI klasse: {_class}<br>" + "<extra></extra>"
                    )

                else:
                    raise ValueError(
                        "Wrong combination of settings? or not implemented yet"
                    )

                if (
                        mechanism_type == Mechanism.SECTION.name
                        and sub_result_type == SubResultType.ABSOLUTE.name
                ):
                    _beta_dict = {
                        key: value[_year_index]
                        for key, value in _measure_results.items()
                        if key in ["StabilityInner", "Piping", "Overflow", "Revetment"]
                    }
                    _mechanism = min(
                        _beta_dict, key=_beta_dict.get
                    )  # mechanism with lowest beta
                    _hovertemplate = (
                            _hovertemplate[:-15]
                            + f"Laagste beta: {_mechanism}<br>"
                            + "<extra></extra>"
                    )

        # If no results are available for the dijkvak, return blank data.
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

    add_colorscale_bar(
        fig,
        result_type,
        colorbar_result_type,
        sub_result_type,
        dike_traject.lower_bound_value,
    )

    # Update layout of the figure and add token for mapbox
    _middle_point = get_middle_point(dike_traject.dike_sections)
    update_layout_map_box(fig, _middle_point)

    return fig


def plot_dike_traject_urgency(
        dike_traject: DikeTraject,
        selected_year: float,
        length_urgency: float,
        calc_type: str,
) -> go.Figure:
    """
    This function plots a Map displaying the urgency of the dike traject after measures based on the length of the dijvak.

    :param dike_traject:
    :param selected_year: Selected year by the user for which results must be displayed
    :param length_urgency: Selected length of the urgency by the user
    :param calc_type: one of "VEILIGHEIDSRENDEMENT" or "DOORSNEDE"
    :return:
    """
    fig = go.Figure()

    _year_index = (
            bisect_right(
                dike_traject.dike_sections[0].years, selected_year - REFERENCE_YEAR
            )
            - 1
    )

    if calc_type == CalcType.VEILIGHEIDSRENDEMENT.name:
        _section_index = bisect_right(
            dike_traject.get_cum_length("vr"), length_urgency * 1e3
        )
        _ordered_sections = dike_traject.reinforcement_order_vr[:_section_index]

    elif calc_type == CalcType.DOORSNEDE_EISEN.name:
        _section_index = bisect_right(
            dike_traject.get_cum_length("dsn"), length_urgency * 1e3
        )
        _ordered_sections = dike_traject.reinforcement_order_dsn[:_section_index]
    else:
        raise ValueError("Wrong calc type")

    cum_length = 0  # cumulative length of the sections
    added_to_legend = {}

    for section_name in _ordered_sections:
        section = dike_traject.get_section(section_name)

        if cum_length < 5000:  # first 5 km
            _color = "#f46e88"
            _group = "0-5km"
        elif cum_length < 10000:  # next 5 km
            _color = "#94a329"
            _group = "5-10km"
        elif cum_length < 15000:  # next 5 km
            _color = "#a38af6"
            _group = "10-15km"
        else:  # last 5 km
            _color = "yellow"
            _group = ">15km"

        _hovertemplate = (
                f"Vaknaam {section.name}<br>"
                f"Length: {section.length}m <br>" + "<extra></extra>"
        )

        showlegend = _group not in added_to_legend

        add_section_trace(
            fig,
            section,
            name=_group,
            color=_color,
            hovertemplate=_hovertemplate,
            legendgroup=_group,
            showlegend=showlegend,
        )

        cum_length += section.length
        added_to_legend[_group] = True

    # Update layout of the figure and add token for mapbox
    _middle_point = get_middle_point(dike_traject.dike_sections)
    update_layout_map_box(fig, _middle_point)
    place_legend_right_top_corner(fig)

    return fig


def plot_dike_traject_measures_map(
        dike_traject: DikeTraject, subresult_type: str, calc_type: str, selected_year: float
):
    """
    This function plots a Map displaying the types of measures of the dike traject.

    :param dike_traject: Dike traject
    :param subresult_type: one of "MEASURE_TYPE" or "CREST_HEIGHTENING" or "BERM_WIDENING"
    :param calc_type: type of the optimization run: one of "VEILIGHEIDSRENDEMENT" or "DOORSNEDE"
    :param selected_year: year for which the results must be displayed
    :return:
    """
    fig = go.Figure()
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

    for section in dike_traject.dike_sections:

        # if a section is not in analyse, skip it, and it turns blank on the map.
        if not section.in_analyse:
            continue

        _measure_results = (
            section.final_measure_veiligheidsrendement
            if calc_type == CalcType.VEILIGHEIDSRENDEMENT.name
            else section.final_measure_doorsnede
        )
        if _measure_results is not None:
            if _measure_results["investment_year"] is not None:
                min_investment_year = min(_measure_results["investment_year"])
                if (
                        min_investment_year + REFERENCE_YEAR
                        <= selected_year
                ):  # only show measures that are implemented in the selected year
                    if subresult_type == SubResultType.MEASURE_TYPE.name:
                        add_measure_type_trace(
                            fig, section, _measure_results, _legend_display
                        )

                    elif subresult_type == SubResultType.CREST_HIGHTENING.name:
                        add_measure_crest_heightening_trace(
                            fig, section, _measure_results
                        )

                    elif subresult_type == SubResultType.BERM_WIDENING.name:
                        add_measure_berm_widening_trace(fig, section, _measure_results)

                if subresult_type == SubResultType.INVESTMENT_YEAR.name:
                    add_measure_investment_year_trace(
                        fig, section, _measure_results, _legend_display
                    )
            # else:
            #     fig.add_trace(go.Scattermapbox(
            #         mode="lines",
            #         lat=[],
            #         lon=[],
            #         showlegend=False))

    _middle_point = get_middle_point(dike_traject.dike_sections)
    update_layout_map_box(fig, _middle_point)
    place_legend_right_top_corner(fig)

    return fig


def add_measure_type_trace(
        fig: go.Figure, section: DikeSection, measure_results: dict, legend_display: dict, opacity: float = 1,
        legendgroup: Optional[str] = None
):
    """
    This function adds a trace to the figure for the measure type.
    :param fig:
    :param section: DikeSection
    :param measure_results:
    :param legend_display: dict to avoid double legend entries
    :param opacity: float
    :param legendgroup: Optional[str]. If None, the legendgroup is based on the measures types (all VZG grouped together)
    otherwise it is based on the provided name
    """
    if measure_results["name"] == "Geen maatregel":
        return
    if MeasureTypeEnum.SOIL_REINFORCEMENT.name in measure_results[
        "type"] or MeasureTypeEnum.SOIL_REINFORCEMENT.legacy_name in measure_results[
        "type"] or MeasureTypeEnum.SOIL_REINFORCEMENT_WITH_STABILITY_SCREEN.name in measure_results[
        "type"] or MeasureTypeEnum.SOIL_REINFORCEMENT_WITH_STABILITY_SCREEN.legacy_name in measure_results["type"]:
        # convert in GWS coordinates:
        _coordinates_wgs = GWSRDConvertor.generate_coordinates_from_buffer(
            section.coordinates_rd, buffersize=60
        )
        _visible = True
        if measure_results["dcrest"] == 0 and measure_results["dberm"] > 0:
            _name = "Bermverbreding"
            _color = f"rgb(154, 205, 50, {opacity})"
            _showlegend = legend_display.get("berm_widening")
            legend_display["berm_widening"] = False

        if measure_results["dberm"] == 0 and measure_results["dcrest"] > 0:
            _name = "Kruinverhoging"
            _color = f"rgb(0, 255, 0, {opacity})"
            _showlegend = legend_display.get("crest_heightening")
            legend_display["crest_heightening"] = False

        if measure_results["dcrest"] > 0 and measure_results["dberm"] > 0:
            _name = "Grondversterking binnenwaarts"
            _color = f"rgb(0, 128, 0, {opacity})"  # Green
            _showlegend = legend_display.get("ground_reinforcement")
            legend_display["ground_reinforcement"] = False
        if measure_results["dcrest"] == 0 and measure_results["dberm"] == 0:
            # exit 2 if statement

            _name = ""
            _color = f"rgb(0, 128, 0, {0})"  # Green
            _showlegend = legend_display.get("ground_reinforcement")
            legend_display["ground_reinforcement"] = False
            _visible = False

        _hovertext = f"Vaknaam {section.name}<br>"
        _hovertext += f"Maatregel: {measure_results['name']} <br>"
        _hovertext += f"Investeringsjaar: {get_investment_year_str(measure_results['investment_year'])} <br>"
        _hovertext += f"Kruinverhoging: {measure_results['dcrest']}m <br>"
        _hovertext += f"Bermverbreding: {measure_results['dberm']}m <br>"
        if measure_results.get("L_stab_screen") is not None:
            _hovertext += f"Stabiliteitsscherm: {measure_results['L_stab_screen']}m <br>"
        _hovertext += "<extra></extra>"

        fig.add_trace(
            go.Scattermap(
                name=_name,
                legendgroup=_name if legendgroup is None else legendgroup,
                legendgrouptitle_text=None if legendgroup is None else legendgroup,
                legendgrouptitle=dict(font=dict(weight='bold')),
                mode="lines",
                lat=[x[0] for x in _coordinates_wgs],
                lon=[x[1] for x in _coordinates_wgs],
                fillcolor=_color,
                line={"width": 1, "color": _color},
                fill="toself",
                showlegend=_showlegend,
                visible=_visible,
                hovertemplate=_hovertext,
                opacity=opacity,
            )
        )

    if MeasureTypeEnum.VERTICAL_PIPING_SOLUTION.name in measure_results[
        "type"] or MeasureTypeEnum.VERTICAL_PIPING_SOLUTION.legacy_name in measure_results["type"]:
        _color = "red"
        _coordinates_wgs = [
            GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in section.coordinates_rd
        ]  # convert in GWS coordinates:
        fig.add_trace(
            go.Scattermap(
                name="Verticale pipingoplossing",
                legendgroup="VZG" if legendgroup is None else legendgroup,
                mode="lines",
                lat=[x[0] for x in _coordinates_wgs],
                lon=[x[1] for x in _coordinates_wgs],
                line={"color": _color, "width": 4},
                opacity=opacity,
                showlegend=legend_display.get("VZG"),
                hovertemplate=f"Vaknaam {section.name}<br>"
                              f"{measure_results['name']}<br>"
                              f"Investeringsjaar: {get_investment_year_str(measure_results['investment_year'])} <br>"
                              f"<extra></extra>",
            )
        )
        legend_display["VZG"] = False

    if MeasureTypeEnum.STABILITY_SCREEN.name in measure_results[
        "type"] or MeasureTypeEnum.STABILITY_SCREEN.legacy_name in measure_results[
        "type"] or MeasureTypeEnum.SOIL_REINFORCEMENT_WITH_STABILITY_SCREEN.name in measure_results[
        "type"] or MeasureTypeEnum.SOIL_REINFORCEMENT_WITH_STABILITY_SCREEN.legacy_name in measure_results["type"]:
        _color = "blue"
        _coordinates_wgs = [
            GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in section.coordinates_rd
        ]  # convert in GWS coordinates:
        fig.add_trace(
            go.Scattermap(
                name="Stabiliteitsscherm",
                legendgroup="screen" if legendgroup is None else legendgroup,
                mode="lines",
                lat=[x[0] for x in _coordinates_wgs],
                lon=[x[1] for x in _coordinates_wgs],
                line={"color": _color, "width": 4},
                opacity=opacity,
                showlegend=legend_display.get("screen"),
                hovertemplate=f"Vaknaam {section.name}<br>"
                              f"{measure_results['name']} <br>"
                              f"Investeringsjaar: {get_investment_year_str(measure_results['investment_year'])} <br>"
                              f"Stabiliteitsscherm: {measure_results.get('L_stab_screen')}m <br>"
                              f"<extra></extra>",
            )
        )
        legend_display["screen"] = False

    if MeasureTypeEnum.DIAPHRAGM_WALL.name in measure_results[
        "type"] or MeasureTypeEnum.DIAPHRAGM_WALL.legacy_name in measure_results["type"]:
        _coordinates_wgs = GWSRDConvertor.generate_coordinates_from_buffer(
            section.coordinates_rd, buffersize=60
        )

        fig.add_trace(
            go.Scattermap(
                name="Zelfkerende constructie",
                legendgroup="diaphram wall" if legendgroup is None else legendgroup,
                mode="lines",
                lat=[x[0] for x in _coordinates_wgs],
                lon=[x[1] for x in _coordinates_wgs],
                fillcolor=f"rgba(0, 0, 0, {opacity})",
                line={"width": 1, "color": "black"},
                fill="toself",
                opacity=opacity,
                showlegend=legend_display.get("diaphram wall"),
                hovertemplate=f"Vaknaam: {section.name}<br>"
                              f"Custom maatregel: {measure_results['name']} <br>"
                              f"Investeringsjaar: {get_investment_year_str(measure_results['investment_year'])} <br>"
                              f"<extra></extra>",
            )
        )
        legend_display["diaphram wall"] = False

    if MeasureTypeEnum.ANCHORED_SHEETPILE.name in measure_results[
        "type"] or MeasureTypeEnum.ANCHORED_SHEETPILE.legacy_name in measure_results["type"]:
        _coordinates_wgs = GWSRDConvertor.generate_coordinates_from_buffer(
            section.coordinates_rd, buffersize=60
        )

        fig.add_trace(
            go.Scattermap(
                name="Damwandconstructie",
                legendgroup="sheetpile" if legendgroup is None else legendgroup,
                mode="lines",
                lat=[x[0] for x in _coordinates_wgs],
                lon=[x[1] for x in _coordinates_wgs],
                fillcolor=f"rgb(128, 128, 128, {opacity})",
                line={"width": 1, "color": "grey"},
                fill="toself",
                opacity=opacity,
                showlegend=legend_display.get("sheetpile"),
                hovertemplate=f"Vaknaam: {section.name}<br>"
                              f"Custom maatregel: {measure_results['name']} <br>"
                              f"Investeringsjaar: {get_investment_year_str(measure_results['investment_year'])} <br>"
                              f"<extra></extra>",
            )
        )
        legend_display["sheetpile"] = False

    if MeasureTypeEnum.REVETMENT.name in measure_results["type"] or MeasureTypeEnum.REVETMENT.legacy_name in \
            measure_results["type"]:
        _ls = LineString(section.coordinates_rd)
        _offset_ls = _ls.parallel_offset(20, "left")

        _coordinates_wgs = [
            GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in _offset_ls.coords
        ]  # convert in GWS coordinates:
        if "Grondversterking" in measure_results["name"] and measure_results["dcrest"] == 0 and measure_results[
            "dberm"] == 0:
            name_hover = "Aanpassing bekleding"
        elif "Grondversterking" not in measure_results["name"]:
            name_hover = "Aanpassing bekleding"
        else:
            name_hover = measure_results["name"]

        if measure_results['diff_transition_level'] == 0 and measure_results['pf_target_ratio'] == 1:
            return

        fig.add_trace(
            go.Scattermap(
                name="Aanpassing bekleding",
                legendgroup="revetment" if legendgroup is None else legendgroup,
                mode="lines",
                lat=[x[0] for x in _coordinates_wgs],
                lon=[x[1] for x in _coordinates_wgs],
                fillcolor=f"rgb(128, 128, 128, {opacity})",
                line={"width": 4, "color": "black"},
                # fill="toself",
                opacity=opacity,
                showlegend=legend_display.get("revetment"),
                hovertemplate=f"Vaknaam {section.name}<br>"
                              f"{name_hover} <br>"
                              f"Investeringsjaar: {get_investment_year_str(measure_results['investment_year'])} <br>"
                              f"Factor veiliger bekleding {measure_results['pf_target_ratio']} <br>"
                              f"Verhoging overgang {measure_results['diff_transition_level']}m <br>"
                              f"<extra></extra>",
            )
        )

        legend_display["revetment"] = False

    if MeasureTypeEnum.CUSTOM.name in measure_results["type"] or MeasureTypeEnum.CUSTOM.legacy_name in \
            measure_results["type"]:
        _coordinates_wgs = GWSRDConvertor.generate_coordinates_from_buffer(
            section.coordinates_rd, buffersize=60
        )

        fig.add_trace(
            go.Scattermap(
                name="Custom",
                legendgroup="custom" if legendgroup is None else legendgroup,
                mode="lines",
                lat=[x[0] for x in _coordinates_wgs],
                lon=[x[1] for x in _coordinates_wgs],
                fillcolor=f"rgb(128, 128, 128, {opacity})",
                line={"width": 1, "color": "grey"},
                fill="toself",
                opacity=opacity,
                showlegend=legend_display.get("custom"),
                hovertemplate=f"Vaknaam {section.name}<br>"
                              f"{measure_results['name']} <br>"
                              f"Investeringsjaar: {get_investment_year_str(measure_results['investment_year'])} <br>"
                              f"<extra></extra>",
            )
        )
        legend_display["custom"] = False


def add_measure_crest_heightening_trace(
        fig: go.Figure, section: DikeSection, measure_results: dict
):
    if "Grondversterking" in measure_results["name"]:
        if measure_results["dcrest"] > 0:
            _trajectory_buffer = section.trajectory_rd.buffer(60, cap_style=2)

            _coordinates_wgs = [
                GWSRDConvertor().to_wgs(pt[0], pt[1])
                for pt in _trajectory_buffer.exterior.coords
            ]  # convert in GWS coordinates:

            _color = get_crest_heightening_color(measure_results["dcrest"])

            fig.add_trace(
                go.Scattermap(
                    name=measure_results["name"],
                    legendgroup=measure_results["name"],
                    mode="lines",
                    lat=[x[0] for x in _coordinates_wgs],
                    lon=[x[1] for x in _coordinates_wgs],
                    fillcolor=_color,
                    line={"width": 1, "color": _color},
                    fill="toself",
                    showlegend=False,
                    hovertemplate=f"Vaknaam {section.name}<br>"
                                  f"Maatregel: {measure_results['name']} <br>"
                                  f"Investeringsjaar: {get_investment_year_str(measure_results['investment_year'])} <br>"
                                  f"Kruin verhoging: {measure_results['dcrest']}m <br>"
                                  f"Bermverbreding: {measure_results['dberm']}m <br>"
                                  f"<extra></extra>",
                )
            )
            add_colorscale_bar_crest_heigtening(fig)


def add_measure_berm_widening_trace(
        fig: go.Figure, section: DikeSection, measure_results: dict
):
    if "Grondversterking" in measure_results["name"]:
        if measure_results["dberm"] > 0:
            _coordinates_wgs = GWSRDConvertor.generate_coordinates_from_buffer(
                section.coordinates_rd, buffersize=60
            )

            _color = get_berm_widening_color(measure_results["dberm"])

            fig.add_trace(
                go.Scattermap(
                    name=measure_results["name"],
                    legendgroup=measure_results["name"],
                    mode="lines",
                    lat=[x[0] for x in _coordinates_wgs],
                    lon=[x[1] for x in _coordinates_wgs],
                    fillcolor=_color,
                    line={"width": 1, "color": _color},
                    fill="toself",
                    showlegend=False,
                    hovertemplate=f"Vaknaam {section.name}<br>"
                                  f"Maatregel: {measure_results['name']} <br>"
                                  f"Investeringsjaar: {get_investment_year_str(measure_results['investment_year'])} <br>"
                                  f"Kruin verhoging: {measure_results['dcrest']}m <br>"
                                  f"Bermverbreding: {measure_results['dberm']}m <br>"
                                  f"<extra></extra>",
                )
            )
            add_colorscale_bar_berm_widening(fig)


def add_measure_investment_year_trace(
        fig: go.Figure, section: DikeSection, measure_results: dict, legend_display: dict
):
    """
    This function adds a trace to the figure for the investment year.
    :param fig:
    :param section:
    :param measure_results:
    :param legend_display:
    :return:
    """
    _group = str(max(measure_results["investment_year"]) + REFERENCE_YEAR)
    _color = get_color(
        max(measure_results["investment_year"]) + REFERENCE_YEAR,
        cmap=plt.cm.Dark2,
        vmin=2025,
        vmax=2075,
    )
    _hovertemplate = ""

    if _group in legend_display.keys():
        showlegend = False
    else:
        showlegend = True
        legend_display[_group] = True

    add_section_trace(
        fig,
        section,
        name=_group,
        color=_color,
        hovertemplate=_hovertemplate,
        legendgroup=_group,
        showlegend=showlegend,
    )


def add_section_trace(
        fig: go.Figure,
        section: DikeSection,
        name: str,
        color: str,
        hovertemplate: str,
        showlegend: bool = False,
        legendgroup: str = None,
        opacity: float = 1,
        width: int = 10,
):
    """
    Add a trace of a section to the figure which the given specifications for color and hover, etc...
    """
    _coordinates_wgs = [
        GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in section.coordinates_rd
    ]  # convert in GWS coordinates:

    fig.add_trace(
        go.Scattermap(
            mode="lines",
            lat=[x[0] for x in _coordinates_wgs],
            lon=[x[1] for x in _coordinates_wgs],
            marker={"size": 10, "color": color},
            line={"width": width, "color": color},
            name=name,
            opacity=opacity,
            legendgroup=legendgroup,
            hovertemplate=hovertemplate,
            showlegend=showlegend,
        )
    )


def dike_traject_pf_cost_helping_map_detail(
        dike_traject: DikeTraject, curve_number: int, reinforced_sections: list[str]
) -> go.Figure:
    """
    Args:
        dike_traject:
        curve_number:
        reinforced_sections:

    Returns:

    """
    fig = go.Figure()
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
    if curve_number == 2:  # for the VR pad, we don't store the measures for each section, so we can't make this plot
        return plot_default_overview_map_dummy()

    for section in dike_traject.dike_sections:

        # if a section is not in analyse, skip it, and it turns blank on the map.
        if not section.in_analyse:
            continue

        _measure_results = (
            section.final_measure_doorsnede
            if curve_number == 0
            else section.final_measure_veiligheidsrendement
        )
        if _measure_results is not None:
            opacity = 1 if section.name == reinforced_sections[-1] else 0.2
            add_measure_type_trace(
                fig, section, _measure_results, _legend_display, opacity
            )

    # Update layout of the figure and add token for mapbox
    _middle_point = get_middle_point(dike_traject.dike_sections)
    update_layout_map_box(fig, _middle_point)

    return fig


def dike_traject_pf_cost_helping_map_simple(
        dike_traject: DikeTraject, curve_number: int, reinforced_sections: list[str]
) -> go.Figure:
    """

    :param dike_traject:
    :param curve_number: number of the curve in the pf-cost curve. 0 is veiligheid, 1 is doorsnede
    :param reinforced_sections: list of all the reinforced sections until the clicked section
    :return:
    """
    fig = go.Figure()

    for section in dike_traject.dike_sections:

        # if a section is not in analyse, skip it, and it turns blank on the map.
        if not section.in_analyse:
            continue

        if section.name == reinforced_sections[-1]:
            _color = "blue" if curve_number == 0 else "green"
            _opacity = 1
        elif (
                section.name in reinforced_sections
                and section.name != reinforced_sections[-1]
        ):
            _color = "blue" if curve_number == 0 else "green"
            _opacity = 0.4
        else:
            _color = "grey"
            _opacity = 1
        _hovertemplate = f"Vaknaam {section.name}<br>" + "<extra></extra>"

        add_section_trace(
            fig,
            section,
            name=dike_traject.name,
            color=_color,
            hovertemplate=_hovertemplate,
            opacity=_opacity,
        )

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

    middle_point_rd = (
        (first_point[0] + last_point[0]) / 2,
        (first_point[1] + last_point[1]) / 2,
    )
    # convert in gws coordinates:
    middle_point_gws = GWSRDConvertor().to_wgs(middle_point_rd[0], middle_point_rd[1])
    return middle_point_gws


def get_average_point(sections: list[DikeSection]) -> tuple[float, float]:
    avg_lat = sum([section.coordinates_rd[0][0] for section in sections]) / len(sections)
    avg_lon = sum([section.coordinates_rd[0][1] for section in sections]) / len(sections)
    return GWSRDConvertor().to_wgs(avg_lat, avg_lon)


def update_layout_map_box(fig: go.Figure, center: tuple[float, float], zoom: int = 11):
    """Update layout of Mapbox figure.

    :param fig: go.Figure object.
    :param center: tuple of the center point in GWS coordinates.
    :param zoom: int of the zoom level of the map.

    """
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        map=dict(
            center=dict(lat=center[0], lon=center[1]),
            zoom=zoom,
        ),
    )


def place_legend_left_top_corner(fig: go.Figure):
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
    ))


def place_legend_right_top_corner(fig: go.Figure):
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.95,
        xanchor="right",
        x=0.99,
    ))


def add_colorscale_bar(
        fig: go.Figure,
        result_type: str,
        colorbar_result_type: str,
        sub_result_type: str,
        lower_bound_pf: float,
):
    """Add a dummy scatter trace to the figure to show the colorscale bar

    :param fig: go.Figure object.
    :param result_type: type of results to show: "PROBABILITY" or "RELIABILITY".
    :param colorbar_result_type: type of colorbar to show: "RELIABILITY", "COST" or "MEASURE".
    """

    if (
            colorbar_result_type == ColorBarResultType.RELIABILITY.name
            and result_type == ResultType.PROBABILITY.name
            and sub_result_type == SubResultType.ABSOLUTE.name
    ):
        beta_ondergrsns = pf_to_beta(lower_bound_pf)
        # This colorbar is centered around pf 1/10000
        marker = dict(
            colorscale="RdYlGn",
            colorbar=dict(
                title="Faalkans",
                titleside="right",
                tickmode="array",
                tickvals=[
                    2.3263478740408408,
                    3.090232306167813,
                    beta_ondergrsns,
                    4.264890793922825,
                    4.753424308822899,
                ],
                ticktext=["1e-2", "1e-3", "1e-4", "1e-5", "1e-6"],
                ticks="outside",
                len=0.5,
                x=0.9,
                xref="paper",  # Superpose the colobar with the map
            ),
            showscale=True,
            cmin=beta_ondergrsns - 1.5,
            cmax=beta_ondergrsns + 1.5,
        )
    elif (
            colorbar_result_type == ColorBarResultType.RELIABILITY.name
            and result_type == ResultType.RELIABILITY.name
            and sub_result_type == SubResultType.ABSOLUTE.name
    ):
        beta_ondergrsns = pf_to_beta(lower_bound_pf)

        marker = dict(
            colorscale="RdYlGn",
            colorbar=dict(
                title="Betrouwbaarheid index",
                titleside="right",
                tickmode="array",
                tickvals=[2, 3, beta_ondergrsns, 4, 5],
                ticktext=["2", "3", str(round(beta_ondergrsns, 1)), "4", "5"],
                ticks="outside",
                len=0.5,
                x=0.9,
                xref="paper",  # Superpose the colobar with the map
            ),
            showscale=True,
            cmin=beta_ondergrsns - 1.5,
            cmax=beta_ondergrsns + 1.5,
        )
    elif (
            colorbar_result_type == ColorBarResultType.RELIABILITY.name
            and sub_result_type == SubResultType.RATIO.name
    ):
        marker = dict(
            colorscale="BrBG",
            reversescale=True,
            colorbar=dict(
                title="Verhouding pf vr/dsn",
                titleside="right",
                tickmode="array",
                tickvals=[-2, -1, 0, 1, 2],
                ticktext=["0.01", "0.1", "1", "10", "100"],
                ticks="outside",
                len=0.5,
            ),
            showscale=True,
            cmin=-2,
            cmax=2,
        )

    elif (
            colorbar_result_type == ColorBarResultType.COST.name
            and sub_result_type == SubResultType.ABSOLUTE.name
    ):
        marker = dict(
            colorscale="RdYlGn",
            reversescale=True,
            colorbar=dict(
                title="Kosten (M€/km)",
                titleside="right",
                tickmode="array",
                tickvals=[0, 5, 10, 15, 20],
                ticktext=["0", "5", "10", "15", "20"],
                ticks="outside",
                len=0.5,
            ),
            showscale=True,
            cmin=0,
            cmax=20,
        )

    elif (
            colorbar_result_type == ColorBarResultType.COST.name
            and sub_result_type == SubResultType.DIFFERENCE.name
    ):
        marker = dict(
            colorscale="RdYlGn",
            reversescale=True,
            colorbar=dict(
                title="Kosten (M€/km)",
                titleside="right",
                tickmode="array",
                tickvals=[-10, 0, 10],
                ticktext=["-10", "0", "10"],
                ticks="outside",
                len=0.5,
            ),
            showscale=True,
            cmin=-10,
            cmax=7,
        )

    elif result_type == ResultType.INTERPRETATION_CLASS.name:
        names = ["VI", "V", "IV", "III", "II", "I"]
        colors = ["#800000", "#FF6347", "#FFA500", "#FFD700", "#98FB98", "#7FFF00"]
        for name, color in zip(names, colors):
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker=dict(color=color),
                    name=name,
                    hoverinfo="none",
                    showlegend=True,
                )
            )
            fig.update_layout(legend=dict(title="WBI klasse"))

        # remove ticks from dummy scatter plot
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)

        return

    fig.add_trace(
        go.Scatter(
            x=[None, None],
            y=[None, None],
            mode="markers",
            showlegend=False,
            marker=marker,
            hoverinfo="none",
        )
    )

    # remove ticks from dummy scatter plot
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)


def add_colorscale_bar_crest_heigtening(fig: go.Figure):
    marker = dict(
        colorscale="Blues",
        colorbar=dict(
            title="Kruinverhoging (m)",
            titleside="right",
            tickmode="array",
            tickvals=[0, 0.5, 1, 1.5, 2],
            ticktext=["0", "0.5", "1", "1.5", "2"],
            ticks="outside",
            len=0.5,
        ),
        showscale=True,
        cmin=0,
        cmax=2,
    )
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            showlegend=False,
            marker=marker,
            hoverinfo="none",
        )
    )

    # remove ticks from dummy scatter plot
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)


def add_colorscale_bar_berm_widening(fig: go.Figure):
    marker = dict(
        colorscale="Greens",
        colorbar=dict(
            title="Bermverbreding (m)",
            titleside="right",
            tickmode="array",
            tickvals=[0, 10, 20, 30],
            ticktext=["0", "10", "20", "30"],
            ticks="outside",
            len=0.5,
        ),
        showscale=True,
        cmin=0,
        cmax=30,
    )
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            showlegend=False,
            marker=marker,
            hoverinfo="none",
        )
    )

    # remove ticks from dummy scatter plot
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)


def get_interpretation_class_color(
        beta_value: float, p_signal: float, p_lower_bound: float
) -> str:
    """

    :param beta_value: reliability index for the selected mechanism (or section)
    :param p_signal: signaleringswaarde for the dijktraject
    :param p_lower_bound: ondergrens for the dijktraject (pmax in the database)
    :return:
    """
    pf_value = beta_to_pf(beta_value)
    if pf_value < 1 / 1000 * p_signal:
        return "#006400"  # dark green
    elif 1 / 1000 * p_signal < pf_value < 1 / 100 * p_signal:
        return "#7FFF00"  # lawn green
    elif 1 / 100 * p_signal < pf_value < 1 / 10 * p_signal:
        return "#98FB98"  # pale green
    elif 1 / 10 * p_signal < pf_value < p_signal:
        return "#FFD700"  # gold
    elif p_signal < pf_value < p_lower_bound:
        return "#FFA500"  # orange
    elif p_lower_bound < pf_value < 10 * p_lower_bound:
        return "#FF6347"  # tomato
    elif 10 * p_lower_bound < pf_value:
        return "#800000"  # scarlet


def get_color_class_WBI(beta_values) -> tuple[str, str]:
    if beta_values < 2.75:
        return "purple", "IV"
    elif 2.75 <= beta_values < 3.72:
        return "red", "V"
    elif 3.72 <= beta_values < 4.78:
        return "orange", "IV"
    elif 4.78 <= beta_values < 5:
        return "yellow", "III"
    elif 5 <= beta_values < 5.62:
        return "lightgreen", "II"
    elif beta_values >= 5.62:
        return "green", "I"


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
    return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"



def get_color_plotly(value: float, colorscale: "PlotlyColorscale", vmin: float, vmax: float) -> str:
    """
    Return the color of the value on a colorscale, as an RGB string using Plotly.
    :param value: value for which a color must be assigned
    :param colorscale: color scale theme (e.g., 'Viridis', 'Cividis', etc.)
    :param vmin: min value of the color scale
    :param vmax: max value of the color scale
    :return: color as an RGB string
    """
    # Normalize the value to the range [0, 1]
    normalized_value = (value - vmin) / (vmax - vmin)
    normalized_value = max(0, min(1, normalized_value))  # Clamp to [0, 1]

    # Sample the color from the colorscale
    rgb_tuple = plotly.colors.sample_colorscale(colorscale, [normalized_value], colortype='rgb')[0]
    return rgb_tuple







def get_reliability_color(reliability_value: float, center_pf: float) -> str:
    """
    Return the color of the reliability value Beta on a colorscale from 2 (scarlet) to 5 (green), as a rgb string.
    :param reliability_value:
    :param center_pf: probability for which the color scale is centered
    :return:
    """
    beta_center = pf_to_beta(center_pf)
    cmin = beta_center - 1.5  # corresponds to pf=1/100
    cmax = beta_center + 1.5  # corresponds to pf=1/100000
    return get_color(reliability_value, plt.cm.RdYlGn, cmin, cmax)


def get_probability_ratio_color(probability_ratio: float) -> str:
    cmap = plt.cm.BrBG  # theme of the colorscale
    cmap = cmap.reversed()
    return get_color(np.log10(probability_ratio), cmap, -2, 2)  # from 0.01 to 100


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
    return get_color(cost_value, cmap, -10, 7)


def get_crest_heightening_color(crest_hightening_value) -> str:
    """
    Return the color of the crest heightening value on a colorscale from 0m (white) to 2m (dark blue), as a rgb string.
    :param crest_hightening_value: value of the heightening of the crest
    :return:
    """
    cmap = plt.cm.Blues
    return get_color(crest_hightening_value, cmap, 0, 2)


def get_berm_widening_color(berm_widening_value: float) -> str:
    """
    Return the color of the berm widening value on a colorscale from 0m (white) to 2m (dark blue), as a rgb string.
    :param berm_widening_value: value of the heightening of the crest
    :return:
    """
    cmap = plt.cm.Greens
    return get_color(berm_widening_value, cmap, 0, 30)

def get_veiligheidsrendemeent_index_color(vr_index: int) -> str:
    colorscale = px.colors.diverging.Geyser
    power = int(np.log10(vr_index))
    return get_color_plotly(power, colorscale, 0, 3)


def get_color_hover_prob_ratio(
        section: DikeSection, year_index: int, mechanism_type: str
) -> Tuple[str, str]:
    if (
            section.final_measure_veiligheidsrendement is None
            or section.final_measure_doorsnede is None
    ):
        _color = "grey"
        _hovertemplate = f"Vaknaam {section.name}<br>" f"Beta: NO DATA<br>"
    else:
        _beta_vr = get_beta(
            section.final_measure_veiligheidsrendement, year_index, mechanism_type
        )
        _beta_dsn = get_beta(
            section.final_measure_doorsnede, year_index, mechanism_type
        )
        _ratio_pf = beta_to_pf(_beta_vr) / beta_to_pf(_beta_dsn)
        _color = get_probability_ratio_color(_ratio_pf)

        _hovertemplate = (
            f"Vaknaam {section.name}<br>"
            f"Pf Veiligheidsrendement: {beta_to_pf(_beta_vr):.2e}<br>"
            f"Pf Doorsnede: {beta_to_pf(_beta_dsn):.2e}<br>"
            f"Ratio Pf vr/dsn: {round(_ratio_pf, 1)}<br>"
            f"<extra></extra>"
        )

    return _color, _hovertemplate


def get_color_hover_absolute_reliability(
        section: DikeSection,
        beta_section: float,
        measure_results: dict,
        pf_lower_bound: float,
) -> Tuple[str, str]:
    _color = get_reliability_color(beta_section, pf_lower_bound)

    _hovertemplate = (
        f"Vaknaam {section.name}<br>"
        f'Maatregel: {measure_results["name"]}<br>'
        f'LCC: {to_million_euros(measure_results["LCC"])} M€<br>'
        f"Beta sectie: {beta_section:.2}<br>"
        f"Pf sectie: {beta_to_pf(beta_section):.2e}<br>"
        f"<extra></extra>"
    )

    return _color, _hovertemplate


def get_color_hover_absolute_cost(
        section: DikeSection, beta_section: float, measure_results: dict
) -> Tuple[str, str]:
    _cost_per_kilometer = to_million_euros(
        measure_results["LCC"] / (section.length / 1e3)
    )

    _color = get_cost_color(_cost_per_kilometer)
    _hovertemplate = (
        f"Vaknaam {section.name} : {section.length}m<br>"
        f'Maatregel: {measure_results["name"]}<br>'
        f'Kosten sectie: {to_million_euros(measure_results["LCC"])} M€<br>'
        f"Kosten per kilometers: {_cost_per_kilometer} M€/km<br>"
        f"Beta sectie: {beta_section:.2}<br>"
        f"Pf sectie: {beta_to_pf(beta_section):.2e}<br>"
        f"<extra></extra>"
    )

    return _color, _hovertemplate


def get_color_hover_difference_cost(section: DikeSection) -> Tuple[str, str]:
    if (
            section.final_measure_veiligheidsrendement is None
            or section.final_measure_doorsnede is None
    ):
        _color = "grey"
        _hovertemplate = (
            f"Vaknaam {section.name}<br>" f"Beta: NO DATA<br>" f"<extra></extra>"
        )
    else:
        _cost_vr = section.final_measure_veiligheidsrendement["LCC"]
        _cost_dsn = section.final_measure_doorsnede["LCC"]
        _diff = _cost_vr - _cost_dsn
        _diff_per_kilometer = to_million_euros(_diff / (section.length / 1e3))

        _color = get_color_diff_cost(_diff_per_kilometer)

        _hovertemplate = (
            f"Vaknaam {section.name} : {section.length}m<br>"
            f"Kosten Veiligheidsrendement: {to_million_euros(_cost_vr)} M€<br>"
            f"Kosten Doorsnede: {to_million_euros(_cost_dsn)} M€<br>"
            f"Kostenverschil: {to_million_euros(_diff)} M€<br>"
            f"Kostenverschil per kilometer: {_diff_per_kilometer} M€/km<br>"
            f"<extra></extra>"
        )

    return _color, _hovertemplate


def get_no_data_info(section: DikeSection) -> Tuple[str, str]:
    _color = "grey"
    _hovertemplate = (
            f"Vaknaam {section.name}<br>" f"Beta: NO DATA<br>" + "<extra></extra>"
    )
    return _color, _hovertemplate


def get_investment_year_str(investement_years: list[int]) -> str:
    string = ""
    for year in investement_years:
        year = year + REFERENCE_YEAR
        string = string + f"{year} + "
    return string[:-3]
