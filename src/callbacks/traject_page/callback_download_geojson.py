import dash
from dash import Output, callback, Input

from src.component_ids import DOWNLOAD_OVERVIEW_ID, DOWNLOAD_OVERVIEW_BUTTON_ID
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

    #TODO: update such a way the callback is only triggeered when (re)clicking on the button ( which is different than n-cliks >0)
    if dike_traject_data is None or n_clicks == 0 or n_clicks is None:

        return dash.no_update
    else:
        _dike_traject = DikeTraject.deserialize(dike_traject_data)
        return dict(content=_dike_traject.export_to_geojson(), filename="overview.geojson")
