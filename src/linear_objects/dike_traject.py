import json
from bisect import bisect_right
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from pandas import DataFrame

from src.constants import REFERENCE_YEAR
from src.linear_objects.base_linear import BaseLinearObject
from src.linear_objects.dike_section import DikeSection

from src.utils.utils import beta_to_pf


@dataclass
class DikeTraject(BaseLinearObject):
    name: str
    signalering_value: float  # Signaleerwaarde
    lower_bound_value: float  # Ondergrens
    dike_sections: list[DikeSection]
    reinforcement_order_vr: list[str]
    reinforcement_order_dsn: list[str]
    greedy_steps: list[dict]
    run_name: str = None

    def serialize(self) -> dict:
        """Serialize the DikeTraject object to a dict, in order to be saved in dcc.Store"""
        return {
            'name': self.name,
            'dike_sections': [section.serialize() for section in self.dike_sections],
            'reinforcement_order_vr': self.reinforcement_order_vr,
            'reinforcement_order_dsn': self.reinforcement_order_dsn,
            'signalering_value': self.signalering_value,
            'lower_bound_value': self.lower_bound_value,
            'greedy_steps': self.greedy_steps,
            'run_name': self.run_name
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
                           reinforcement_order_dsn=data['reinforcement_order_dsn'],
                           signalering_value=data["signalering_value"],
                           lower_bound_value=data["lower_bound_value"],
                           greedy_steps=data["greedy_steps"],
                           run_name=data["run_name"]
                           )

    def export_to_geojson(self) -> str:
        """
        Export the dike traject to a geojson format
        """
        _geojson = {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::28992"}},
            "features": [section.export_as_geojson_feature() for section in self.dike_sections]
        }
        return json.dumps(_geojson)

    def calc_traject_probability_array(self, calc_type: str) -> np.array:

        _beta_df = get_initial_assessment_df(self.dike_sections)
        _traject_pf, _ = get_traject_prob(_beta_df, ['StabilityInner', 'Piping', 'Overflow', "Revetment"])
        years = self.dike_sections[0].years

        if calc_type == "vr":
            _section_order = self.reinforcement_order_vr
            _section_measure = "final_measure_veiligheidsrendement"

        elif calc_type == "dsn":
            _section_order = self.reinforcement_order_dsn
            _section_measure = "final_measure_doorsnede"

        else:
            raise ValueError("calc_type should be either 'vr' or 'dsn' ")

        for section_name in _section_order:
            section = self.get_section(section_name)

            if not section.in_analyse:  # skip if the section is not reinforced
                continue

            if (calc_type == 'doorsnede') and (
                    not section.is_reinforced_doorsnede):  # skip if the section is not reinforced
                continue

            if (calc_type == 'veiligheidsrendement') and (
                    not section.is_reinforced_veiligheidsrendement):  # skip if the section is not reinforced
                continue
            _active_mechanisms = ["Overflow", "Piping", "StabilityInner"]
            if section.revetment:
                _active_mechanisms.append("Revetment")
            # add a row to the dataframe with the initial assessment of the section
            for mechanism in _active_mechanisms:
                mask = (_beta_df['name'] == section.name) & (_beta_df['mechanism'] == mechanism)
                # replace the row in the dataframe with the betas of the section if both the name and mechanism match
                d = {"name": section.name, "mechanism": mechanism, "Length": section.length}

                for year, beta in zip(years, getattr(section, _section_measure)[mechanism]):
                    d[year] = beta
                _beta_df.loc[mask, years] = d
            _reinforced_traject_pf, _ = get_traject_prob(_beta_df, _active_mechanisms)

            _traject_pf = np.concatenate((_traject_pf, _reinforced_traject_pf), axis=0)

        return np.array(_traject_pf)

    def get_section(self, name: str) -> DikeSection:
        """Get the section object by name"""
        for section in self.dike_sections:
            if (section.name == name):
                return section
        raise ValueError(f"Section with name {name} not found")

    @staticmethod
    def get_initial_assessment_df(sections: list[DikeSection]) -> DataFrame:
        """Get the initial assessment dataframe from all children sections"""

        years = sections[0].years
        df = pd.DataFrame(columns=["name", "mechanism"] + years + ["Length"])

        for section in sections:
            if not section.in_analyse:
                continue
            if not section.is_reinforced_doorsnede and not section.is_reinforced_veiligheidsrendement:
                continue
            # add a row to the dataframe with the initial assessment of the section
            mechanisms = ["Overflow", "StabilityInner", "Piping"]
            if section.revetment:
                mechanisms.append("Revetment")

            for mechanism in mechanisms:
                d = {"name": section.name, "mechanism": mechanism, "Length": section.length

                     }

                for year, beta in zip(years, section.initial_assessment[mechanism]):
                    d[year] = beta
                s = pd.DataFrame(d, index=[0])
                df = pd.concat([df, s])

        return df

    def get_cum_cost(self, calc_type: str) -> np.ndarray:
        """Get the cumulative cost (M€) of the dike traject for various reinforcement states

        :param calc_type: either 'vr' or 'dsn'

        :return: np.ndarray with the cumulative cost of the dike traject. The first element is the cost of the
        unreinforced dike traject (0€), the second element is the cost of the first reinforced section, the third
        element is the cost of the first and second reinforced sections, etc...
        The last element is the cost of the fully reinforced dike traject for the given calc_type.

        """

        cost_list = [0]

        if calc_type == "vr":
            _section_order = self.reinforcement_order_vr
            _section_measure = "final_measure_veiligheidsrendement"
        elif calc_type == "dsn":
            _section_order = self.reinforcement_order_dsn
            _section_measure = "final_measure_doorsnede"
        else:
            raise ValueError("calc_type should be either 'vr' or 'dsn'")

        for section_name in _section_order:
            section = self.get_section(section_name)
            if not (section.in_analyse):
                continue
            if (calc_type == 'doorsnede') and (
                    not section.is_reinforced_doorsnede):  # skip if the section is not reinforced
                continue
            if (calc_type == 'veiligheidsrendement') and (
                    not section.is_reinforced_veiligheidsrendement):  # skip if the section is not reinforced
                continue

            try:
                cost_list.append(getattr(section, _section_measure)['LCC'])
            except:
                # temporary print for debugging
                print('Geen maatregel op dijkvak {} voor {}'.format(section.name, calc_type))

        return np.cumsum(cost_list) / 1e6

    def get_cum_length(self, calc_type: str) -> np.ndarray:

        length_list = [0]
        if calc_type == "vr":
            _section_order = self.reinforcement_order_vr
            _section_measure = "final_measure_veiligheidsrendement"
        elif calc_type == "dsn":
            _section_order = self.reinforcement_order_dsn
            _section_measure = "final_measure_doorsnede"
        else:
            raise ValueError("calc_type should be either 'vr' or 'dsn'")

        for section_name in _section_order:
            section = self.get_section(section_name)

            if not (section.in_analyse):
                continue
            if (calc_type == 'doorsnede') and (
                    not section.is_reinforced_doorsnede):  # skip if the section is not reinforced
                continue
            if (calc_type == 'veiligheidsrendement') and (
                    not section.is_reinforced_veiligheidsrendement):  # skip if the section is not reinforced
                continue

            length_list.append(section.length)

        return np.cumsum(length_list)

    def _get_greedy_optimization_step_from_speficiations(self, target_year: int, target_beta: float) -> int:
        """Get the optimization step number for the greedy optimization algorithm based on the specifications

        :param target_year: the year for which the reliability should be met
        :param target_beta: the target reliability
        :return: the optimization step number
        """
        # find for which optimization step_number the criteria 'reliability in year' is met
        _year_step_index = bisect_right(self.dike_sections[0].years,
                                        target_year - REFERENCE_YEAR) - 1
        _target_pf = beta_to_pf(target_beta)
        _step_pf_array = get_step_traject_pf(self)[:, _year_step_index]
        _step_index = np.argmax(_step_pf_array < _target_pf)
        return int(_step_index)


def get_traject_prob(beta_df: DataFrame, mechanisms: list) -> tuple[np.array, dict]:
    """Determines the probability of failure for a traject based on the standardized beta input"""

    beta_df = beta_df.reset_index().set_index('mechanism').drop(columns=['name'])
    beta_df = beta_df.drop(columns=['Length', "index"])

    traject_probs = dict((el, []) for el in mechanisms)
    total_traject_prob = np.empty((1, beta_df.shape[1]))
    for mechanism in mechanisms:
        if mechanism == 'Revetment':
            # check is mechanism is in the index
            if not mechanism in beta_df.index:
                continue

        if mechanism == 'Overflow':
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


def get_initial_assessment_df(sections: list[DikeSection]) -> DataFrame:
    """Get the initial assessment dataframe from all children sections"""
    years = sections[0].years
    df = pd.DataFrame(columns=["name", "mechanism"] + years + ["Length"])

    for section in sections:
        if not section.in_analyse:
            continue
        if not section.is_reinforced_doorsnede and not section.is_reinforced_veiligheidsrendement:
            continue
        # add a row to the dataframe with the initial assessment of the section
        mechanisms = ["Overflow", "StabilityInner", "Piping"]
        if section.revetment:
            mechanisms.append("Revetment")

        for mechanism in mechanisms:
            d = {"name": section.name, "mechanism": mechanism, "Length": section.length

                 }

            for year, beta in zip(years, section.initial_assessment[mechanism]):
                d[year] = beta
            s = pd.DataFrame(d, index=[0])
            df = pd.concat([df, s])

    return df


def cum_cost_steps(dike_traject: DikeTraject):
    cost_list = []
    for step in dike_traject.greedy_steps:
        cost_list.append(step["LCC"])

    return np.cumsum(cost_list) / 1e6


def get_step_traject_pf(dike_traject: DikeTraject) -> np.array:
    pf_array = []
    for step in dike_traject.greedy_steps:
        pf_array.append(step["pf"])

    return np.array(pf_array)
