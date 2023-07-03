from scipy.stats import norm

def to_million_euros(cost: float) -> float:
    """Converts a cost in euros to millions of euros"""
    return round(cost / 1e6, 2)


def beta_to_pf(beta):
    # alternative: use scipy
    return norm.cdf(-beta)


def pf_to_beta(pf):
    # alternative: use scipy
    return -norm.ppf(pf)