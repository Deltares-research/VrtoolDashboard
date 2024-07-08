import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

import pytest
from vrtool.defaults.vrtool_config import VrtoolConfig

from peewee import SqliteDatabase

from src.orm.import_database import get_dike_traject_from_config_ORM
from src.utils.utils import export_to_json
from tests import get_test_results_dir

vrtool_db = SqliteDatabase(None)

test_data = Path(__file__).parent.parent / "data"
vrtool_db_default_name = "vrtool_input.db"


@dataclass
class AcceptanceTestCase:
    case_name: str
    case_directory: str
    traject_name: str
    excluded_mechanisms: list[str]
    database_name: str

    @staticmethod
    def get_cases() -> list['AcceptanceTestCase']:
        # Defining acceptance test cases so they are accessible from the other test classes.
        return [
            # AcceptanceTestCase(
            #     case_directory="Case_10_3",
            #     traject_name="10-3",
            #     case_name="10-3",
            #     excluded_mechanisms=["REVETMENT", "HYDRAULIC_STRUCTURES"],
            #     database_name="database_10-3.db",
            # ),
            # AcceptanceTestCase(
            #     case_directory="Case_24_3",
            #     traject_name="24-3",
            #     case_name="24-3",
            #     excluded_mechanisms=[],
            #     database_name="24-3_results_vrtool_0_1_1.db",
            # ),
            # AcceptanceTestCase(
            #     case_directory="Case_31_1",
            #     traject_name="31-1",
            #     case_name="31-1",
            #     excluded_mechanisms=[],
            #     database_name="database_31-1.db",
            # ),
        ]


acceptance_test_cases = list(
    map(
        lambda x: pytest.param(x, id=x.case_name),
        AcceptanceTestCase.get_cases(),
    )
)


class TestDikeTrajectImporter:

    @pytest.fixture
    def valid_vrtool_config(self, request: pytest.FixtureRequest) -> VrtoolConfig:
        _test_case: AcceptanceTestCase = request.param
        _test_input_directory = Path.joinpath(test_data, _test_case.case_directory)
        assert _test_input_directory.exists()

        _test_results_directory = get_test_results_dir(request).joinpath(
            _test_case.case_name
        )
        if _test_results_directory.exists():
            shutil.rmtree(_test_results_directory)
        _test_results_directory.mkdir(parents=True)

        # Define the VrtoolConfig
        _test_config = VrtoolConfig()
        _test_config.input_directory = _test_input_directory
        _test_config.output_directory = _test_results_directory
        _test_config.traject = _test_case.traject_name
        _test_config.excluded_mechanisms = _test_case.excluded_mechanisms

        # We need to create a copy of the database on the input directory.
        _test_db_name = "test_{}.db".format(
            hashlib.shake_128(_test_results_directory.__bytes__()).hexdigest(4)
        )
        _test_config.input_database_name = _test_db_name

        # Create a copy of the database to avoid parallelization runs locked databases.
        _reference_db_file = _test_input_directory.joinpath(_test_case.database_name)
        assert _reference_db_file.exists(), "No database found at {}.".format(
            _reference_db_file
        )

        if _test_config.input_database_path.exists():
            # Somehow it was not removed in the previous test run.
            _test_config.input_database_path.unlink(missing_ok=True)

        shutil.copy(_reference_db_file, _test_config.input_database_path)
        assert (
            _test_config.input_database_path.exists()
        ), "No database found at {}.".format(_reference_db_file)

        yield _test_config

        # Make sure that the database connection will be closed even if the test fails.
        if isinstance(vrtool_db, SqliteDatabase) and not vrtool_db.is_closed():
            vrtool_db.close()

        # # Copy the test database to the results directory so it can be manually reviewed.
        # if _test_config.input_database_path.exists():
        #     _results_db_name = _test_config.output_directory.joinpath(
        #         "vrtool_result.db"
        #     )
        #     shutil.move(_test_config.input_database_path, _results_db_name)

    @pytest.mark.parametrize(
        "valid_vrtool_config",
        acceptance_test_cases,
        indirect=True,
    )
    def test_importer_dike_traject(self, valid_vrtool_config: VrtoolConfig):

        # 1. Import the dike traject from database
        _dike_traject = get_dike_traject_from_config_ORM(valid_vrtool_config, run_id_dsn=2, run_is_vr=1)
        _dike_traject.run_name = "Basisberekening"
        _serialized_traject = _dike_traject.serialize()

        # 2. Validate results
        _test_reference_dir = valid_vrtool_config.input_directory.joinpath("reference")
        _files_to_compare = [
            "reference_dike_traject.json",
        ]

        comparison_errors = []
        for file in _files_to_compare:
            # load jsons:
            with open(_test_reference_dir.joinpath(file), 'r') as f:
                reference = json.load(f)

            export_to_json(_serialized_traject, path=valid_vrtool_config.output_directory.joinpath(file))
            with open(valid_vrtool_config.output_directory.joinpath(file), 'r') as f:
                results = json.load(f)

            try:
                assert reference.keys() == results.keys()
                assert reference['dike_sections'][0].keys() == results['dike_sections'][0].keys()
                assert reference == results

            except Exception:
                comparison_errors.append("{} is different.".format(file))
        # assert no error message has been registered, else print messages
        assert not comparison_errors, "errors occured:\n{}".format(
            "\n".join(comparison_errors)
        )

    @pytest.mark.parametrize(
        "valid_vrtool_config",
        acceptance_test_cases,
        indirect=True,
    )
    def test_calc_traject_probability_array(self, valid_vrtool_config: VrtoolConfig):
        # 1. Import the dike traject from database
        _dike_traject = get_dike_traject_from_config_ORM(valid_vrtool_config, run_id_dsn=2, run_is_vr=1)

        # 2. Calculate the probability array
        _probability_array_vr = _dike_traject.calc_traject_probability_array("vr")
        _probability_array_dsn = _dike_traject.calc_traject_probability_array("dsn")

        # export to json
        export_to_json(_probability_array_vr,
                       path=valid_vrtool_config.output_directory.joinpath("reference_probability_array_vr.json"))
        export_to_json(_probability_array_dsn,
                       path=valid_vrtool_config.output_directory.joinpath("reference_probability_array_dsn.json"))

        # 3. Validate results
        _test_reference_dir = valid_vrtool_config.input_directory.joinpath("reference")
        _files_to_compare = [
            "reference_probability_array_vr.json",
            "reference_probability_array_dsn.json",
        ]

        comparison_errors = []
        for file in _files_to_compare:
            # load jsons:
            with open(_test_reference_dir.joinpath(file), 'r') as f:
                reference = json.load(f)

            if "vr" in file:
                results = _probability_array_vr
            else:
                results = _probability_array_dsn

            try:
                assert reference == results

            except Exception:
                comparison_errors.append("{} is different.".format(file))
