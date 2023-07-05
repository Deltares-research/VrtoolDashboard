import copy
from dataclasses import dataclass

import numpy as np
import pandas as pd
from pandas import DataFrame

from src.linear_objects.base_linear import BaseLinearObject
from src.linear_objects.dike_section import DikeSection

from src.utils.importers import parse_zip_content
from src.utils.utils import beta_to_pf


@dataclass
class DikeTraject(BaseLinearObject):
    name: str
    dike_sections: list[DikeSection]
    reinforcement_order_vr: list[str]
    reinforcement_order_dsn: list[str]

    @classmethod
    def from_uploaded_zip(cls, contents: str, zipname: str):
        """ Create a DikeTraject object from the uploaded zip file"""
        _all_unzipped_files = parse_zip_content(contents, zipname)

        # Parse the csv of the optimal measures of Doorsnede-eisen and Veiligheidsrendement:
        #  -For dsn, the optimal measure is extracted from FinalMeasures_Doorsnede-eisen.csv
        #  -For vr, the optimal measure is extracted from TakenMeasures_Optimal_Veiligheidsrendement.csv
        _optimal_measure_dsn_dict = parse_optimal_measures_results(_all_unzipped_files, "FinalMeasures_Doorsnede-eisen")
        _optimal_measure_vr_dict = parse_optimal_measures_results(_all_unzipped_files,
                                                                  "TakenMeasures_Optimal_Veiligheidsrendement")

        # Get the order of the reinforced sections
        _order_reinforcement_dsn = determine_reinforcement_order(_all_unzipped_files, "TakenMeasures_Doorsnede-eisen")
        _order_reinforcement_vr = determine_reinforcement_order(_all_unzipped_files,
                                                                "TakenMeasures_Veiligheidsrendement")

        # Parse the geojson of the dike sections and add the final measures to the dike sections
        _dike_sections = []

        for _, section in _all_unzipped_files['traject_gdf'].iterrows():
            _dike_section = DikeSection(name=section['vaknaam'],
                                        coordinates_rd=section['geometry'],
                                        in_analyse=section['in_analyse'],
                                        )

            # Parse dike results csv and add the measure and its associated reliabilities
            _dike_section.set_measure_and_reliabilities_from_csv(_optimal_measure_dsn_dict, _all_unzipped_files,
                                                                 "doorsnede")
            _dike_section.set_measure_and_reliabilities_from_csv(_optimal_measure_vr_dict, _all_unzipped_files,
                                                                 "veiligheidrendement")
            _dike_section.set_initial_assessment_from_csv(_all_unzipped_files["InitialAssessment_Betas"])

            _dike_sections.append(_dike_section)

        return cls(name=zipname,
                   dike_sections=_dike_sections,
                   reinforcement_order_vr=_order_reinforcement_vr,
                   reinforcement_order_dsn=_order_reinforcement_dsn)

    def serialize(self) -> dict:
        """Serialize the DikeTraject object to a dict, in order to be saved in dcc.Store"""
        return {
            'name': self.name,
            'dike_sections': [section.serialize() for section in self.dike_sections],
            'reinforcement_order_vr': self.reinforcement_order_vr,
            'reinforcement_order_dsn': self.reinforcement_order_dsn,
        }

    @staticmethod
    def deserialize(data: dict) -> 'DikeTraject':
        """
        Deserialize the DikeTraject object from a dict, in order to be loaded from dcc.Store
        :param data: serialized dict with the data of the DikeTraject object
        """
        sections = [DikeSection.deserialize(section_data) for section_data in data['dike_sections']]
        return DikeTraject(name=data['name'],
                           dike_sections=sections,
                           reinforcement_order_vr=data['reinforcement_order_vr'],
                           reinforcement_order_dsn=data['reinforcement_order_dsn'])


def parse_optimal_measures_results(all_unzipped_files: dict, filename: str) -> dict:
    """
    Parse the optimal measures results from the csv files in the zip file. Each section should have one and only one
    optimal measure.
    :param all_unzipped_files: dict with all the unzipped files from the zip file
    :param filename: name of the csv file with the final measures results
    :return:
    """
    if filename not in all_unzipped_files.keys():
        raise ValueError(f'The zip file does not contain the required file: {filename}')
    _measures_df = all_unzipped_files[filename]
    _measures_df.dropna(subset=['Section'], inplace=True)  # drop nan in Section column
    _measures_df['Section'] = _measures_df['Section'].str.replace('^DV', '',
                                                                  regex=True)  # remove DV from section names
    _measures_df.set_index("Section", inplace=True)

    if not _measures_df.index.is_unique:
        raise ValueError(f"Error: the file {filename} contains duplicate section names")

    _measure_dict = _measures_df[["LCC", 'name', "ID", "yes/no", "dberm", "dcrest"]].to_dict('index')
    return _measure_dict


def determine_reinforcement_order(all_unzipped_files: dict, filename: str) -> list[str]:
    """
    Parse the taken measures csv file to obtain the order of the reinforcement measures
    :param all_unzipped_files: dict with all the unzipped files from the zip file
    :param filename: name of the csv file with the final measures results
    :return:
    """
    if filename not in all_unzipped_files.keys():
        raise ValueError(f'The zip file does not contain the required file: {filename}')
    final_measures_df = all_unzipped_files[filename]
    return final_measures_df['Section'].dropna().unique()
