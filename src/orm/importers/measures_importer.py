from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from geopandas import GeoDataFrame
from peewee import JOIN
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.io.importers.optimization.optimization_step_importer import OptimizationStepImporter
from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.models import SectionData, MeasurePerSection, MeasureResultSection, Measure, MeasureResultParameter

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


class TrajectMeasureResultsImporter(OrmImporterProtocol):

    def __init__(self, vr_config: VrtoolConfig, section_name: str) -> None:
        self.vr_config = vr_config
        self.section_name = section_name

    def import_orm(self, orm_model):
        """
        Import the dike traject from the ORM database

        :param orm_model: ORM model
        :return: DikeTraject object
        """


        _measure_results = (MeasureResult
        .select()
        .join(MeasurePerSection)
        .join(SectionData, JOIN.INNER, on=(SectionData.section_name == self.section_name))
        .where(
            # MeasurePerSection.measure_id.in_([measure.id for measure in _measure]),
            MeasurePerSection.section_id == SectionData.id
        ))
        list_results = []
        for measure_result in _measure_results:
            # select only the first occurence of the measure result section
            _measure_result_section = MeasureResultSection().select().where(
                MeasureResultSection.measure_result == measure_result.id).get()

            # Get measure name/ measure type
            measure = (Measure
                       .select()
                       .join(MeasurePerSection)
                       .join(MeasureResult)
                       .where(Measure.id == measure_result.measure_per_section.measure_id)
                       .get())

            params_dberm = MeasureResultParameter.select().where(
                (MeasureResultParameter.measure_result_id == measure_result.id) &
                (MeasureResultParameter.name == "DBERM")
            )
            params_dcrest = MeasureResultParameter.select().where(
                (MeasureResultParameter.measure_result_id == measure_result.id) &
                (MeasureResultParameter.name == "DCREST")
            )

            dberm = params_dberm[0].value if params_dberm.count() > 0 else None
            dcrest = params_dcrest[0].value if params_dcrest.count() > 0 else None

            list_results.append(
                {"LCC": _measure_result_section.cost, "beta": _measure_result_section.beta, "measure": measure.name,
                 "dberm": dberm, "dcrest": dcrest})

        # transform list into a dataframe:
        df = pd.DataFrame(list_results)
        print(df)

        return df
