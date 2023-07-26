from peewee import ForeignKeyField, IntegerField

from vrtool.orm.models.mechanism_per_section import MechanismPerSection
from vrtool.orm.models.orm_base_model import (
    OrmBaseModel,
    _get_table_name,
)


class GreedyOptimizationOrder(OrmBaseModel):
    modified_measure = ForeignKeyField(
        MechanismPerSection, backref="greedy_optimization_order"
    )
    optimization_step = IntegerField()

    class Meta:
        table_name = _get_table_name(__qualname__)
