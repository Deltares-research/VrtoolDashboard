import base64
from io import BytesIO, StringIO
import datetime
import zipfile
from pathlib import Path

import pandas as pd
import geopandas as gpd
from dash import dcc, html
from pandas import DataFrame


def parse_zip_content(contents, zipname: str) -> dict[str, DataFrame]:
    # Read the content of the zip file
    content_type, content_string = contents.split(',')
    decoded = BytesIO(base64.b64decode(content_string))

    # Extract the files from the zip file
    with zipfile.ZipFile(decoded, 'r') as zip_ref:
        file_list = zip_ref.namelist()

        # Parse and process each file
        file_contents = []

        serialized_dike_content = {}
        results = {}
        for file_name in file_list:
            with zip_ref.open(file_name) as file:
                file_content = file.read().decode('utf-8')


                if Path(file_name).suffix == '.csv':

                    if Path(file_name).stem == 'FinalMeasures_Veiligheidsrendement':
                        df = pd.read_csv(StringIO(file_content))

                        # dcc.Store(id=f'stored_veiligheidsrendement', data=df.to_dict('records')),
                        results[file_name] = df
                    elif Path(file_name).stem == 'FinalMeasures_Doorsnede-eisen':
                        df = pd.read_csv(StringIO(file_content))
                        # dcc.Store(id=f'stored_doorsnede-eisen', data=df.to_dict('records')),
                        results[file_name] = df

                if Path(file_name).suffix == '.geojson':

                    # TODO: check if the geometry is expressed in RD coordinates
                    traject_gdf = gpd.read_file(file_content)
                    traject_gdf["geometry"] = traject_gdf["geometry"].apply(lambda x: list(x.coords))  # Serialize the geometry column to a list of coordinates
                    serialized_dike_content["traject_gdf"] = traject_gdf.to_dict('records')
                    results['traject_gdf'] = traject_gdf

        #         # Process each file content as needed
        # file_contents.append(html.Div([
        #     html.H4(file_name),
        # ]))
        # dcc.Store(id='dike_traject_data', data=serialized_dike_content)
        # return file_contents
        return results




def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(BytesIO(decoded))

        elif 'geojson' in filename:
            df = gpd.read_file(BytesIO(decoded))
            df["geometry"] = df["geometry"].apply(lambda x: list(x.coords))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        # dash_table.DataTable(
        #     data=df.to_dict('records'),
        #     columns=[{'name': i, 'id': i} for i in df.columns],
        #     page_size=15
        # ),
        dcc.Store(id='stored-data', data=df.to_dict('records')),

        html.Hr(),  # horizontal line
    ])