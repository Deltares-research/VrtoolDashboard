from peewee import FloatField, ForeignKeyField

from vrtool.orm.models.mechanism_per_section import MechanismPerSection
from vrtool.orm.models.orm_base_model import (
    OrmBaseModel,
    _get_table_name,
)


class ModifiedMeasure(OrmBaseModel):
    measure_per_section = ForeignKeyField(
        MechanismPerSection, backref="modified_measures"
    )
    dcrest = FloatField()
    dberm = FloatField()

    class Meta:
        table_name = _get_table_name(__qualname__)
