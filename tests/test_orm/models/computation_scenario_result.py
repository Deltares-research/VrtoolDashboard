from vrtool.orm.models.orm_base_model import OrmBaseModel

from src.orm.models import ComputationScenarioResult
from tests.test_orm import empty_db_fixture


class TestComputationScenarioResult:

    def test_initialize_with_database_fixture(self, empty_db_fixture):
        # Run test.
        _comp_scenario_result = ComputationScenarioResult.create(computation_scenario_id=1, year=1, beta=1)

        # Verify expectations.
        assert isinstance(_comp_scenario_result, ComputationScenarioResult)
        assert isinstance(_comp_scenario_result, OrmBaseModel)
