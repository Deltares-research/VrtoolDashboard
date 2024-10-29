
import numpy as np
import plotly.graph_objects as go
from matplotlib import pyplot as plt, colors

from src.constants import (
    REFERENCE_YEAR,
    ColorBarResultType,
    Mechanism,
    SubResultType,
    CalcType,
    ResultType,
)
from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject
from src.utils.gws_convertor import GWSRDConvertor
from src.utils.utils import to_million_euros, beta_to_pf, pf_to_beta, get_beta

color_dict = {""}

def plot_comparison_measures_map(imported_runs: dict) -> go.Figure:
    fig = go.Figure()
    return fig