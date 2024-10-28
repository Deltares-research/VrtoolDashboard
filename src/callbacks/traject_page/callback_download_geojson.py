import dash
from dash import Output, callback, Input

from src.component_ids import DOWNLOAD_OVERVIEW_ID, DOWNLOAD_OVERVIEW_BUTTON_ID, DOWNLOAD_ASSESSMENT_BUTTON_ID, \
    DOWNLOAD_ASSESSMENT_ID, SLIDER_YEAR_RELIABILITY_RESULTS_ID, DOWNLOAD_REINFORCED_SECTIONS_ID, \
    DOWNLOAD_REINFORCED_SECTIONS_BUTTON_ID, BUTTON_DOWNLOAD_OVERVIEW_NB_CLICKS, BUTTON_DOWNLOAD_ASSESSMENT_NB_CLICKS, \
    BUTTON_DOWNLOAD_REINFORCED_SECTIONS_NB_CLICKS, DOWNLOAD_RUN_JSON_ID, BUTTON_SAVE_RUN_AS_JSON, RUN_SAVE_NAME_ID
from src.linear_objects.dike_traject import DikeTraject
from src.utils.utils import export_to_json


@callback(
    [Output(DOWNLOAD_RUN_JSON_ID, 'data')],
    [Input('stored-data', 'data'),
     Input(BUTTON_SAVE_RUN_AS_JSON, 'n_clicks'),
     Input(RUN_SAVE_NAME_ID, 'data'),
     ]
)
def download_traject_run_json(dike_traject_data: dict, n_clicks: int, run_name: str):
    print(n_clicks, run_name)
    if dike_traject_data is None or n_clicks == 0 or n_clicks is None:
        return dash.no_update

    if n_clicks is None:
        return dash.no_update

    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        return dict(content=_dike_traject, filename=f"{run_name}.json")


@callback(
    [Output(DOWNLOAD_OVERVIEW_ID, 'data'),
     Output(BUTTON_DOWNLOAD_OVERVIEW_NB_CLICKS, 'value')],
    [Input('stored-data', 'data'),
     Input(DOWNLOAD_OVERVIEW_BUTTON_ID, 'n_clicks'),
     Input(BUTTON_DOWNLOAD_OVERVIEW_NB_CLICKS, 'value')]
)
def download_overview_geojson(dike_traject_data: dict, n_clicks: int, store_n_click_button: int) -> tuple[dict, int]:
    """
    Download the overview map of the dike traject as a geojson file.

    :param dike_traject_data:
    :param n_clicks:
    :return:
    """
    params = {'tab': 'overview'}

    if dike_traject_data is None or n_clicks == 0 or n_clicks is None:
        return dash.no_update

    if n_clicks is None or store_n_click_button == n_clicks:  # update when clicking on button ONLY
        return dash.no_update

    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        return dict(content=_dike_traject.export_to_geojson(params), filename="overzicht.geojson"), n_clicks


@callback(
    [Output(DOWNLOAD_ASSESSMENT_ID, 'data'),
     Output(BUTTON_DOWNLOAD_ASSESSMENT_NB_CLICKS, 'value')],
    [Input('stored-data', 'data'),
     Input(SLIDER_YEAR_RELIABILITY_RESULTS_ID, "value"),
     Input(DOWNLOAD_ASSESSMENT_BUTTON_ID, 'n_clicks'),
     Input(BUTTON_DOWNLOAD_ASSESSMENT_NB_CLICKS, 'value')]
)
def download_assessment_geojson(dike_traject_data: dict, selected_year: int, n_clicks: int,
                                store_n_click_button: int) -> tuple[dict, int]:
    """
    Download the overview map of the dike traject as a geojson file.

    :param dike_traject_data:
    :param n_clicks:
    :return:
    """
    params = {'tab': 'assessment', 'selected_year': selected_year}

    if dike_traject_data is None or n_clicks == 0 or n_clicks is None:
        return dash.no_update

    if n_clicks is None or store_n_click_button == n_clicks:  # update when clicking on button ONLY
        return dash.no_update

    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        return dict(content=_dike_traject.export_to_geojson(params),
                    filename=f"beoordelingsresultaten_{selected_year}.geojson"), n_clicks


@callback(
    [Output(DOWNLOAD_REINFORCED_SECTIONS_ID, 'data'),
     Output(BUTTON_DOWNLOAD_REINFORCED_SECTIONS_NB_CLICKS, "value")],
    [Input('stored-data', 'data'),
     Input(SLIDER_YEAR_RELIABILITY_RESULTS_ID, "value"),
     Input("select_calculation_type", "value"),
     Input(DOWNLOAD_REINFORCED_SECTIONS_BUTTON_ID, 'n_clicks'),
     Input(BUTTON_DOWNLOAD_REINFORCED_SECTIONS_NB_CLICKS, 'value')]
)
def download_reinforced_sections_geojson(dike_traject_data: dict, selected_year: int, calculation_type: str,
                                         n_clicks: int, store_n_click_button: int) -> tuple[dict, int]:
    """
    Download the overview map of the dike traject as a geojson file.

    :param dike_traject_data:
    :param selected_year: selected year on the user input slider
    :param calc_type: Selected calculation type by the user from the OptionField, one of "VEILIGHEIDSRENDEMENT" or "DOORSNEDE"
    :param n_clicks:
    :return:
    """
    params = {'tab': 'reinforced_sections', 'selected_year': selected_year, 'calculation_type': calculation_type}

    if dike_traject_data is None or n_clicks == 0 or n_clicks is None:
        return dash.no_update

    if n_clicks is None or store_n_click_button == n_clicks:  # update when clicking on button ONLY
        return dash.no_update

    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        return dict(content=_dike_traject.export_to_geojson(params),
                    filename=f"versterkingsmaatregelen_{selected_year}_{calculation_type}.geojson"), n_clicks
