from pathlib import Path

from geopandas import GeoDataFrame
from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.models import SectionData, MeasurePerSection

from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject

from src.orm.importers.dike_section_importer import DikeSectionImporter
from src.orm.models import GreedyOptimizationOrder, TargetReliabilityBasedOrder, ModifiedMeasure
from src.orm.models.dike_traject_info import DikeTrajectInfo

import geopandas as gpd


class DikeTrajectImporter(OrmImporterProtocol):
    path_dir: Path
    traject_name: str

    def __init__(self, path_dir: Path, traject_name: str) -> None:
        self.path_dir = path_dir
        self.traject_name = traject_name

    def _import_dike_section_list(
            self, orm_dike_section_list: list[SectionData], traject_gdf: GeoDataFrame
    ) -> list[DikeSection]:
        _ds_importer = DikeSectionImporter(traject_gdf)
        return list(map(_ds_importer.import_orm, orm_dike_section_list))

    def parse_geo_dataframe(self, traject_geojson_name: str) -> GeoDataFrame:
        """Open the geojson of the spatial coordinates of the dike traject and parse it to a GeoDataFrame

        /!\ This function might not be general enough to accomodate to every variation of column names.
        """
        _traject_gdf = gpd.read_file(self.path_dir / traject_geojson_name)
        _traject_gdf["geometry"] = _traject_gdf["geometry"].apply(
            lambda x: list(x.coords))  # Serialize the geometry column to a list of coordinates

        # if vaknaam is a single digit, add a 0 in front of it
        _traject_gdf["vaknaam"] = _traject_gdf["vaknaam"].apply(lambda x: x.zfill(2))

        # rename vaknaam to section_name
        _traject_gdf.rename(columns={"vaknaam": "section_name"}, inplace=True)

        return _traject_gdf[["geometry", "section_name"]]

    def _get_reinforcement_order(self, assessment_type: str) -> list[str]:
        """
        Get the reinforcement order for the given assessment type
        :param assessment_type: one of "GreedyOptimizationBased" or "TargetReliabilityBased"
        :return:
        """

        _order_table = GreedyOptimizationOrder if assessment_type == "GreedyOptimizationBased" else TargetReliabilityBasedOrder

        _ordered_sections = []
        for row in _order_table.select().order_by(_order_table.optimization_step):
            _modified_measure = ModifiedMeasure.get(ModifiedMeasure.id == row.modified_measure_id)

            _measure_per_section = MeasurePerSection.get(
                MeasurePerSection.id == _modified_measure.measure_per_section_id)

            _section = SectionData.get(SectionData.id == _measure_per_section.section_id)

            _dike_traject_name = DikeTrajectInfo.get(DikeTrajectInfo.id == _section.dike_traject_id).traject_name

            if _dike_traject_name == self.traject_name:
                _ordered_sections.append(_section.section_name)

        return _ordered_sections

    def import_orm(self, orm_model) -> DikeTraject:
        """Import a DikeTraject object from the ORM """
        _traject_name = orm_model.DikeTrajectInfo.get(
            orm_model.DikeTrajectInfo.traject_name == self.traject_name).traject_name
        _traject_id = DikeTrajectInfo.get(DikeTrajectInfo.traject_name == _traject_name).id
        _traject_geojson = DikeTrajectInfo.get(DikeTrajectInfo.traject_name == _traject_name).name_geojson
        _traject_p_signal = DikeTrajectInfo.get(DikeTrajectInfo.traject_name == _traject_name).p_signal
        _traject_p_lower_bound = DikeTrajectInfo.get(DikeTrajectInfo.traject_name == _traject_name).p_max

        _dike_traject = DikeTraject(name=_traject_name,
                                    dike_sections=[],
                                    reinforcement_order_vr=[],
                                    reinforcement_order_dsn=[],
                                    signalering_value=_traject_p_signal,
                                    lower_bound_value=_traject_p_lower_bound)
        _selected_sections = orm_model.SectionData.select().where(
            SectionData.dike_traject == _traject_id
        )
        _traject_gdf = self.parse_geo_dataframe(_traject_geojson)

        _dike_traject.dike_sections = self._import_dike_section_list(_selected_sections, _traject_gdf)
        _dike_traject.reinforcement_order_vr = self._get_reinforcement_order("GreedyOptimizationBased")
        _dike_traject.reinforcement_order_dsn = self._get_reinforcement_order("TargetReliabilityBased")

        return _dike_traject
