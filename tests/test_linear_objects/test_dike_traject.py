import json
from pathlib import Path

import numpy as np
from vrtool.common.enums import MechanismEnum

from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject, get_traject_prob, get_initial_assessment_df, \
    get_traject_prob_fast
from src.utils.utils import get_traject_reliability


class TestDikeTraject:
    def test_deserialize(self):
        """ Test if the DikeTraject object can be deserialized from a dict correctly"""
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/31-1 base coastal case/reference' / 'dike_data.json'))

        # 2. Define test
        _dike_traject = DikeTraject.deserialize(_dike_data)
        _dike_section_1 = _dike_traject.dike_sections[0]

        # 3. Assert
        assert isinstance(_dike_traject, DikeTraject)
        assert isinstance(_dike_traject.dike_sections, list)
        assert isinstance(_dike_traject.name, str)

        assert isinstance(_dike_section_1, DikeSection)
        assert isinstance(_dike_section_1.name, str)
        assert isinstance(_dike_section_1.coordinates_rd, list)
        assert isinstance(_dike_section_1.final_measure_doorsnede, dict)
        assert isinstance(_dike_section_1.final_measure_veiligheidsrendement, dict)
        assert isinstance(_dike_section_1.initial_assessment, dict)

    def test_get_traject_prob(self):
        # 1. Define data
        _dike_data = json.load(
            open(Path(__file__).parent.parent / 'data/31-1 base coastal case/reference' / 'dike_data.json'))

        # 2. Define test
        _dike_traject = DikeTraject.deserialize(_dike_data)
        dike_sections = _dike_traject.dike_sections

        _traject_reliability = get_traject_reliability(dike_sections, 'initial')
        _traject_pf = get_traject_prob_fast(_traject_reliability)[1]

        # 3. Assert
        _expected_traject_pf = np.array(
            [[0.02938911, 0.02957493, 0.02958784, 0.02965843, 0.03022501, 0.03147336, 0.03413831]])
        # _expected_res_2 = {'Overflow': np.array([0.00014024, 0.00027972, 0.00028995, 0.0003468, 0.00083413,
        #                                          0.00198239, 0.00452094]),
        #                    'Piping': np.array([1.68673435e-05, 2.39223517e-05, 2.43596051e-05, 2.66576876e-05,
        #                                        4.14124848e-05, 6.32569054e-05, 9.50274736e-05]),
        #                    'StabilityInner': np.array([0.02900858, 0.02900858, 0.02900858, 0.02900858, 0.02900858,
        #                                                0.02900858, 0.02900858]),
        #                    'Revetment': np.array([0.00022343, 0.00026271, 0.00026495, 0.0002764, 0.00034088,
        #                                           0.00041913, 0.00051377])}

        assert np.allclose(_traject_pf, _expected_traject_pf, atol=1e-2)
