from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.models import SectionData, DikeTrajectInfo

from src.constants import SIGNALERING, ONDERGRENS
from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject

from src.orm.importers.dike_section_importer import DikeSectionImporter


class DikeTrajectImporter(OrmImporterProtocol):

    def __init__(self) -> None:
        pass

    def _import_dike_section_list(
            self, orm_dike_section_list: list[SectionData]
    ) -> list[DikeSection]:
        _ds_importer = DikeSectionImporter()
        return list(map(_ds_importer.import_orm, orm_dike_section_list))

    def import_orm(self, orm_model) -> DikeTraject:
        traject_name = orm_model.DikeTrajectInfo.get(orm_model.DikeTrajectInfo.traject_name == "38-1").traject_name
        _dike_traject = DikeTraject(name=traject_name,
                                    dike_sections=[],
                                    reinforcement_order_vr=[],
                                    reinforcement_order_dsn=[],
                                    signalering_value=SIGNALERING,
                                    lower_bound_value=ONDERGRENS)

        _selected_sections = orm_model.SectionData.select()


        _dike_traject.dike_section = self._import_dike_section_list(_selected_sections)

        _dike_traject = DikeTraject(name=traject_name,
                                    dike_sections=[],
                                    reinforcement_order_vr=[],
                                    reinforcement_order_dsn=[],
                                    signalering_value=SIGNALERING,
                                    lower_bound_value=ONDERGRENS)

        return _dike_traject
