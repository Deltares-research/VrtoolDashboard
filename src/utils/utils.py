from pathlib import Path

from scipy.stats import norm
import json

from src.constants import SIGNALERING, ONDERGRENS


def to_million_euros(cost: float) -> float:
    """Converts a cost in euros to millions of euros"""
    return round(cost / 1e6, 2)


def beta_to_pf(beta):
    # alternative: use scipy
    return norm.cdf(-beta)


def pf_to_beta(pf):
    # alternative: use scipy
    return -norm.ppf(pf)


def export_to_json(data):
    # convert dike_traject_data to json :
    # write to a json file:
    path = Path(__file__).parent / 'data.json'
    with open(path, 'w') as outfile:
        json.dump(data, outfile)


def get_WBI_category(P_f_dsn: float, traject_length: float) -> str:
    """

    Function to determine the WBI catgeory of a dike section based on its cross-sectional probability of failure and
    on norm probabilities of failure.
    Is this function correct? Weird assumptions here with N_dsn and w.

    :param P_f_dsn: Probability of failure of the section
    :param traject_length: Length of the dike trajectory in meters
    :return:
    """

    # Normering
    Pf_eis_sign = SIGNALERING
    Pf_eis_ond = ONDERGRENS

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
