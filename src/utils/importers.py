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
    """
    Parse the content of a zip file and return a dictionary with the file names as keys and the file dataframes as values
    """
    # Read the content of the zip file
    content_type, content_string = contents.split(',')
    decoded = BytesIO(base64.b64decode(content_string))

    # Extract the files from the zip file
    with zipfile.ZipFile(decoded, 'r') as zip_ref:
        file_list = zip_ref.namelist()

        # Parse and process each file
        results = {}
        for file_name in file_list:
            with zip_ref.open(file_name) as file:

                _path_name = Path(file_name)
                _file_content = file.read().decode('utf-8')

                if _path_name.suffix == '.csv':
                    df = pd.read_csv(StringIO(_file_content))
                    results[_path_name.stem] = df
                    if "name" in results[_path_name.stem].columns:
                        #convert to string
                        results[_path_name.stem]["name"] = results[_path_name.stem]["name"].astype(str)

                if _path_name.suffix == '.geojson':
                    # TODO: check if the geometry is expressed in RD coordinates
                    traject_gdf = gpd.read_file(_file_content)
                    traject_gdf["geometry"] = traject_gdf["geometry"].apply(
                        lambda x: list(x.coords))  # Serialize the geometry column to a list of coordinates

                    # if vaknaam is a single digit, add a 0 in front of it
                    # traject_gdf["vaknaam"] = traject_gdf["vaknaam"].apply(lambda x: x.zfill(2))

                    results['traject_gdf'] = traject_gdf


        return results

