from peewee import ForeignKeyField, IntegerField

from vrtool.orm.models.mechanism_per_section import MechanismPerSection
from vrtool.orm.models.orm_base_model import (
    OrmBaseModel,
    _get_table_name,
)


class TargetReliabilityBasedOrder(OrmBaseModel):
    modified_measure = ForeignKeyField(
        MechanismPerSection, backref="target_reliability_based_order"
    )
    optimization_step = IntegerField()

    class Meta:
        table_name = _get_table_name(__qualname__)
