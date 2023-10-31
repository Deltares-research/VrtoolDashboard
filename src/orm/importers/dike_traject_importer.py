from pathlib import Path

from geopandas import GeoDataFrame
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.io.importers.optimization.optimization_step_importer import OptimizationStepImporter
from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.models import SectionData, MeasurePerSection
from vrtool.orm.orm_controllers import get_optimization_steps

from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject

from src.orm.importers.dike_section_importer import DikeSectionImporter
from src.orm.models import OptimizationSelectedMeasure, OptimizationStep, MeasureResult
from src.orm.models.dike_traject_info import DikeTrajectInfo

import geopandas as gpd

from src.utils.utils import get_signal_value


class DikeTrajectImporter(OrmImporterProtocol):
    vr_config: VrtoolConfig
    path_dir: Path
    traject_name: str
    run_id_vr: int
    run_id_dsn: int

    def __init__(self, vr_config: VrtoolConfig, run_id_vr: int, run_id_dsn: int) -> None:
        """

        :param vr_config: VrtoolConfig object
        :param run_id_vr: run id in the database for which the veiligheidsrendement optimization results must be
         imported
        :param run_id_dsn: run id in the database for which the doorsnede eisen optimization results must be imported.
        """
        self.vr_config = vr_config
        self.path_dir = Path(vr_config.input_directory)
        self.traject_name = vr_config.traject
        self.run_id_vr = run_id_vr
        self.run_id_dsn = run_id_dsn

    def _import_dike_section_list(
            self, orm_dike_section_list: list[SectionData], traject_gdf: GeoDataFrame,
            final_greedy_step_id: int
    ) -> list[DikeSection]:
        """Import the dike sections from the ORM to a list of DikeSection objects

        :param orm_dike_section_list: list of ORM SectionData objects
        :param traject_gdf: GeoDataFrame of the dike trajectory
        :param run_id: id of the optimization run for veiligheidsrendement (default 1)
        :param final_greedy_step_id: id of the final step of the greedy optimization
        """
        _ds_importer = DikeSectionImporter(traject_gdf,
                                           run_id_dsn=self.run_id_dsn,
                                           run_id_vr=self.run_id_vr,
                                           final_greedy_step_id=final_greedy_step_id)

        return list(map(_ds_importer.import_orm, orm_dike_section_list))

    def parse_geo_dataframe(self, traject_name: str) -> GeoDataFrame:
        """Open the geojson of the spatial coordinates of the dike traject and parse it to a GeoDataFrame

        /!\ This function might not be general enough to accomodate to every variation of column names.
        """
        _traject_gdf = gpd.read_file(self.path_dir / traject_name.__add__(".geojson"))
        _traject_gdf["geometry"] = _traject_gdf["geometry"].apply(
            lambda x: list(x.coords))  # Serialize the geometry column to a list of coordinates

        if not "vaknaam" in _traject_gdf.columns:
            raise ValueError("No column named <vaknaam> in the geojson file.")

        # rename vaknaam to section_name
        _traject_gdf.rename(columns={"vaknaam": "section_name"}, inplace=True)

        return _traject_gdf[["geometry", "section_name"]]

    def _get_reinforcement_section_order_dsn(self, run_id: int) -> list[str]:
        """Get the reinforcement order of the section names for Doorsnede Eisen"""
        _optimization_steps = get_optimization_steps(run_id)

        _ordered_section_names = [
            SectionData.select(SectionData.section_name)
            .join(MeasurePerSection)
            .join(MeasureResult)
            .join(OptimizationSelectedMeasure)
            .where(OptimizationSelectedMeasure.id == step.optimization_selected_measure_id)
            .get()
            .section_name
            for step in _optimization_steps
        ]

        return _ordered_section_names

    def _get_reinforcement_section_order_vr(self, run_id) -> tuple[list[str], int]:
        """Get the reinforcement order of the section names for Veiligheidsrendement and return the final step id of the
         greedy optimization """
        _optimization_steps = get_optimization_steps(run_id)

        _ordered_section_names = []

        _final_step_id = self._get_final_step_vr(run_id)
        _final_step_number = OptimizationStep.get(OptimizationStep.id == _final_step_id).step_number
        for step in _optimization_steps:

            if step.step_number > _final_step_number:
                break

            optimization_selected_measure = OptimizationSelectedMeasure.get(
                OptimizationSelectedMeasure.id == step.optimization_selected_measure_id)
            measure_result = MeasureResult.get(MeasureResult.id == optimization_selected_measure.measure_result_id)
            measure_per_section = MeasurePerSection.get(MeasurePerSection.id == measure_result.measure_per_section_id)
            section = SectionData.get(SectionData.id == measure_per_section.section_id)
            if section.section_name not in _ordered_section_names:
                _ordered_section_names.append(section.section_name)

        return _ordered_section_names, _final_step_id

    def _get_final_step_vr(self, optimization_run_id: int) -> int:
        """Get the final step id of the optimization run.
        The final step in this case is the step with the lowest total cost.

        :param optimization_run_id: The id of the optimization run

        :return: The id of the final step
        """

        _results = []
        for _optimization_step in get_optimization_steps(optimization_run_id):
            _as_df = OptimizationStepImporter.import_optimization_step_results_df(
                _optimization_step
            )
            _cost = _optimization_step.total_lcc + _optimization_step.total_risk
            _results.append((_optimization_step, _as_df, _cost))

        _step_id, _, _ = min(_results, key=lambda results_tuple: results_tuple[2])

        return _step_id

    def import_orm(self, orm_model) -> DikeTraject:
        """Import a DikeTraject object from the ORM """
        _traject_name = orm_model.DikeTrajectInfo.get(
            orm_model.DikeTrajectInfo.traject_name == self.traject_name).traject_name
        _traject_id = DikeTrajectInfo.get(DikeTrajectInfo.traject_name == _traject_name).id
        _traject_p_lower_bound = DikeTrajectInfo.get(DikeTrajectInfo.traject_name == _traject_name).p_max
        _traject_p_signal = get_signal_value(_traject_p_lower_bound)

        _dike_traject = DikeTraject(name=_traject_name,
                                    dike_sections=[],
                                    reinforcement_order_vr=[],
                                    reinforcement_order_dsn=[],
                                    signalering_value=_traject_p_signal,
                                    lower_bound_value=_traject_p_lower_bound)

        _selected_sections = orm_model.SectionData.select().where(
            SectionData.dike_traject == _traject_id
        )
        _traject_gdf = self.parse_geo_dataframe(_traject_name)

        _dike_traject.reinforcement_order_dsn = self._get_reinforcement_section_order_dsn(
            run_id=self.run_id_dsn)  # TODO retrieve run_id from run name of datestamp
        _dike_traject.reinforcement_order_vr, final_greedy_step_id = self._get_reinforcement_section_order_vr(
            run_id=self.run_id_vr)

        _dike_traject.dike_sections = self._import_dike_section_list(_selected_sections, _traject_gdf,
                                                                     final_greedy_step_id=final_greedy_step_id)

        return _dike_traject
