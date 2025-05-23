import json
from pathlib import Path

from vrtool.defaults.vrtool_config import VrtoolConfig

from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject
from src.orm.import_database import get_dike_traject_from_config_ORM, get_name_optimization_runs, \
    get_run_optimization_ids


class TestOrmControllers:

    def test_initialization_get_dike_traject_from_ORM(self):
        _vr_config = VrtoolConfig().from_json(
            Path(__file__).parent.parent / "data/TestCase1_38-1_no_housing/vr_config.json")
        _vr_config.input_directory = Path(__file__).parent.parent / "data/TestCase1_38-1_no_housing"

        _dike_traject = get_dike_traject_from_config_ORM(_vr_config, run_id_dsn=2, run_is_vr=1)

        assert isinstance(_dike_traject, DikeTraject)
        assert isinstance(_dike_traject.dike_sections[0], DikeSection)

    def test_get_dike_traject_from_ORM_returns_correct_dike_traject(self):
        # 1. Define data
        with open(Path(__file__).parent.parent / "data/serialized_traject_38_1_mini.json", "r") as f:
            _expected_serialized_traject = json.load(f)
        _vr_config = VrtoolConfig().from_json(
            Path(__file__).parent.parent / "data/TestCase1_38-1_no_housing/vr_config.json")
        _vr_config.input_directory = Path(__file__).parent.parent / "data/TestCase1_38-1_no_housing"

        # 2. Define test
        _dike_traject = get_dike_traject_from_config_ORM(_vr_config, run_id_dsn=2, run_is_vr=1)
        _serialized_traject = _dike_traject.serialize()

        # 3. Assert
        for section_expected, section_actual in zip(_expected_serialized_traject["dike_sections"],
                                                    _serialized_traject["dike_sections"]):
            assert section_expected["name"] == section_actual["name"]
            # assert section_expected["final_measure_doorsnede"] == section_actual["final_measure_doorsnede"]
            # assert section_expected["final_measure_veiligheidrendement"] == section_actual["final_measure_veiligheidrendement"]
            assert section_expected["initial_assessment"] == section_actual["initial_assessment"]
            assert section_expected["years"] == section_actual["years"]

        assert _expected_serialized_traject["reinforcement_order_vr"] == _serialized_traject["reinforcement_order_vr"]
        assert _expected_serialized_traject["reinforcement_order_dsn"] == _serialized_traject["reinforcement_order_dsn"]
        assert _expected_serialized_traject["signalering_value"] == _serialized_traject["signalering_value"]
        assert _expected_serialized_traject["lower_bound_value"] == _serialized_traject["lower_bound_value"]

    def test_get_name_optimization_runs(self):
        # 1. Define data
        vr_config = VrtoolConfig().from_json(
            Path(__file__).parent.parent / "data/TestCase1_38-1_no_housing/vr_config.json")
        vr_config.input_directory = Path(__file__).parent.parent / "data/TestCase1_38-1_no_housing"

        # 2. Define test
        names = get_name_optimization_runs(vr_config)

        # 3. Assert
        assert isinstance(names, list)
        assert isinstance(names[0], str)

    def test_get_run_optimization_ids(self):
        # 1. Define data
        vr_config = VrtoolConfig().from_json(
            Path(__file__).parent.parent / "data/TestCase1_38-1_no_housing/vr_config.json")
        vr_config.input_directory = Path(__file__).parent.parent / "data/TestCase1_38-1_no_housing"

        # 2. Define test
        id_vr, id_dsn = get_run_optimization_ids(vr_config, optimization_run_name="Basisberekening")

        # 3. Assert
        assert isinstance(id_vr, int)
        assert isinstance(id_dsn, int)
        assert (id_vr == 1)
        assert (id_dsn == 2)
