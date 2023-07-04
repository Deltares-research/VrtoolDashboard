import dash
from dash import html, dcc, Output, Input, State

from src.layouts.layout_main_page import layout_tab_one, CalcType, layout_tab_two, layout_tab_three
from src.linear_objects.dike_traject import DikeTraject
from src.plotly_graphs.plotly_maps import plot_overview_map_dummy, plot_default_overview_map_dummy, \
    plot_dike_traject_reliability_initial_assessment_map, plot_dike_traject_reliability_measures_assessment_map
from src.app import app
from src.utils.utils import export_to_json


@app.callback([Output('output-data-upload-zip', 'children'),
               Output("upload-toast", "is_open")],
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
        # try:
        _dike_traject = DikeTraject.from_uploaded_zip(contents, filename)
        return html.Div(
        dcc.Store(id='stored-data', data=_dike_traject.serialize())), True
        # except:
        #     return html.Div(children=["The uploaded zip file does not contain the correct files"]), False
    else:
        return html.Div("No file has been uploaded yet"), False


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
              [Input('stored-data', 'data'), Input("slider_year_initial_reliability_results", "value"), Input("select_result_type_initial", 'value')])
def make_graph_initial_assessment(dike_traject_data: dict, selected_year: float, result_type: str) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data:

    """
    if dike_traject_data is None:
        _fig = plot_default_overview_map_dummy()
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        _fig = plot_default_overview_map_dummy()
        _fig = plot_dike_traject_reliability_initial_assessment_map(_dike_traject, selected_year, result_type)
    return dcc.Graph(figure=_fig, style={'width': '100%', 'height': '100%'})


@app.callback(Output('dike_traject_reliability_map_measures', 'children'),
              [Input('stored-data', 'data'), Input("slider_year_reliability_results_measures", "value"), Input("select_result_type_measures", 'value')])
def make_graph_initial_assessment(dike_traject_data: dict, selected_year: float, result_type: str) -> dcc.Graph:
    """
    Call to display the graph of the overview map of the dike from the saved imported dike data.

    :param dike_traject_data:

    """
    if dike_traject_data is None:
        _fig = plot_default_overview_map_dummy()
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        _fig = plot_default_overview_map_dummy()
        export_to_json(dike_traject_data)
        _fig = plot_dike_traject_reliability_measures_assessment_map(_dike_traject, selected_year, result_type)
    return dcc.Graph(figure=_fig, style={'width': '100%', 'height': '100%'})


@app.callback(
    Output("content_tab", "children"),
    [Input("tabs", "active_tab")]
)
def render_tab_map_content(active_tab: str) -> html.Div:
    """
    Renders the content of the selected tab for the general overview page.
    :param active_tab:
    :return:
    """
    if active_tab == "tab-3":
        return layout_tab_one()
    elif active_tab == "tab-2":
        return layout_tab_two()
    elif active_tab == "tab-1":
        return layout_tab_three()
    else:
        return html.Div("Invalid tab selected")