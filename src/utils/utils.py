from pathlib import Path
from typing import Optional

import numpy as np
from scipy.stats import norm
import json

from vrtool.common.enums import MechanismEnum
from vrtool.defaults.vrtool_config import VrtoolConfig

from src.constants import Mechanism


def to_million_euros(cost: float) -> float:
    """Converts a cost in euros to millions of euros"""
    return round(cost / 1e6, 2)


def beta_to_pf(beta):
    # alternative: use scipy
    return norm.cdf(-beta)


def pf_to_beta(pf):
    # alternative: use scipy
    return -norm.ppf(pf)


class CombinFunctions:
    """Copy-pasted from Core v0.1.3 because it has been deprecated in Core v0.2.0"""

    @staticmethod
    def combine_probabilities(
            prob_of_failure: dict[str, np.array], selection
    ) -> np.array:

        cnt = 0
        for mechanism in selection:
            if mechanism in prob_of_failure:
                cnt += 1
                p = prob_of_failure[mechanism]
                if cnt == 1:
                    product = 1 - p
                else:
                    product = np.multiply(product, 1 - p)

        if cnt == 1:
            # p is in this case almost equal to 1 - product, but p is more accurate
            return p
        else:
            return 1 - product


class MyEncoder(json.JSONEncoder):
    """Special encoder for numpy arrays to be able to write them to a json file."""

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def export_to_json(data, path: Optional[Path] = None):
    # convert dike_traject_data to json :
    # write to a json file:
    if path is None:
        path = Path(__file__).parent / 'data.json'
    with open(path, 'w') as outfile:
        json.dump(data, outfile, cls=MyEncoder)


def get_signal_value(p_max: float):
    """Obtain a signal value (Signaleringswaarde) from a given maximum probability of failure
    Note that p_signal is always approximately 3 times smaller (just rounded)

    :param p_max: Maximum probability of failure

    :return: Signal value

    """
    if p_max == 1 / 3000:
        return 1 / 10000
    else:
        return p_max / 3.0


def get_WBI_category(P_f_dsn: float, traject_length: float, Pf_eis_sign: float, Pf_eis_ond: float) -> str:
    """

    Function to determine the WBI catgeory of a dike section based on its cross-sectional probability of failure and
    on norm probabilities of failure.
    Is this function correct? Weird assumptions here with N_dsn and w.

    :param P_f_dsn: Probability of failure of the section
    :param traject_length: Length of the dike trajectory in meters
    :param Pf_eis_sign: Probability of failure signaleringswaarde
    :param Pf_eis_ond: Maximum probability of failure for a lower bound: ondergrens
    :return:
    """

    # Lengte-effect
    w = 0.24
    N_dsn = 1 + (0.9 * traject_length) / 300.0  # is 0.9 voor het bovenrivierengebied

    Pf_eis_sign_dsn = (w * Pf_eis_sign) / N_dsn
    Pf_eis_ond_dsn = (w * Pf_eis_ond) / N_dsn

    if P_f_dsn < 1 / 30.0 * Pf_eis_sign_dsn:
        cat = "Iv"
    elif P_f_dsn >= 1 / 30.0 * Pf_eis_sign_dsn and P_f_dsn < Pf_eis_sign_dsn:
        cat = "IIv"
    elif P_f_dsn >= Pf_eis_sign_dsn and P_f_dsn < Pf_eis_ond_dsn:
        cat = "IIIv"
    elif Pf_eis_ond_dsn <= P_f_dsn < Pf_eis_ond:
        cat = "IVv"
    elif Pf_eis_ond <= P_f_dsn < 30.0 * Pf_eis_ond:
        cat = "Vv"
    elif P_f_dsn >= 30.0 * Pf_eis_ond and P_f_dsn <= 1.000:
        cat = "VIv"
    else:
        cat = "VIIv"
    return cat


def get_beta(results: dict, year_index: int, mechanism: str) -> float:
    """Get the reliability value of a mechanism for a given year index.

    :param results: dict of results.
    :param year_index: int of the year index.
    :param mechanism: str of the mechanism.
    :return: float of the reliability value.

    """
    if mechanism == Mechanism.SECTION.name:
        return results["Section"][year_index]
    elif mechanism == Mechanism.PIPING.name:
        return results["Piping"][year_index]
    elif mechanism == Mechanism.OVERFLOW.name:
        return results["Overflow"][year_index]
    elif mechanism == Mechanism.STABILITY.name:
        return results["StabilityInner"][year_index]
    elif mechanism == Mechanism.REVETMENT.name:
        return results["Revetment"][year_index]
    elif mechanism == "STABILITYINNER":
        return results["StabilityInner"][year_index]


def get_vr_config_from_dict(vr_config: dict) -> VrtoolConfig:
    _vr_config = VrtoolConfig()
    _vr_config.traject = vr_config["traject"]
    _vr_config.input_directory = Path(vr_config["input_directory"])
    _vr_config.output_directory = Path(vr_config["output_directory"])
    _vr_config.input_database_name = vr_config["input_database_name"]
    _vr_config.T = vr_config["T"]

    for meca in MechanismEnum:
        if meca.name in vr_config["excluded_mechanisms"]:
            _vr_config.excluded_mechanisms.append(meca)
    return _vr_config


def interpolate_beta_values(years_output: np.ndarray, betas: np.ndarray, years: np.ndarray) -> np.ndarray:
    """
    Function to interpolate the beta values for the years in the years_output list.
    If years_output is before years, then assigne the first value from betas.
    If years_output is after years, then assigne the last value from betas.


    :param years_output: The years for which the beta values need to be interpolated.
    :param betas: The beta values for the years in the years list.
    :param years: The years for which the beta values are known.
    :return: The interpolated beta values for the years_output list.
    """
    _betas_output = np.zeros(len(years_output))
    for i, year in enumerate(years_output):
        if year < years[0]:
            _betas_output[i] = betas[0]
        elif year > years[-1]:
            _betas_output[i] = betas[-1]
        else:
            _betas_output[i] = np.interp(year, years, betas)
    return _betas_output


def calculate_traject_probability(traject_prob):
    p_nonf = [1] * len(list(traject_prob.values())[0].values())
    for mechanism, data in traject_prob.items():
        if len(data) == 0:
            continue
        time, pf = zip(*sorted(data.items()))

        p_nonf = np.multiply(p_nonf, np.subtract(1, pf))
    return time, list(1 - p_nonf)


def get_traject_reliability(dike_sections: list["DikeSection"], type: str, unreinforced_sections: Optional[list] = None) -> dict:
    """From a list of DikeSection, return a formatted dict with the reliability of each section for each mechanism.
    This is a preparation for the calculation of the reliability of the dike trajectory.

    type should be one of the following: 'initial', 'doorsnede' or 'veiligheidsrendement', partial
    """
    if type == "initial":
        _traject_reliability = {
            MechanismEnum.PIPING: {section.name: {'beta': section.initial_assessment["Piping"], "time": section.years}
                                   for section in dike_sections},
            MechanismEnum.OVERFLOW: {
                section.name: {'beta': section.initial_assessment["Overflow"], "time": section.years} for section in
                dike_sections},
            MechanismEnum.STABILITY_INNER: {
                section.name: {'beta': section.initial_assessment["StabilityInner"], "time": section.years} for section
                in dike_sections},
            MechanismEnum.REVETMENT: {
                section.name: {'beta': section.initial_assessment["Revetment"], "time": section.years} for section in
                dike_sections if section.revetment is True },
        }
        # remove key revetment is section.revetment is False


    elif type == "doorsnede":
        _traject_reliability = {
            MechanismEnum.PIPING: {
                section.name: {'beta': section.final_measure_doorsnede["Piping"], "time": section.years}
                for section in dike_sections},
            MechanismEnum.OVERFLOW: {
                section.name: {'beta': section.final_measure_doorsnede["Overflow"], "time": section.years} for section
                in
                dike_sections},
            MechanismEnum.STABILITY_INNER: {
                section.name: {'beta': section.final_measure_doorsnede["StabilityInner"], "time": section.years} for
                section
                in dike_sections},
            MechanismEnum.REVETMENT: {
                section.name: {'beta': section.final_measure_doorsnede["Revetment"], "time": section.years} for section
                in
                dike_sections if section.revetment is True},
        }
    elif type == "veiligheidsrendement":

        _traject_reliability = {
            MechanismEnum.PIPING: {
                section.name: {'beta': section.final_measure_veiligheidsrendement["Piping"], "time": section.years}
                for section in dike_sections},
            MechanismEnum.OVERFLOW: {
                section.name: {'beta': section.final_measure_veiligheidsrendement["Overflow"], "time": section.years}
                for section in
                dike_sections},
            MechanismEnum.STABILITY_INNER: {
                section.name: {'beta': section.final_measure_veiligheidsrendement["StabilityInner"],
                               "time": section.years} for section
                in dike_sections},
            MechanismEnum.REVETMENT: {
                section.name: {'beta': section.final_measure_veiligheidsrendement["Revetment"], "time": section.years}
                for section in
                dike_sections if section.revetment is True},
        }

    elif type == "partial":
        _traject_reliability = {
            MechanismEnum.PIPING: {
                section.name: {'beta': section.final_measure_veiligheidsrendement["Piping"], "time": section.years}
                for section in dike_sections},
            MechanismEnum.OVERFLOW: {
                section.name: {'beta': section.final_measure_veiligheidsrendement["Overflow"], "time": section.years}
                for section in
                dike_sections},
            MechanismEnum.STABILITY_INNER: {
                section.name: {'beta': section.final_measure_veiligheidsrendement["StabilityInner"],
                               "time": section.years} for section
                in dike_sections},
            MechanismEnum.REVETMENT: {
                section.name: {'beta': section.final_measure_veiligheidsrendement["Revetment"], "time": section.years}
                for section in
                dike_sections if section.revetment is True},
        }
        # add unreinforced sections
        _traject_reliability[MechanismEnum.PIPING].update(
            {section.name: {'beta': section.initial_assessment["Piping"], "time": section.years} for section in
                unreinforced_sections})
        _traject_reliability[MechanismEnum.OVERFLOW].update(
            {section.name: {'beta': section.initial_assessment["Overflow"], "time": section.years} for section in
                unreinforced_sections})
        _traject_reliability[MechanismEnum.STABILITY_INNER].update(
            {section.name: {'beta': section.initial_assessment["StabilityInner"], "time": section.years} for section in
                unreinforced_sections})
        _traject_reliability[MechanismEnum.REVETMENT].update(
            {section.name: {'beta': section.initial_assessment["Revetment"], "time": section.years} for section in
                unreinforced_sections if section.revetment is True})

    else:
        raise ValueError("Type should be either 'initial', 'doorsnede' or 'veiligheidsrendement'")

    return _traject_reliability
