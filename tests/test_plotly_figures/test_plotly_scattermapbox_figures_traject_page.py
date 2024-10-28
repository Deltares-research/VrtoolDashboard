import json
from enum import Enum
from pathlib import Path

import pytest
from plotly.graph_objs import Figure

from src.constants import ResultType, Mechanism, SubResultType, ColorBarResultType, CalcType
from src.linear_objects.dike_traject import DikeTraject
from src.plotly_graphs.plotly_maps import plot_dike_traject_reliability_initial_assessment_map, \
    plot_dike_traject_reliability_measures_assessment_map, plot_dike_traject_urgency, \
    dike_traject_pf_cost_helping_map_simple, \
    plot_default_overview_map_dummy, plot_overview_map, dike_traject_pf_cost_helping_map_detail


class TestPlotlyScatterMapBox():

    def test_plot_default_overview_map_dummy(self):
        # 1. Call
        _fig = plot_default_overview_map_dummy()

        # 2. Assert
        assert isinstance(_fig, Figure)

    def test_plot_overview_map(self):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/31-1 base coastal case/reference' / 'dike_data.json'))
        _dike_traject = DikeTraject.deserialize(_dike_data)

        # 2. Call
        _fig = plot_overview_map(_dike_traject)

        # 3. Assert
        assert isinstance(_fig, Figure)


    @pytest.mark.parametrize("result_type", [ResultType.RELIABILITY, ResultType.PROBABILITY])
    @pytest.mark.parametrize("mechanism",
                             [Mechanism.SECTION, Mechanism.PIPING, Mechanism.OVERFLOW, Mechanism.STABILITY])
    def test_plot_dike_traject_reliability_initial_assessment_map(self, result_type: Enum, mechanism: Enum):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/31-1 base coastal case/reference' / 'dike_data.json'))
        _dike_traject = DikeTraject.deserialize(_dike_data)

        # 2. Call
        _fig = plot_dike_traject_reliability_initial_assessment_map(_dike_traject,
                                                                    2025,
                                                                    result_type.name,
                                                                    mechanism.name)
        # 3. Assert
        assert isinstance(_fig, Figure)

    @pytest.mark.parametrize("result_type", [ResultType.RELIABILITY, ResultType.PROBABILITY])
    @pytest.mark.parametrize("calc_type", [CalcType.VEILIGHEIDSRENDEMENT, CalcType.DOORSNEDE_EISEN])
    @pytest.mark.parametrize("sub_result_type", [SubResultType.ABSOLUTE, SubResultType.RATIO])
    def test_plot_dike_traject_reliability_measures_assessment_map_reliability(self, result_type: Enum, calc_type: Enum,
                                                                               sub_result_type: Enum):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/31-1 base coastal case/reference' / 'dike_data.json'))
        _dike_traject = DikeTraject.deserialize(_dike_data)

        # 2. Call
        _fig = plot_dike_traject_reliability_measures_assessment_map(_dike_traject,
                                                                     2025,
                                                                     result_type.name,
                                                                     calc_type.name,
                                                                     ColorBarResultType.RELIABILITY.name,
                                                                     Mechanism.SECTION.name,
                                                                     sub_result_type.name)

        # 3. Assert
        assert isinstance(_fig, Figure)

    @pytest.mark.parametrize("result_type", [ResultType.RELIABILITY, ResultType.PROBABILITY])
    @pytest.mark.parametrize("calc_type", [CalcType.VEILIGHEIDSRENDEMENT, CalcType.DOORSNEDE_EISEN])
    @pytest.mark.parametrize("sub_result_type", [SubResultType.ABSOLUTE, SubResultType.DIFFERENCE])
    def test_plot_dike_traject_reliability_measures_assessment_map_cost(self, result_type: Enum, calc_type: Enum,
                                                                        sub_result_type: Enum):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/31-1 base coastal case/reference' / 'dike_data.json'))
        _dike_traject = DikeTraject.deserialize(_dike_data)

        # 2. Call
        _fig = plot_dike_traject_reliability_measures_assessment_map(_dike_traject,
                                                                     2025,
                                                                     result_type.name,
                                                                     calc_type.name,
                                                                     ColorBarResultType.COST.name,
                                                                     Mechanism.SECTION.name,
                                                                     sub_result_type.name)

        # 3. Assert
        assert isinstance(_fig, Figure)

    @pytest.mark.parametrize("calc_type", [CalcType.VEILIGHEIDSRENDEMENT, CalcType.DOORSNEDE_EISEN])
    @pytest.mark.parametrize("sub_result_type", [SubResultType.MEASURE_TYPE, SubResultType.BERM_WIDENING, SubResultType.CREST_HIGHTENING, SubResultType.INVESTMENT_YEAR])
    def test_plot_dike_traject_reliability_measures_assessment_map_measure(self,calc_type: Enum,
                                                                        sub_result_type: Enum):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/31-1 base coastal case/reference' / 'dike_data.json'))
        _dike_traject = DikeTraject.deserialize(_dike_data)

        # 2. Call
        _fig = plot_dike_traject_reliability_measures_assessment_map(_dike_traject,
                                                                     2025,
                                                                     ResultType.RELIABILITY.name,
                                                                     calc_type.name,
                                                                     ColorBarResultType.MEASURE.name,
                                                                     Mechanism.SECTION.name,
                                                                     sub_result_type.name)

        # 3. Assert
        assert isinstance(_fig, Figure)

    @pytest.mark.parametrize("calc_type", [CalcType.VEILIGHEIDSRENDEMENT, CalcType.DOORSNEDE_EISEN])
    def test_plot_dike_traject_urgency(self, calc_type: Enum):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/31-1 base coastal case/reference' / 'dike_data.json'))
        _dike_traject = DikeTraject.deserialize(_dike_data)

        # 2. Call
        _fig = plot_dike_traject_urgency(_dike_traject, 2025, 20, calc_type.name)

        # 3. Assert
        assert isinstance(_fig, Figure)

    def test_dike_traject_pf_cost_helping_map_simple(self):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/31-1 base coastal case/reference' / 'dike_data.json'))
        _dike_traject = DikeTraject.deserialize(_dike_data)

        # 2. Call
        _fig1 = dike_traject_pf_cost_helping_map_simple(_dike_traject, 0, ["33"])
        _fig2 = dike_traject_pf_cost_helping_map_simple(_dike_traject, 0, ["93"])  # this one has a grey dijkvak

        # 3. Assert
        assert isinstance(_fig1, Figure)
        assert isinstance(_fig2, Figure)

    def test_dike_traject_pf_cost_helping_map_detailed(self):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/31-1 base coastal case/reference' / 'dike_data.json'))
        _dike_traject = DikeTraject.deserialize(_dike_data)

        # 2. Call
        _fig1 = dike_traject_pf_cost_helping_map_detail(_dike_traject, 0, ["33"])
        _fig2 = dike_traject_pf_cost_helping_map_detail(_dike_traject, 0, ["93"])  # this one has a grey dijkvak

        # 3. Assert
        assert isinstance(_fig1, Figure)
        assert isinstance(_fig2, Figure)


