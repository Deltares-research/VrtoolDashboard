from peewee import FloatField, ForeignKeyField, CharField, IntegerField

from vrtool.orm.models.mechanism_per_section import MechanismPerSection
from vrtool.orm.models.orm_base_model import (
    OrmBaseModel,
    _get_table_name, _max_char_length,
)


class MeasureReliability(OrmBaseModel):
    modified_measure = ForeignKeyField(
        MechanismPerSection, backref="measure_cost"
    )
    time = IntegerField()
    mechanism = CharField(max_length=_max_char_length)
    beta = FloatField()

    class Meta:
        table_name = _get_table_name(__qualname__)
