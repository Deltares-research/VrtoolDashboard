from bisect import bisect_right
from pathlib import Path

from dash import dcc, Output, Input, callback
from plotly.graph_objs import Figure
from vrtool.defaults.vrtool_config import VrtoolConfig

from src.component_ids import (
    SLIDER_YEAR_RELIABILITY_RESULTS_ID,
    SELECT_DIKE_SECTION_FOR_MEASURES_ID,
    GRAPG_MEASURE_COMPARISON_ID,
    STORE_CONFIG,
)
from src.constants import REFERENCE_YEAR, get_mapbox_token, Mechanism
from src.linear_objects.dike_traject import DikeTraject
from src.orm.import_database import get_all_measure_results
from src.plotly_graphs.measure_comparison_graph import plot_measure_results_graph
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
    dike_traject_pf_cost_helping_map,
)
from src.utils.utils import export_to_json


@callback(Output("overview_map_div", "children"), [Input("stored-data", "data")])
def make_graph_overview_dike(dike_traject_data: dict) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data: The data of the dike traject to be displayed.
    """

    export_to_json(dike_traject_data)
    print(dike_traject_data)

    if dike_traject_data is None or dike_traject_data == {}:
        _fig = plot_default_overview_map_dummy()
    else:

        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        _fig = plot_overview_map(_dike_traject)
    return dcc.Graph(
        figure=_fig,
        style={"width": "100%", "height": "100%"},
        config={"mapboxAccessToken": get_mapbox_token()},
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
        config={"mapboxAccessToken": get_mapbox_token()},
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
        config={"mapboxAccessToken": get_mapbox_token()},
    )


@callback(
    Output("dike_traject_pf_cost_graph", "figure"),
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
        config={"mapboxAccessToken": get_mapbox_token()},
    )


@callback(
    Output("dike_traject_pf_cost_helping_map", "figure"),
    Input("stored-data", "data"),
    Input("dike_traject_pf_cost_graph", "clickData"),
)
def update_click(dike_traject_data: dict, click_data: dict) -> Figure:
    """
    Trigger callback when clicking over the Pf_vs_cost graph. This callback will update the accompanying map of the
    traject by highlighting the selected dike section.

    :param dike_traject_data: The data of the dike traject to be displayed.
    :param click_data: data obtained from Plotly API by clicking on the plot of Pf_vs_cost graph. This data
    is typically a dictionary with the structure:
    {'points': [{'curveNumber': 1, 'pointNumber': 40, 'pointIndex': 40, 'x': 103.3, 'y': 3.5, 'customdata': '33A', 'bbox': {'x0': 1194.28, 'x1': 1200.28, 'y0': 462.52, 'y1': 468.52}}]}
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

        return dike_traject_pf_cost_helping_map(
            _dike_traject, click_data["points"][0]["curveNumber"], _reinforced_sections
        )


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
            _option_list.append({"label": section.name, "value": section.name})

    return _option_list


@callback(
    Output(GRAPG_MEASURE_COMPARISON_ID, "figure"),
    [
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

        _meas_results, _vr_steps, _dsn_steps = get_all_measure_results(
            _vr_config,
            _section.name,
            get_mechanism_name_ORM(selected_mechanism),
            _time,
            run_id_vr=dike_traject_data["_run_id_vr"],
            run_id_dsn=dike_traject_data["_run_id_dsn"],
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

