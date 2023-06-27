from pathlib import Path

import plotly.graph_objects as go

from src.utils.gws_convertor import GWSRDConvertor


def plot_overview_map_dummy(data: list[dict]):
    """
    TODO: display the correct information as color and hover.
    DISCLAIMER: This is a DUMMY function
    This function plots an overview Map of the current dike in data. It uses plotly Mapbox for the visualization.

    :param data: serialized dike data from a geopandas dataframe that has been saved
    :return:
    """
    fig = go.Figure()

    for dijkvak in data:
        # convert in GWS coordinates:
        linestring_rd = dijkvak['geometry']
        convertor = [GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in linestring_rd]

        if dijkvak["objectid"] in [0, 1, 2, 4, 7, 8, 30, 31, 33, 34, 35]:
            color = 'red'
        elif dijkvak["objectid"] in [5, 6, 9, 10, 11, 12, 13, 14, 21, 22]:
            color = 'orange'
        elif dijkvak["objectid"] in [15, 16, 17, 18, 19, 20]:
            color = 'green'
        else:
            color = 'blue'

        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lat=[x[0] for x in convertor],
            lon=[x[1] for x in convertor],
            marker={'size': 10, 'color': color},
            line={'width': 5, 'color': color},
            name='Traject 38-1',
            hovertemplate=f'Vaknaam {dijkvak["vaknaam"]}',
            showlegend=False, ))

    # Update layout of the figure and add token for mapbox
    mapbox_access_token = open(Path(__file__).parent.parent / "assets" / "mapbox_token.txt").read()
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            center=dict(lat=convertor[0][0], lon=convertor[0][1]),
            zoom=11,
        ))
    return fig
