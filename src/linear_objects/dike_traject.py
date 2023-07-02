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
        _taken_measure_vr_dict = parse_final_measures_results(_all_unzipped_files, "TakenMeasures_Optimal_Veiligheidsrendement")


        # Parse the geojson of the dike sections and add the final measures to the dike sections
        _dike_sections = []

        for _, section in _all_unzipped_files['traject_gdf'].iterrows():
            _dike_section = DikeSection(name=section['vaknaam'],
                                        coordinates_rd=section['geometry'],
                                        in_analyse=section['in_analyse'],
                                        )
            _dike_section.set_measure_and_reliabilities_from_csv(_final_measure_dsn_dict, _all_unzipped_files, "doorsnede")
            _dike_section.set_measure_and_reliabilities_from_csv(_final_measure_vr_dict, _all_unzipped_files, "veiligheidrendement")

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


def get_traject_prob_development(
        optimal_measures: DataFrame,
        taken_measures: DataFrame,
        initial_beta: DataFrame,
        option_dir,
        calc_type: str = "Veiligheidsrendement",
        mechanisms: list[str] = ("StabilityInner", "Piping", "Overflow"),
):
    """
    Calculate the probability of development of the dike trajectory
    :param optimal_measures:
    :param taken_measures:
    :param initial_beta:
    :param option_dir: Directory where all the dike sections results are stored
    :param calc_type:
    :param mechanisms:
    :return:
    """
    section_order = taken_measures["Section"].dropna().unique()
    beta_dfs = []
    # begin_betas:
    beta_dfs.append(initial_beta)
    for count, section in enumerate(section_order, 1):
        beta_df = copy.deepcopy(beta_dfs[-1])
        # print('Original')

        # maatregel lezen:
        # option_index = taken_measures.loc[optimal_measures.loc[section]['Unnamed: 0']].option_index
        # vr_measure = pd.read_csv(results_dir.joinpath(run,'{}_Options_{}.csv'.format(section,calc_type)),index_col=0).loc[option_index]
        # if section
        if taken_measures.loc[taken_measures.Section == section].shape[0] == 1:
            measure_data = taken_measures.loc[
                taken_measures.Section == section
                ].squeeze()
        else:
            measure_data = taken_measures.loc[
                optimal_measures.loc[section]["Unnamed: 0"]
            ]
        if not np.isnan(measure_data.option_index):
            vr_measure = pd.read_csv(
                option_dir.joinpath(f"{section}_Options_{calc_type}.csv"),
                index_col=0,
            )
            vr_measure = vr_measure.loc[
                (vr_measure.ID == measure_data.ID)
                & (vr_measure["yes/no"] == measure_data["yes/no"])
                & (vr_measure.dcrest == measure_data.dcrest)
                & (vr_measure.dberm == measure_data.dberm)
                ].squeeze()
            for mechanism in mechanisms:
                mask = vr_measure.index.str.startswith(mechanism)
                betas = vr_measure.loc[mask].values
                beta_df.loc[(section[2:], mechanism), :] = betas

        else:
            # no measure, so keep initial beta
            pass

        beta_dfs.append(beta_df)
        # print('added {} with {}'.format(section,vr_measure.type))

    traject_probs = np.empty((len(beta_dfs), 7))
    raw_traject_probs = []
    for count, beta_df in enumerate(beta_dfs):
        traject_probs[count, :], raw_traject_prob = get_traject_prob(beta_df)
        raw_traject_probs.append(raw_traject_prob)
    return section_order, traject_probs


def get_traject_prob(beta_df, mechanisms=["StabilityInner", "Piping", "Overflow"]):
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



