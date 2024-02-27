import dash
from dash import Output, callback, Input

from src.component_ids import DOWNLOAD_OVERVIEW_ID, DOWNLOAD_OVERVIEW_BUTTON_ID, DOWNLOAD_ASSESSMENT_BUTTON_ID, \
    DOWNLOAD_ASSESSMENT_ID, SLIDER_YEAR_RELIABILITY_RESULTS_ID, DOWNLOAD_REINFORCED_SECTIONS_ID, \
    DOWNLOAD_REINFORCED_SECTIONS_BUTTON_ID
from src.linear_objects.dike_traject import DikeTraject


@callback(
    Output(DOWNLOAD_OVERVIEW_ID, 'data'),
    [Input('stored-data', 'data'),
     Input(DOWNLOAD_OVERVIEW_BUTTON_ID, 'n_clicks')]
)
def download_overview_geojson(dike_traject_data: dict, n_clicks: int) -> dict:
    """
    Download the overview map of the dike traject as a geojson file.

    :param dike_traject_data:
    :param n_clicks:
    :return:
    """
    params = {'tab': 'overview'}
    # TODO: update such a way the callback is only triggeered when (re)clicking on the button ( which is different than n-cliks >0)
    # TODO: deal with item above
    if dike_traject_data is None or n_clicks == 0 or n_clicks is None:

        return dash.no_update
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        return dict(content=_dike_traject.export_to_geojson(params), filename="overzicht.geojson")


@callback(
    Output(DOWNLOAD_ASSESSMENT_ID, 'data'),
    [Input('stored-data', 'data'),
     Input(SLIDER_YEAR_RELIABILITY_RESULTS_ID, "value"),
     Input(DOWNLOAD_ASSESSMENT_BUTTON_ID, 'n_clicks')]
)
def download_assessment_geojson(dike_traject_data: dict, selected_year: int, n_clicks: int) -> dict:
    """
    Download the overview map of the dike traject as a geojson file.

    :param dike_traject_data:
    :param n_clicks:
    :return:
    """
    params = {'tab': 'assessment', 'selected_year': selected_year}

    if dike_traject_data is None or n_clicks == 0 or n_clicks is None:

        return dash.no_update
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        return dict(content=_dike_traject.export_to_geojson(params), filename=f"beoordelingsresultaten_{selected_year}.geojson")

@callback(
    Output(DOWNLOAD_REINFORCED_SECTIONS_ID, 'data'),
    [Input('stored-data', 'data'),
     Input(SLIDER_YEAR_RELIABILITY_RESULTS_ID, "value"),
Input("select_calculation_type", "value"),
     Input(DOWNLOAD_REINFORCED_SECTIONS_BUTTON_ID, 'n_clicks')]
)
def download_reinforced_sections_geojson(dike_traject_data: dict, selected_year: int, calculation_type: str, n_clicks: int) -> dict:
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
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        return dict(content=_dike_traject.export_to_geojson(params), filename=f"versterkingsmaatregelen_{selected_year}_{calculation_type}.geojson")
