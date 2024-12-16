import json
from bisect import bisect_right
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from pandas import DataFrame
from vrtool.common.enums import MechanismEnum

from src.constants import REFERENCE_YEAR, Mechanism
from src.linear_objects.base_linear import BaseLinearObject
from src.linear_objects.dike_section import DikeSection

from src.utils.utils import beta_to_pf, pf_to_beta, calculate_traject_probability


@dataclass
class DikeTraject(BaseLinearObject):
    name: str
    signalering_value: float  # Signaleerwaarde
    lower_bound_value: float  # Ondergrens
    dike_sections: list[DikeSection]
    reinforcement_order_vr: list[str]
    reinforcement_order_dsn: list[str]
    greedy_steps: list[dict]
    _run_id_vr: int
    _run_id_dsn: int
    flood_damage: float = 0
    run_name: str = None
    final_step_number: int = None  # the step number of the final step in the greedy optimization
    greedy_stop_type_criteria: Optional[str] = None
    greedy_stop_criteria_year: Optional[int] = None
    greedy_stop_criteria_beta: Optional[float] = None
    reinforcement_modified_order_vr: Optional[dict] = None  # set as Optional with default value to prevent necessary migration for users


    def serialize(self) -> dict:
        """Serialize the DikeTraject object to a dict, in order to be saved in dcc.Store"""
        return {
            "name": self.name,
            "dike_sections": [section.serialize() for section in self.dike_sections],
            "reinforcement_order_vr": self.reinforcement_order_vr,
            "reinforcement_order_dsn": self.reinforcement_order_dsn,
            "reinforcement_modified_order_vr": self.reinforcement_modified_order_vr,
            "signalering_value": self.signalering_value,
            "lower_bound_value": self.lower_bound_value,
            "greedy_steps": self.greedy_steps,
            "run_name": self.run_name,
            "flood_damage": self.flood_damage,
            "_run_id_vr": self._run_id_vr,
            "_run_id_dsn": self._run_id_dsn,
            "final_step_number": self.final_step_number,
            "greedy_stop_type_criteria": self.greedy_stop_type_criteria,
            "greedy_stop_criteria_year": self.greedy_stop_criteria_year,
            "greedy_stop_criteria_beta": self.greedy_stop_criteria_beta,
        }

    @staticmethod
    def deserialize(data: dict) -> "DikeTraject":
        """
        Deserialize the DikeTraject object from a dict, in order to be loaded from dcc.Store
        :param data: serialized dict with the data of the DikeTraject object
        """
        sections = [
            DikeSection.deserialize(section_data)
            for section_data in data["dike_sections"]
        ]
        return DikeTraject(
            name=data["name"],
            dike_sections=sections,
            reinforcement_order_vr=data["reinforcement_order_vr"],
            reinforcement_order_dsn=data["reinforcement_order_dsn"],
            reinforcement_modified_order_vr=data.get("reinforcement_modified_order_vr", None),
            signalering_value=data["signalering_value"],
            lower_bound_value=data["lower_bound_value"],
            greedy_steps=data["greedy_steps"],
            run_name=data["run_name"],
            flood_damage=data.get("flood_damage", -9999),
            _run_id_vr=data["_run_id_vr"],
            _run_id_dsn=data["_run_id_dsn"],
            final_step_number=data["final_step_number"],
            greedy_stop_type_criteria=data.get("greedy_stop_type_criteria", None),
            greedy_stop_criteria_year=data.get("greedy_stop_criteria_year", None),
            greedy_stop_criteria_beta=data.get("greedy_stop_criteria_beta", None),
        )

    def export_to_geojson(self, params: dict) -> str:
        """
        Export the dike traject to a geojson format
        """
        _geojson = {
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:EPSG::28992"},
            },
            "features": [
                section.export_as_geojson_feature(params)
                for section in self.dike_sections
            ],
        }

        return json.dumps(_geojson)

    def calc_traject_probability_array(self, calc_type: str) -> np.array:
        """
        Return an array of the traject probability of failure for year year and each step. Columns are the years and
        rows are the steps. The first row is the probability of failure of the unreinforced dike traject.
        :param calc_type:
        :return:
        """

        _beta_df = get_initial_assessment_df(self.dike_sections)
        _traject_pf, _ = get_traject_prob(_beta_df)
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

            if (calc_type == "doorsnede") and (
                    not section.is_reinforced_doorsnede
            ):  # skip if the section is not reinforced
                continue

            if (calc_type == "veiligheidsrendement") and (
                    not section.is_reinforced_veiligheidsrendement
            ):  # skip if the section is not reinforced
                continue
            _active_mechanisms = ["Overflow", "Piping", "StabilityInner"]
            if section.revetment:
                _active_mechanisms.append("Revetment")
            # add a row to the dataframe with the initial assessment of the section
            for mechanism in _active_mechanisms:
                mask = (_beta_df["name"] == section.name) & (
                        _beta_df["mechanism"] == mechanism
                )
                # replace the row in the dataframe with the betas of the section if both the name and mechanism match

                for year, beta in zip(
                        years, getattr(section, _section_measure)[mechanism]
                ):
                    _beta_df.loc[mask, year] = beta

            _reinforced_traject_pf, _ = get_traject_prob(_beta_df)

            _traject_pf = np.concatenate((_traject_pf, _reinforced_traject_pf), axis=0)
        return np.array(_traject_pf)

    def get_section(self, name: str) -> DikeSection:
        """Get the section object by name"""
        for section in self.dike_sections:
            if section.name == name:
                return section
        raise ValueError(f"Section with name {name} not found")

    def get_sections_in_reinforcement_order(self) -> list[DikeSection]:
        """Get the sections in the reinforcement order"""
        return [self.get_section(name) for name in self.reinforcement_order_vr]


    @staticmethod
    def get_initial_assessment_df(sections: list[DikeSection]) -> DataFrame:
        """Get the initial assessment dataframe from all children sections"""

        years = sections[0].years
        df = pd.DataFrame(columns=["name", "mechanism"] + years + ["Length"])

        for section in sections:
            if not section.in_analyse:
                continue
            if (
                    not section.is_reinforced_doorsnede
                    and not section.is_reinforced_veiligheidsrendement
            ):
                continue
            # add a row to the dataframe with the initial assessment of the section
            mechanisms = ["Overflow", "StabilityInner", "Piping"]
            if section.revetment:
                mechanisms.append("Revetment")

            for mechanism in mechanisms:
                d = {
                    "name": section.name,
                    "mechanism": mechanism,
                    "Length": section.length,
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
            if (calc_type == "doorsnede") and (
                    not section.is_reinforced_doorsnede
            ):  # skip if the section is not reinforced
                continue
            if (calc_type == "veiligheidsrendement") and (
                    not section.is_reinforced_veiligheidsrendement
            ):  # skip if the section is not reinforced
                continue

            try:
                cost_list.append(getattr(section, _section_measure)["LCC"])
            except:
                # temporary print for debugging
                print(
                    "Geen maatregel op dijkvak {} voor {}".format(
                        section.name, calc_type
                    )
                )

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
            if (calc_type == "doorsnede") and (
                    not section.is_reinforced_doorsnede
            ):  # skip if the section is not reinforced
                continue
            if (calc_type == "veiligheidsrendement") and (
                    not section.is_reinforced_veiligheidsrendement
            ):  # skip if the section is not reinforced
                continue

            length_list.append(section.length)

        return np.cumsum(length_list)

    def _get_greedy_optimization_step_from_speficiations(
            self, target_year: int, target_beta: float
    ) -> int:
        """Get the optimization step number for the greedy optimization algorithm based on the specifications

        :param target_year: the year for which the reliability should be met
        :param target_beta: the target reliability
        :return: the optimization step number
        """
        # find for which optimization step_number the criteria 'reliability in year' is met
        _year_step_index = (
                bisect_right(self.dike_sections[0].years, target_year - REFERENCE_YEAR) - 1
        )
        _target_pf = beta_to_pf(target_beta)
        _step_pf_array = get_step_traject_pf(self)[:, _year_step_index]
        _step_index = np.argmax(_step_pf_array < _target_pf)
        return int(_step_index)


def get_traject_prob_fast(traject_reliability: dict):
    """Calculate the traject probability of failure for the given traject reliability data for the whole time horizon
    
    Args:
        traject_reliability: dictionary with the reliability data for each mechanism
        Example: "Overflow": {"time": [2025, 2030, 2035], "beta": [0.1, 0.2, 0.3]}
        
        
    """

    def convert_beta_to_pf_per_section(traject_reliability):
        time = [t for section in traject_reliability.values() for t in section["time"]]
        beta = [b for section in traject_reliability.values() for b in section["beta"]]
        beta_per_time = {
            t: [b for b, t_ in zip(beta, time) if t_ == t] for t in set(time)
        }
        pf_per_time = {
            t: list(beta_to_pf(np.array(beta))) for t, beta in beta_per_time.items()
        }
        return pf_per_time

    def compute_overflow(traject_reliability):
        pf_per_time = convert_beta_to_pf_per_section(traject_reliability)
        traject_pf_per_time = {t: max(pf) for t, pf in pf_per_time.items()}
        return traject_pf_per_time

    def compute_piping_stability(traject_reliability):
        pf_per_time = convert_beta_to_pf_per_section(traject_reliability)
        traject_pf_per_time = {
            t: 1 - np.prod(np.subtract(1, pf)) for t, pf in pf_per_time.items()
        }
        return traject_pf_per_time

    def compute_revetment(traject_reliability):
        pf_per_time = convert_beta_to_pf_per_section(traject_reliability)
        traject_pf_per_time = {t: max(pf) for t, pf in pf_per_time.items()}
        return traject_pf_per_time

    def compute_system_failure_probability(traject_reliability):
        result = {}
        for mechanism, data in traject_reliability.items():
            if mechanism is MechanismEnum.OVERFLOW:
                result[mechanism] = compute_overflow(data)
            elif (
                    mechanism is MechanismEnum.PIPING
                    or mechanism is MechanismEnum.STABILITY_INNER
            ):
                result[mechanism] = compute_piping_stability(data)
            elif mechanism is MechanismEnum.REVETMENT:
                result[mechanism] = compute_revetment(data)
            else:
                raise ValueError(f"Mechanism {mechanism} not recognized.")
        return result


    _traject_probability = compute_system_failure_probability(traject_reliability)
    _traject_probs = calculate_traject_probability(_traject_probability)
    return _traject_probs


def get_traject_prob(beta_df: DataFrame) -> tuple[np.array, dict]:
    """Determines the probability of failure for a traject based on the standardized beta input"""

    beta_df = beta_df.reset_index().set_index("mechanism").drop(columns=["name"])
    beta_df = beta_df.drop(columns=["Length", "index"])
    beta_df = beta_df.astype(float)
    mechanisms = ['Overflow', 'Piping', 'StabilityInner', 'Revetment']
    traject_probs = dict((el, []) for el in mechanisms)
    total_traject_prob = np.empty((1, beta_df.shape[1]))
    # You need to loop over Revetment here even if it is not an active mechanism of the current section
    for mechanism in mechanisms:

        if mechanism in ['Overflow', 'Revetment']:
            # check is mechanism is in the index
            if not mechanism in beta_df.index:
                continue
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
        if (
                not section.is_reinforced_doorsnede
                and not section.is_reinforced_veiligheidsrendement
        ):
            continue
        # add a row to the dataframe with the initial assessment of the section
        mechanisms = ["Overflow", "StabilityInner", "Piping"]
        if section.revetment:
            mechanisms.append("Revetment")

        for mechanism in mechanisms:
            d = {"name": section.name, "mechanism": mechanism, "Length": section.length}

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
