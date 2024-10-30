from bisect import bisect_right
from pathlib import Path

import dash
from dash import dcc, Output, Input, callback, State
from plotly.graph_objs import Figure
from vrtool.defaults.vrtool_config import VrtoolConfig

from src.component_ids import (
    SLIDER_YEAR_RELIABILITY_RESULTS_ID,
    SELECT_DIKE_SECTION_FOR_MEASURES_ID,
    GRAPH_MEASURE_COMPARISON_ID,
    STORE_CONFIG, MEASURE_MODAL_ID, CLOSE_MEASURE_MODAL_BUTTON_ID, DIKE_TRAJECT_PF_COST_GRAPH_ID,
    GRAPH_MEASURE_RELIABILITY_TIME_ID
)
from src.constants import REFERENCE_YEAR, Mechanism
from src.linear_objects.dike_traject import DikeTraject
from src.orm.import_database import get_all_measure_results, get_measure_reliability_over_time
from src.plotly_graphs.measure_comparison_graph import plot_measure_results_graph
from src.plotly_graphs.measure_reliability_time import plot_measure_results_over_time_graph, \
    update_measure_results_over_time_graph
from src.plotly_graphs.pf_length_cost import (
    plot_pf_length_cost,
    plot_default_scatter_dummy,
)
from src.plotly_graphs.plotly_maps import (
    plot_overview_map,
    plot_default_overview_map_dummy,
    plot_dike_traject_reliability_initial_assessment_map,
    plot_dike_traject_reliability_measures_assessment_map,
    plot_dike_traject_urgency,
    dike_traject_pf_cost_helping_map_simple, dike_traject_pf_cost_helping_map_detail,
)
from src.utils.utils import export_to_json, get_default_plotly_config, get_plotly_config


@callback(Output("overview_map_div", "children"), [Input("stored-data", "data")])
def make_graph_overview_dike(dike_traject_data: dict) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data: The data of the dike traject to be displayed.
    """

    export_to_json(dike_traject_data)

    if dike_traject_data is None or dike_traject_data == {}:
        _fig = plot_default_overview_map_dummy()
    else:

        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        _fig = plot_overview_map(_dike_traject)
    return dcc.Graph(
        figure=_fig,
        style={"width": "100%", "height": "100%"},
    )


@callback(
    Output("dike_traject_reliability_map_initial", "children"),
    [
        Input("stored-data", "data"),
        Input(SLIDER_YEAR_RELIABILITY_RESULTS_ID, "value"),
        Input("select_result_type", "value"),
        Input("select_mechanism_type", "value"),
    ],
)
def make_graph_map_initial_assessment(
        dike_traject_data: dict, selected_year: float, result_type: str, mechanism_type: str
) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data: The data of the dike traject to be displayed.
    :param selected_year: Selected year by the user from the slider
    :param result_type: Selected result type by the user from the OptionField, one of "RELIABILITY" or "PROBABILITY"
    :param mechanism_type: Selected mechanism type by the user from the OptionField, one of "PIPING", "STABILITY",
    "OVERFLOW", "REVETMENT" or "SECTION"

    :return: dcc.Graph with the plotly figure

    """
    if dike_traject_data is None:
        _fig = plot_default_overview_map_dummy()
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        _fig = plot_dike_traject_reliability_initial_assessment_map(
            _dike_traject, selected_year, result_type, mechanism_type
        )
    return dcc.Graph(
        figure=_fig,
        style={"width": "100%", "height": "100%"},
        config=get_plotly_config("TESTNAME", height=500, width=700),
    )


@callback(
    Output("dike_traject_reliability_map_measures", "children"),
    [
        Input("stored-data", "data"),
        Input(SLIDER_YEAR_RELIABILITY_RESULTS_ID, "value"),
        Input("select_result_type", "value"),
        Input("select_calculation_type", "value"),
        Input("select_measure_map_result_type", "value"),
        Input("select_mechanism_type", "value"),
        Input("select_sub_result_type_measure_map", "value"),
    ],
)
def make_graph_map_measures(
        dike_traject_data: dict,
        selected_year: float,
        result_type: str,
        calc_type: str,
        color_bar_result_type: str,
        mechanism_type: str,
        sub_result_type: str,
) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data: The data of the dike traject to be displayed.
    :param selected_year: Selected year by the user from the slider
    :param result_type: Selected result type by the user from the OptionField, one of "RELIABILITY" or "PROBABILITY"
    :param calc_type: Selected calculation type by the user from the OptionField, one of "VEILIGHEIDSRENDEMENT" or "DOORSNEDE"
    :param color_bar_result_type: Select which type of colored result must be displayed on the map for the measures: either
    show the reliability, the cost of the type of measure. Must be one of "RELIABILITY" or "COST" or "MEASURE",
    :param mechanism_type: Selected mechanism type by the user from the OptionField, one of "PIPING", "STABILITY",
    "OVERFLOW", "REVETMENT or "SECTION"
    :param sub_result_type: Selected sub result type by the user from the OptionField, one of "ABSOLUTE" or "DIFFERENCE"
    or "RATIO"

    :return: dcc.Graph with the plotly figure
    """
    if dike_traject_data is None:
        _fig = plot_default_overview_map_dummy()
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        _fig = plot_dike_traject_reliability_measures_assessment_map(
            _dike_traject,
            selected_year,
            result_type,
            calc_type,
            color_bar_result_type,
            mechanism_type,
            sub_result_type,
        )
    return dcc.Graph(
        figure=_fig,
        style={"width": "100%", "height": "100%"},
    )


@callback(
    Output(DIKE_TRAJECT_PF_COST_GRAPH_ID, "figure"),
    [
        Input("stored-data", "data"),
        Input(SLIDER_YEAR_RELIABILITY_RESULTS_ID, "value"),
        Input("select_result_type", "value"),
        Input("select_length_cost_switch", "value"),
    ],
)
def make_graph_pf_vs_cost(
        dike_traject_data: dict,
        selected_year: float,
        result_type: str,
        cost_length_switch: str,
):
    """
    Call to display the graph of the plot of the probability of failure vs the cost of the measures.

    :param dike_traject_data: The data of the dike traject to be displayed.
    :param selected_year: Selected year by the user from the slider
    :param result_type: Selected result type by the user from the OptionField, one of "RELIABILITY" or "PROBABILITY"
    :param cost_length_switch: Selected cost length switch by the user from the OptionField, one of "COST" or "LENGTH"
    """

    if dike_traject_data is None:
        return plot_default_scatter_dummy()
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        _fig = plot_pf_length_cost(
            _dike_traject, selected_year, result_type, cost_length_switch
        )
    return _fig


@callback(
    Output("dike_traject_urgency_map", "children"),
    [
        Input("stored-data", "data"),
        Input(SLIDER_YEAR_RELIABILITY_RESULTS_ID, "value"),
        Input("slider_urgency_length", "value"),
        Input("select_calculation_type", "value"),
    ],
)
def make_graph_map_urgency(
        dike_traject_data: dict, selected_year: float, length_urgency: float, calc_type: str
) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data: The data of the dike traject to be displayed.
    :param selected_year: Selected year by the user from the slider
    :param length_urgency: Selected length of the urgency by the user from the slider
    :param calc_type: Selected calculation type by the user from the OptionField, one of "VEILIGHEIDSRENDEMENT" or "DOORSNEDE"

    or "RATIO"

    :return: dcc.Graph with the plotly figure
    """
    if dike_traject_data is None:
        _fig = plot_default_overview_map_dummy()
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        _fig = plot_dike_traject_urgency(
            _dike_traject, selected_year, length_urgency, calc_type
        )
    return dcc.Graph(
        figure=_fig,
        style={"width": "100%", "height": "100%"},
    )


@callback(
    Output("dike_traject_pf_cost_helping_map", "figure"),
    Input("stored-data", "data"),
    Input(DIKE_TRAJECT_PF_COST_GRAPH_ID, "clickData"),
    Input("select_helper_map_switch", 'value')
)
def update_click(dike_traject_data: dict, click_data: dict, switch_map_helper_type: str) -> Figure:
    """
    Trigger callback when clicking over the Pf_vs_cost graph. This callback will update the accompanying map of the
    traject by highlighting the selected dike section.

    :param dike_traject_data: The data of the dike traject to be displayed.
    :param click_data: data obtained from Plotly API by clicking on the plot of Pf_vs_cost graph. This data
    is typically a dictionary with the structure:
    {'points': [{'curveNumber': 1, 'pointNumber': 40, 'pointIndex': 40, 'x': 103.3, 'y': 3.5, 'customdata': '33A', 'bbox': {'x0': 1194.28, 'x1': 1200.28, 'y0': 462.52, 'y1': 468.52}}]}
    :param switch_map_helper_type: Selected switch map helper type by the user from the OptionField, one of "SIMPLE" or "DETAIL"
    :return: Update the accompanying map of the Pf_vs_cost graph.
    """
    # TODO: the maps here does not need to be plotly! or at least not a MapBox
    if click_data is None:
        return plot_default_overview_map_dummy()
    elif dike_traject_data is None:
        return plot_default_overview_map_dummy()
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)

        _order = (
            _dike_traject.reinforcement_order_dsn
            if click_data["points"][0]["curveNumber"] == 0
            else _dike_traject.reinforcement_order_vr
        )
        _reinforced_sections = _order[: int(click_data["points"][0]["pointNumber"])]

        if switch_map_helper_type == "DETAILED":
            return dike_traject_pf_cost_helping_map_detail(_dike_traject, click_data["points"][0]["curveNumber"],
                                                           _reinforced_sections)
        else:
            return dike_traject_pf_cost_helping_map_simple(_dike_traject, click_data["points"][0]["curveNumber"],
                                                       _reinforced_sections)


### TAB Maatregelen ###


@callback(
    Output(SELECT_DIKE_SECTION_FOR_MEASURES_ID, "options"),
    Input("stored-data", "data"),
)
def fill_dike_section_selection(dike_traject_data: dict) -> list[dict]:
    """

    :return:
    """

    _option_list = []
    if dike_traject_data is not None:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)

        for section in _dike_traject.dike_sections:
            if section.in_analyse:
                _option_list.append({"label": section.name, "value": section.name})

    return _option_list


@callback(
    Output(GRAPH_MEASURE_COMPARISON_ID, "figure"),
    inputs=[
        Input("stored-data", "data"),
        Input(STORE_CONFIG, "data"),
        Input(SLIDER_YEAR_RELIABILITY_RESULTS_ID, "value"),
        Input(SELECT_DIKE_SECTION_FOR_MEASURES_ID, "value"),
        Input("select_mechanism_type", "value"),
    ],
)
def make_graph_measure_results_comparison(
        dike_traject_data: dict,
        vr_config: dict,
        selected_year: float,
        selected_dike_section: str,
        selected_mechanism: str,
) -> Figure:
    """

    :param dike_traject_data: The data of the dike traject to be displayed.
    :param vr_config: Stored configuration of the VRTool
    :param selected_year: Selected year by the user from the slider
    :param selected_dike_section: Selected dike section by the user from the Dropdown
    :param selected_mechanism: Selected mechanism to filter and display the betas.
    :param dike_data: The data of the dike traject to be displayed.

    :return:
    """
    if dike_traject_data is None:
        return plot_default_scatter_dummy()

    if selected_dike_section == "":
        return plot_default_scatter_dummy()

    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)

        _section = _dike_traject.get_section(selected_dike_section)
        _year_index = bisect_right(_section.years, selected_year - REFERENCE_YEAR) - 1
        _time = _section.years[_year_index]
        _vr_config = VrtoolConfig()
        _vr_config.traject = vr_config["traject"]
        _vr_config.input_directory = Path(vr_config["input_directory"])
        _vr_config.output_directory = Path(vr_config["output_directory"])
        _vr_config.input_database_name = vr_config["input_database_name"]
        _vr_config.T = vr_config["T"]

        _final_step_number = dike_traject_data["final_step_number"]
        _meas_results, _vr_steps, _dsn_steps = get_all_measure_results(
            _vr_config,
            _section.name,
            get_mechanism_name_ORM(selected_mechanism),
            _time,
            run_id_vr=dike_traject_data["_run_id_vr"],
            run_id_dsn=dike_traject_data["_run_id_dsn"],
            active_mechanisms=_section.active_mechanisms,
            final_step_number=_final_step_number,
        )

        _fig = plot_measure_results_graph(
            _meas_results,
            _vr_steps,
            _dsn_steps,
            selected_mechanism,
            _section.name,
            _year_index,
        )

    return _fig


@callback(
    output=[
        Output(MEASURE_MODAL_ID, "is_open", allow_duplicate=True),
        Output(CLOSE_MEASURE_MODAL_BUTTON_ID, "n_clicks"),
    ],
    inputs=[
        Input(CLOSE_MEASURE_MODAL_BUTTON_ID, "n_clicks"),
    ],
    prevent_initial_call=True,
)
def close_modal_measure_reliability_time(close_n_click: int
                                         ) -> tuple[bool, int]:
    """
    Dummy call to trigger the opening of the canvas so the `update_timestamp`
    can output the vrtool logging.
    """
    if close_n_click and close_n_click > 0:
        return False, 0
    return True, 0


@callback(output=[
    Output(MEASURE_MODAL_ID, "is_open"),
    Output(GRAPH_MEASURE_RELIABILITY_TIME_ID, "figure"),
    Output(GRAPH_MEASURE_COMPARISON_ID, "figure", allow_duplicate=True)
],
    inputs=[Input(GRAPH_MEASURE_COMPARISON_ID, "clickData"),
            ],
    state=[State("select_mechanism_type", "value"),
           State(STORE_CONFIG, "data"),
           State("stored-data", "data"),
           State(SELECT_DIKE_SECTION_FOR_MEASURES_ID, "value"),
           State(GRAPH_MEASURE_COMPARISON_ID, "figure"),
           ]
    ,
    prevent_initial_call=True,
)
def open_modal_measure_reliability_time(click_data: dict, selected_mechanism, vr_config, dike_traject_data: dict,
                                        section_name: str, fig: dict) -> tuple:
    """

    :param click_data: data clicked from the figure showing beta vs cost of all measures for a selected dike section.
    :param selected_mechanism:
    :param vr_config:
    :param dike_traject_data:
    :param section_name:
    :param fig: plotly figure object as a dict to which we want to modify

    :return:


    """

    if click_data is None:
        return False, plot_default_scatter_dummy(), dash.no_update

    if click_data["points"][0]["curveNumber"] == 0:

        _clicked_measure_result_id = click_data["points"][0]["customdata"][
            3]  # fourth position is the measure_result_id
        _measure_data = {"measure_name": click_data["points"][0]["customdata"][0],
                         "dberm": click_data["points"][0]["customdata"][1],
                         "dcrest": click_data["points"][0]["customdata"][2]}

        _vr_config = VrtoolConfig()
        _vr_config.traject = vr_config["traject"]
        _vr_config.input_directory = Path(vr_config["input_directory"])
        _vr_config.output_directory = Path(vr_config["output_directory"])
        _vr_config.input_database_name = vr_config["input_database_name"]
        _vr_config.T = vr_config["T"]

        _mechanism_name = get_mechanism_name_ORM(selected_mechanism)

        betas_meas = get_measure_reliability_over_time(_vr_config, _clicked_measure_result_id,
                                                       _mechanism_name)

        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        _years = _dike_traject.get_section(section_name).years

        _betas_ini = _dike_traject.get_section(section_name).initial_assessment[_mechanism_name]
        return True, plot_measure_results_over_time_graph(betas_meas, _betas_ini, selected_mechanism, section_name,
                                                          _years, _measure_data), dash.no_update
    else:
        _fig = update_measure_results_over_time_graph(fig, click_data)

        return False, plot_default_scatter_dummy(), _fig


def get_mechanism_name_ORM(mechanism: str) -> str:
    """
    Get the Mechanism object from the string representation of the mechanism.

    :param mechanism: String representation of the mechanism.
    :return: Mechanism object.
    """

    if mechanism == Mechanism.PIPING.name:
        return "Piping"
    elif mechanism == Mechanism.STABILITY.name:
        return "StabilityInner"
    elif mechanism == Mechanism.OVERFLOW.name:
        return "Overflow"
    elif mechanism == Mechanism.REVETMENT.name:
        return "Revetment"
    elif mechanism == Mechanism.SECTION.name:
        return "Section"
