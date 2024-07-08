from pathlib import Path
from typing import Optional

import numpy as np
from geopandas import GeoDataFrame
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.io.importers.optimization.optimization_step_importer import OptimizationStepImporter
from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.models import SectionData, MeasurePerSection

from src.constants import GreedyOPtimizationCriteria
from src.linear_objects.dike_section import DikeSection
from src.linear_objects.dike_traject import DikeTraject, get_initial_assessment_df, get_traject_prob

from src.orm.importers.dike_section_importer import DikeSectionImporter
from src.orm.importers.optimization_step_importer import _get_final_measure_betas, _get_section_lcc
from src.orm.importers.solution_importer import TrajectSolutionRunImporter
from src.orm.models import OptimizationSelectedMeasure, OptimizationStep, MeasureResult
from src.orm.models.dike_traject_info import DikeTrajectInfo

import geopandas as gpd

from src.orm.orm_controller_custom import get_optimization_steps_ordered
from src.utils.utils import get_signal_value


class DikeTrajectImporter(OrmImporterProtocol):
    vr_config: VrtoolConfig
    path_dir: Path
    traject_name: str
    run_id_vr: int
    run_id_dsn: int
    greedy_optimization_criteria: str
    greedy_criteria_year: Optional[int]
    greedy_criteria_beta: Optional[float]

    def __init__(self, vr_config: VrtoolConfig, run_id_vr: int, run_id_dsn: int, greedy_optimization_criteria: str,
                 greedy_criteria_year: Optional[int] = None, greedy_criteria_beta: Optional[float] = None) -> None:
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
        self.greedy_optimization_criteria = greedy_optimization_criteria
        self.greedy_criteria_year = greedy_criteria_year
        self.greedy_criteria_beta = greedy_criteria_beta

    def _import_dike_section_list(
            self, orm_dike_section_list: list[SectionData], traject_gdf: GeoDataFrame,
    ) -> list[DikeSection]:
        """Import the dike sections from the ORM to a list of DikeSection objects

        :param orm_dike_section_list: list of ORM SectionData objects
        :param traject_gdf: GeoDataFrame of the dike trajectory
        :param run_id: id of the optimization run for veiligheidsrendement (default 1)
        :param final_greedy_step_id: id of the final step of the greedy optimization
        """
        _ds_importer = DikeSectionImporter(traject_gdf, self.vr_config.T)

        return list(map(_ds_importer.import_orm_without_measure, orm_dike_section_list))

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
                                    greedy_steps=[],
                                    signalering_value=_traject_p_signal,
                                    lower_bound_value=_traject_p_lower_bound,
                                    _run_id_vr=self.run_id_vr,
                                    _run_id_dsn=self.run_id_dsn,
                                    )

        _selected_sections = orm_model.SectionData.select().where(
            SectionData.dike_traject == _traject_id
        )
        _traject_gdf = self.parse_geo_dataframe(_traject_name)
        _dike_traject.dike_sections = self._import_dike_section_list(_selected_sections, _traject_gdf)

        # import solution: both
        _solution_importer = TrajectSolutionRunImporter(dike_traject=_dike_traject,
                                                        run_id_vr=self.run_id_vr,
                                                        run_id_dsn=self.run_id_dsn,
                                                        greedy_optimization_criteria=self.greedy_optimization_criteria,
                                                        greedy_criteria_beta=self.greedy_criteria_beta,
                                                        greedy_criteria_year=self.greedy_criteria_year,
                                                        assessment_years=self.vr_config.T
                                                        )
        _solution_importer.import_orm()

        return _dike_traject
