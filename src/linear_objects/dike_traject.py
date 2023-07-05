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

    @classmethod
    def from_uploaded_zip(cls, contents: str, zipname: str):
        """ Create a DikeTraject object from the uploaded zip file"""
        _all_unzipped_files = parse_zip_content(contents, zipname)
        # Parse the csv of the final measures of Doorsnede-eisen and Veiligheidsrendement;
        _final_measure_dsn_dict = parse_final_measures_results(_all_unzipped_files, "FinalMeasures_Doorsnede-eisen")
        _taken_measure_dsn_dict = parse_final_measures_results(_all_unzipped_files, "TakenMeasures_Doorsnede-eisen")

        _final_measure_vr_dict = parse_final_measures_results(_all_unzipped_files, "FinalMeasures_Veiligheidsrendement")
        _taken_measure_vr_dict = parse_final_measures_results(_all_unzipped_files,
                                                              "TakenMeasures_Optimal_Veiligheidsrendement")

        # Parse the geojson of the dike sections and add the final measures to the dike sections
        _dike_sections = []

        for _, section in _all_unzipped_files['traject_gdf'].iterrows():
            _dike_section = DikeSection(name=section['vaknaam'],
                                        coordinates_rd=section['geometry'],
                                        in_analyse=section['in_analyse'],
                                        )

            # Parse dike results csv and add the measure and its associated reliabilities
            _dike_section.set_measure_and_reliabilities_from_csv(_taken_measure_dsn_dict, _all_unzipped_files,
                                                                 "doorsnede")
            _dike_section.set_measure_and_reliabilities_from_csv(_taken_measure_vr_dict, _all_unzipped_files,
                                                                 "veiligheidrendement")
            _dike_section.set_initial_assessment_from_csv(_all_unzipped_files["InitialAssessment_Betas"])

            _dike_sections.append(_dike_section)

        return cls(name=zipname, dike_sections=_dike_sections)

    def serialize(self) -> dict:
        """Serialize the DikeTraject object to a dict, in order to be saved in dcc.Store"""
        return {
            'name': self.name,
            'dike_sections': [section.serialize() for section in self.dike_sections]
        }

    @staticmethod
    def deserialize(data: dict) -> 'DikeTraject':
        """
        Deserialize the DikeTraject object from a dict, in order to be loaded from dcc.Store
        #TODO: make it classmethod .from_dict()
        :param data: serialized dict with the data of the DikeTraject object
        """
        sections = [DikeSection.deserialize(section_data) for section_data in data['dike_sections']]
        return DikeTraject(name=data['name'], dike_sections=sections)


def parse_final_measures_results(all_unzipped_files: dict, filename: str) -> dict:
    """
    Parse the final measures results from the csv files in the zip file.
    :param all_unzipped_files: dict with all the unzipped files from the zip file
    :param filename: name of the csv file with the final measures results
    :return:
    """
    if filename not in all_unzipped_files.keys():
        raise ValueError(f'The zip file does not contain the required file: {filename}')
    final_measures_df = all_unzipped_files[filename]
    final_measures_df.dropna(subset=['Section'], inplace=True)  # drop nan in Section column
    final_measures_df['Section'] = final_measures_df['Section'].str.replace('^DV', '',
                                                                            regex=True)  # remove DV from section names
    final_measures_df.set_index("Section", inplace=True)

    final_measure_dict = final_measures_df[["LCC", 'name', "ID", "yes/no", "dberm", "dcrest"]].to_dict(orient='index')
    return final_measure_dict


def get_traject_prob(beta_df, mechanisms=["StabilityInner", "Piping", "Overflow"]):
    """From VRUtils postprocessing"""
    # determines the probability of failure for a traject based on the standardized beta input
    beta_df = beta_df.reset_index().set_index("mechanism").drop(columns=["name"])
    traject_probs = dict((el, []) for el in mechanisms)
    total_traject_prob = np.empty((1, beta_df.shape[1]))
    for mechanism in mechanisms:
        if mechanism == "Overflow":
            # take min beta in each column
            traject_probs[mechanism] = beta_to_pf(beta_df.loc[mechanism].min().values)
        else:
            pf_df = beta_to_pf(beta_df.loc[mechanism].values)
            pnonf_df = np.subtract(1, pf_df)
            pnonf_traject = np.product(pnonf_df, axis=0)
            traject_probs[mechanism] = 1 - pnonf_traject
            # convert to probability
            # 1-prod(1-p)
        total_traject_prob += traject_probs[mechanism]
    return total_traject_prob, traject_probs
