
from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.models import SectionData

from src.constants import SIGNALERING, ONDERGRENS
from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject

from src.orm.importers.dike_section_importer import DikeSectionImporter


class DikeTrajectImporter(OrmImporterProtocol):

    def __init__(self) -> None:
        pass
    def _import_dike_section_list(
        self, _orm_dike_section_list,
    ) -> list[DikeSection]:
        _ds_importer = DikeSectionImporter().import_orm()
        return list(map(_ds_importer.import_orm, _orm_dike_section_list))


    def _import_dike_section_list_og(
        self, orm_dike_section_list: list[SectionData]
    ) -> list[DikeSection]:
        _ds_importer = DikeSectionImporter()
        print(type(orm_dike_section_list))
        return list(map(_ds_importer.import_orm, orm_dike_section_list))



    def import_orm(self, orm_model) -> DikeTraject:
        print(orm_model, type(orm_model))
        _dike_traject = DikeTraject(name=orm_model.traject_name,
                                    dike_sections=[],
                                    reinforcement_order_vr=[],
                                    reinforcement_order_dsn=[],
                                    signalering_value=SIGNALERING,
                                    lower_bound_value=ONDERGRENS)

        print(_dike_traject)
        print(orm_model.dike_sections, type(orm_model.dike_sections))
        _selected_sections = orm_model.dike_sections.select().where(
            SectionData.in_analysis == True
        )
        print(_selected_sections)


        _dike_traject.dike_section = self._import_dike_section_list_og(orm_model.traject_name)


        # Currently it is assumed that all SectionData present in a db belongs to whatever traject name has been provided.
        _dike_traject.sections = self._import_dike_section_list(_selected_sections)
        # _mechanisms = self._select_available_mechanisms(orm_model)
        # _dike_traject.mechanism_names = list(set([_m.name for _m in _mechanisms]))

        _dike_traject = DikeTraject(name=orm_model.traject_name,
                                    dike_sections=[],
                                    reinforcement_order_vr=[],
                                    reinforcement_order_dsn=[],
                                    signalering_value=SIGNALERING,
                                    lower_bound_value=ONDERGRENS)

        return _dike_traject
