from pathlib import Path

import plotly.graph_objects as go

from src.linear_objects.traject import DikeTraject
from src.utils.gws_convertor import GWSRDConvertor




def plot_overview_map_dummy(dike_traject: DikeTraject):
    """
    TODO: display the correct information as color and hover.
    DISCLAIMER: This is a DUMMY function
    This function plots an overview Map of the current dike in data. It uses plotly Mapbox for the visualization.

    :param data: serialized dike data from a geopandas dataframe that has been saved
    :return:
    """
    fig = go.Figure()

    for section in dike_traject.dike_sections:
        convertor = [GWSRDConvertor().to_wgs(pt[0], pt[1]) for pt in section.coordinates_rd] # convert in GWS coordinates:
        if section.is_reinforced:
            color = 'green' if section.final_measure_doorsnede == "Grondversterking binnenwaarts 2025" else 'red'
        else:
            color = 'grey'

        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lat=[x[0] for x in convertor],
            lon=[x[1] for x in convertor],
            marker={'size': 10, 'color': color},
            line={'width': 5, 'color': color},
            name='Traject 38-1',
            hovertemplate=f'Vaknaam {section.name}',
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
