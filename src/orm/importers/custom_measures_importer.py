from vrtool.common.enums import CombinableTypeEnum
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.models import CustomMeasureDetail, Measure, Mechanism, MechanismPerSection, SectionData


class CustomMeasureImporter(OrmImporterProtocol):

    def __init__(
            self,
            vr_config: VrtoolConfig,

    ) -> None:
        self.vr_config = vr_config

    def import_orm(self, orm_model) -> list:
        """
        Import the custom measures from the database.

        :param orm_model: ORM model
        :return: list of custom measures
        """

        _res = []
        _custom_measure_results = (CustomMeasureDetail().select()
                                   .join(Measure)
                                   )
        for cm_detail in _custom_measure_results:
            _mechanism_per_section = MechanismPerSection().select().where(
                MechanismPerSection.id == cm_detail.mechanism_per_section_id).get()
            _section = SectionData().select().where(SectionData.id == _mechanism_per_section.section_id).get()
            _mechanism = Mechanism().select().where(Mechanism.id == _mechanism_per_section.mechanism_id).get()
            _measure = Measure().select().where(Measure.id == cm_detail.measure_id).get()

            _cm_data = dict(beta=cm_detail.beta,
                            cost=cm_detail.cost,
                            time=cm_detail.year,
                            section_name=_section.section_name,
                            mechanism=_mechanism.name,
                            measure_name=_measure.name,
                            # COMBINABLE_TYPE_TYPE=CombinableTypeEnum.FULL.name,
                            )

            _res.append(_cm_data)
        return _res
