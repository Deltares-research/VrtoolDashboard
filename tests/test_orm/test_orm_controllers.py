import json
from pathlib import Path

from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject
from src.orm.import_database import get_dike_traject_from_ORM


class TestOrmControllers:

    def test_initialization_get_dike_traject_from_ORM(self):
        _dike_traject = get_dike_traject_from_ORM("38-1")

        assert isinstance(_dike_traject, DikeTraject)
        assert isinstance(_dike_traject.dike_sections[0], DikeSection)

    def test_get_dike_traject_from_ORM_returns_correct_dike_traject(self):
        # 1. Define data
        with open(Path(__file__).parent.parent / "data/serialized_traject_38_1_mini.json", "r") as f:
            _expected_serialized_traject = json.load(f)

        # 2. Define test
        _dike_traject = get_dike_traject_from_ORM("38-1")
        _serialized_traject = _dike_traject.serialize()

        # 3. Assert
        for section_expected, section_actual in zip(_expected_serialized_traject["dike_sections"], _serialized_traject["dike_sections"]):
            assert section_expected["name"] == section_actual["name"]
            # assert section_expected["final_measure_doorsnede"] == section_actual["final_measure_doorsnede"]
            # assert section_expected["final_measure_veiligheidrendement"] == section_actual["final_measure_veiligheidrendement"]
            assert section_expected["initial_assessment"] == section_actual["initial_assessment"]
            assert section_expected["years"] == section_actual["years"]

        assert _expected_serialized_traject["reinforcement_order_vr"] == _serialized_traject["reinforcement_order_vr"]
        assert _expected_serialized_traject["reinforcement_order_dsn"] == _serialized_traject["reinforcement_order_dsn"]
        assert _expected_serialized_traject["signalering_value"] == _serialized_traject["signalering_value"]
        assert _expected_serialized_traject["lower_bound_value"] == _serialized_traject["lower_bound_value"]
