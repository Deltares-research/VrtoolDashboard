from peewee import FloatField, ForeignKeyField

from vrtool.orm.models.mechanism_per_section import MechanismPerSection
from vrtool.orm.models.orm_base_model import (
    OrmBaseModel,
    _get_table_name,
)


class MeasureReliability(OrmBaseModel):
    modified_measure = ForeignKeyField(
        MechanismPerSection, backref="measure_reliability"
    )
    cost = FloatField()

    class Meta:
        table_name = _get_table_name(__qualname__)
