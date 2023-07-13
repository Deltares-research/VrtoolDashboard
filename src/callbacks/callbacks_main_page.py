from dash import html, dcc, Output, Input, State

from src.constants import ColorBarResultType, SubResultType
from src.layouts.layout_main_page import layout_tab_one, layout_tab_two, layout_tab_three, layout_tab_four, \
    layout_tab_five
from src.layouts.layout_radio_items import layout_radio_calc_type
from src.linear_objects.dike_traject import DikeTraject
from src.plotly_graphs.pf_length_cost import plot_pf_length_cost, plot_default_scatter_dummy
from src.plotly_graphs.plotly_maps import plot_overview_map_dummy, plot_default_overview_map_dummy, \
    plot_dike_traject_reliability_initial_assessment_map, plot_dike_traject_reliability_measures_assessment_map, \
    plot_dike_traject_urgency
from src.app import app


@app.callback([Output('output-data-upload-zip', 'children'),
               Output("upload-toast", "is_open"), ],
              [Input('upload-data-zip', 'contents')],
              [State('upload-data-zip', 'filename')])
def upload_and_save_traject_input(contents: str, filename: str, dbc=None) -> tuple:
    """This is the callback for the upload of the zip files of the traject data.

    :param contents: string content of the uploaded zip file. The zip should content at least:
        - a geojson file with the dike data
        - a csv file with the results of the Veiligheidrendement method.

    :param filename: name of the uploaded zip file.

    :return: Return a tuple with:
        - html.Div with the serialized dike traject data.
        - boolean indicating if the upload was successful.
    """
    if contents is not None:
        try:
            _dike_traject = DikeTraject.from_uploaded_zip(contents, filename)
            return html.Div(
                dcc.Store(id='stored-data', data=_dike_traject.serialize())), True
        except:
            return html.Div(children=["Something went wrong when uploading the file"]), False
    else:
        return html.Div("Geen bestand geüpload"), False


@app.callback(Output('overview_map_div', 'children'),
              [Input('stored-data', 'data'), Input("select_calculation_type", 'value')])
def make_graph_overview_dike(dike_traject_data: dict, selected_result_type) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data:

    """
    if dike_traject_data is None:
        _fig = plot_default_overview_map_dummy()
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        _fig = plot_overview_map_dummy(_dike_traject, selected_result_type)
    return dcc.Graph(figure=_fig, style={'width': '100%', 'height': '100%'})


@app.callback(Output('dike_traject_reliability_map_initial', 'children'),
              [Input('stored-data', 'data'), Input("slider_year_reliability_results", "value"),
               Input("select_result_type", 'value'), Input("select_mechanism_type", 'value')])
def make_graph_map_initial_assessment(dike_traject_data: dict, selected_year: float, result_type: str,
                                      mechanism_type: str) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data:
    :param selected_year: Selected year by the user from the slider
    :param result_type: Selected result type by the user from the OptionField, one of "RELIABILITY" or "PROBABILITY"
    :param mechanism_type: Selected mechanism type by the user from the OptionField, one of "PIPING", "STABILITY",
    "OVERFLOW" or "SECTION"

    :return: dcc.Graph with the plotly figure

    """
    if dike_traject_data is None:
        _fig = plot_default_overview_map_dummy()
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        _fig = plot_dike_traject_reliability_initial_assessment_map(_dike_traject, selected_year, result_type,
                                                                    mechanism_type)
    return dcc.Graph(figure=_fig, style={'width': '100%', 'height': '100%'})


@app.callback(Output('dike_traject_reliability_map_measures', 'children'),
              [Input('stored-data', 'data'), Input("slider_year_reliability_results", "value"),
               Input("select_result_type", 'value'), Input("select_calculation_type", "value"),
               Input("select_measure_map_result_type", "value"), Input("select_mechanism_type", 'value'),
               Input("select_sub_result_type_measure_map", "value")])
def make_graph_map_measures(dike_traject_data: dict, selected_year: float, result_type: str,
                            calc_type: str, color_bar_result_type: str, mechanism_type: str,
                            sub_result_type: str) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data:
    :param selected_year: Selected year by the user from the slider
    :param result_type: Selected result type by the user from the OptionField, one of "RELIABILITY" or "PROBABILITY"
    :param calc_type: Selected calculation type by the user from the OptionField, one of "VEILIGHEIDRENDEMENT" or "DOORSNEDE"
    :param color_bar_result_type: Select which type of colored result must be displayed on the map for the measures: either
    show the reliability, the cost of the type of measure. Must be one of "RELIABILITY" or "COST" or "MEASURE",
    :param mechanism_type: Selected mechanism type by the user from the OptionField, one of "PIPING", "STABILITY",
    "OVERFLOW" or "SECTION"
    :param sub_result_type: Selected sub result type by the user from the OptionField, one of "ABSOLUTE" or "DIFFERENCE"
    or "RATIO"

    :return: dcc.Graph with the plotly figure
    """
    if dike_traject_data is None:
        _fig = plot_default_overview_map_dummy()
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        _fig = plot_dike_traject_reliability_measures_assessment_map(_dike_traject, selected_year, result_type,
                                                                     calc_type, color_bar_result_type, mechanism_type,
                                                                     sub_result_type)
    return dcc.Graph(figure=_fig, style={'width': '100%', 'height': '100%'})


@app.callback(Output('dike_traject_pf_cost_graph', 'children'),
              [Input('stored-data', 'data'), Input("slider_year_reliability_results", "value"),
               Input("select_result_type", 'value'), Input("select_length_cost_switch", "value")])
def make_graph_pf_vs_cost(dike_traject_data: dict, selected_year: float, result_type: str,
                          cost_length_switch: str) -> dcc.Graph:
    """
    Call to display the graph of the plot of the probability of failure vs the cost of the measures.

    :param dike_traject_data:
    :param selected_year: Selected year by the user from the slider
    :param result_type: Selected result type by the user from the OptionField, one of "RELIABILITY" or "PROBABILITY"
    :param cost_length_switch: Selected cost length switch by the user from the OptionField, one of "COST" or "LENGTH"

    """
    if dike_traject_data is None:
        _fig = plot_default_scatter_dummy()
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        _fig = plot_pf_length_cost(_dike_traject, selected_year, result_type, cost_length_switch)
    return dcc.Graph(figure=_fig, style={'width': '100%', 'height': '100%'})


@app.callback(Output('dike_traject_urgency_map', 'children'),
              [Input('stored-data', 'data'), Input("slider_year_reliability_results", "value"),
               Input("slider_urgency_length", "value"), Input("select_calculation_type", "value")])
def make_graph_map_urgency(dike_traject_data: dict, selected_year: float, length_urgency: float,
                           calc_type: str) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data:
    :param selected_year: Selected year by the user from the slider
    :param length_urgency: Selected length of the urgency by the user from the slider
    :param calc_type: Selected calculation type by the user from the OptionField, one of "VEILIGHEIDRENDEMENT" or "DOORSNEDE"

    or "RATIO"

    :return: dcc.Graph with the plotly figure
    """
    if dike_traject_data is None:
        _fig = plot_default_overview_map_dummy()
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        _fig = plot_dike_traject_urgency(_dike_traject, selected_year, length_urgency, calc_type)
    return dcc.Graph(figure=_fig, style={'width': '100%', 'height': '100%'})


@app.callback(
    [Output("content_tab", "children"), Output("select_calculation_type", "options")],
    [Input("tabs", "active_tab")]
)
def render_tab_map_content(active_tab: str) -> html.Div:
    """
    Renders the content of the selected tab for the general overview page.
    :param active_tab:
    :return:
    """

    base_layout_calc_type = layout_radio_calc_type
    disabled_calc_type = [{'label': option['label'], 'value': option['value'], 'disabled': True} for option in
                          base_layout_calc_type.options]

    if active_tab == "tab-1":
        return layout_tab_one(), disabled_calc_type
    elif active_tab == "tab-2":
        return layout_tab_two(), disabled_calc_type
    elif active_tab == "tab-3":
        return layout_tab_three(), base_layout_calc_type.options
    elif active_tab == "tab-4":
        return layout_tab_four(), base_layout_calc_type.options
    elif active_tab == "tab-5":
        return layout_tab_five(), base_layout_calc_type.options
    else:
        return html.Div("Invalid tab selected")


@app.callback(
    Output("collapse_1", "is_open"),
    [Input("collapse_button_1", "n_clicks")],
    [State("collapse_1", "is_open")],
)
def toggle_collapse(n: int, is_open: bool):
    """
    Callback to toggle the collapse of the first section.
    :param n: dummy integer
    :param is_open: boolean indicating if the collapse is open or not.
    :return:
    """
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse_2", "is_open"),
    [Input("collapse_button_2", "n_clicks")],
    [State("collapse_2", "is_open")],
)
def toggle_collapse2(n: int, is_open: bool):
    """
    Callback to toggle the collapse of the second section.
    :param n: dummy integer
    :param is_open: boolean indicating if the collapse is open or not.
    :return:
    """
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse_3", "is_open"),
    [Input("collapse_button_3", "n_clicks")],
    [State("collapse_3", "is_open")],
)
def toggle_collapse3(n: int, is_open: bool):
    """
    Callback to toggle the collapse of the second section.
    :param n: dummy integer
    :param is_open: boolean indicating if the collapse is open or not.
    :return:
    """
    if n:
        return not is_open
    return is_open


@app.callback(
    Output('select_sub_result_type_measure_map', 'options'),
    Input('select_measure_map_result_type', 'value'),
)
def update_radio_sub_result_type(result_type: str) -> dcc:
    """
    This is a callback to update the sub Radio list depending on the result type selected by the user.
    If the result type is "RELIABILITY" then the sub Radio list will contain the options "Absoluut" and "Ratio vr/dsn".
    If the result type is "COST" then the sub Radio list will contain the options "Absoluut" and "Verschil vr-dsn".

    :param value: one of "RELIABILITY" or "COST" or "MEASURE"
    :return:
    """
    if result_type == ColorBarResultType.RELIABILITY.name:
        options = [
            {'label': SubResultType.ABSOLUTE.value, 'value': SubResultType.ABSOLUTE.name},
            {'label': SubResultType.RATIO.value, 'value': SubResultType.RATIO.name},
        ]
    elif result_type == ColorBarResultType.COST.name:
        options = [
            {'label': SubResultType.ABSOLUTE.value, 'value': SubResultType.ABSOLUTE.name},
            {'label': SubResultType.DIFFERENCE.value, 'value': SubResultType.DIFFERENCE.name},
        ]
    else:
        options = []

    return options
