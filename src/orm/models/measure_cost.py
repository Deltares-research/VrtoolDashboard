from peewee import CharField, FloatField, ForeignKeyField, IntegerField

from vrtool.orm.models.mechanism_per_section import MechanismPerSection
from vrtool.orm.models.orm_base_model import (
    OrmBaseModel,
    _get_table_name,
    _max_char_length,
)


class MeasureCost(OrmBaseModel):
    modified_measure = ForeignKeyField(
        MechanismPerSection, backref="measure_cost"
    )
    cost = FloatField()

    class Meta:
        table_name = _get_table_name(__qualname__)
