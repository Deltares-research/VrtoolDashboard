import json
from pathlib import Path

from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject


class TestDikeTraject:
    def test_deserialize(self):
        """ Test if the DikeTraject object can be deserialized from a dict correctly"""
        # 1. Define data
        _dike_data = json.load(open(Path(__file__).parent.parent / 'data/TestCase_38_1_full/reference' / 'dike_traject_data_all.json'))

        # 2. Define test
        _dike_traject = DikeTraject.deserialize(_dike_data)
        _dike_section_1 = _dike_traject.dike_sections[10]

        # 3. Assert
        assert isinstance(_dike_traject, DikeTraject)
        assert isinstance(_dike_traject.dike_sections, list)
        assert isinstance(_dike_traject.name, str)

        assert isinstance(_dike_section_1, DikeSection)
        assert isinstance(_dike_section_1.name, str)
        assert isinstance(_dike_section_1.coordinates_rd, list)
        assert isinstance(_dike_section_1.final_measure_doorsnede, dict)
        assert isinstance(_dike_section_1.final_measure_veiligheidrendement, dict)
        assert isinstance(_dike_section_1.initial_assessment, dict)




