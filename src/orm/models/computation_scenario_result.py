from peewee import CharField, FloatField, ForeignKeyField, IntegerField

from vrtool.orm.models.mechanism_per_section import MechanismPerSection
from vrtool.orm.models.orm_base_model import (
    OrmBaseModel,
    _get_table_name,
)


class ComputationScenarioResult(OrmBaseModel):
    computation_scenario_id = ForeignKeyField(
        MechanismPerSection, backref="computation_scenarios_result"
    )
    year = IntegerField()
    beta = FloatField()

    class Meta:
        table_name = _get_table_name(__qualname__)
