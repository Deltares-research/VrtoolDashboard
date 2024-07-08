from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from geopandas import GeoDataFrame
from pandas import DataFrame
from peewee import JOIN, DoesNotExist
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.io.importers.optimization.optimization_step_importer import (
    OptimizationStepImporter,
)
from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.models import (
    SectionData,
    MeasurePerSection,
    MeasureResultSection,
    Measure,
    MeasureResultParameter,
    MeasureResultMechanism,
    MechanismPerSection,
)
from vrtool.orm.models import Mechanism as ORM_Mechanism

from src.constants import Mechanism

from src.orm.importers.importer_utils import _get_measure, _get_measure_cost
from src.orm.importers.optimization_step_importer import (
    _get_section_lcc, _get_measure_result_ids,
)
from src.orm.models import OptimizationSelectedMeasure, OptimizationStep, MeasureResult

from src.orm.orm_controller_custom import get_optimization_steps_ordered


class TrajectMeasureResultsImporter(OrmImporterProtocol):

    def __init__(
            self,
            vr_config: VrtoolConfig,
            section_name: str,
            mechanism: str,
            time: int,
            run_id_vr: int,
            run_id_dsn: int,
            active_mechanisms: Optional[list[str]] = None,
    ) -> None:
        self.vr_config = vr_config
        self.section_name = section_name
        self.mechanism = mechanism
        self.run_id_vr = run_id_vr
        self.run_id_dsn = run_id_dsn
        self.time = time
        self.active_mechanisms = active_mechanisms # used for section only
        self.assessment_time = vr_config.T

    def import_orm(self, orm_model) -> tuple:
        """
        Import the single measures and the step measures.

        :param orm_model: ORM model
        :return: DikeTraject object
        """

        _measures = self.import_measures()
        _steps_vr = self.import_steps(self.run_id_vr)
        _steps_dsn = self.import_steps(self.run_id_dsn)

        return _measures, _steps_vr, _steps_dsn

    def import_steps(self, run_id: int) -> list[dict]:
        """
        Import all the measure steps for the filtered Optimization run and for the filtered dike section.
        :param run_id: run_id of the OptimizationRun
        :return:
        """

        try:
            _optimization_steps = get_optimization_steps_ordered(run_id)

        except DoesNotExist:
            return []

        _previous_step_number = None
        _iterated_step_number = []

        _step_measures = []
        for _optimization_step in _optimization_steps:
            _step_number = _optimization_step.step_number

            # For combined steps sharing the same step number, skip the step if it has already been processed
            if _previous_step_number == _step_number:
                continue
            section = (
                SectionData.select()
                .join(MeasurePerSection)
                .join(MeasureResult)
                .join(OptimizationSelectedMeasure)
                .where(
                    OptimizationSelectedMeasure.id
                    == _optimization_step.optimization_selected_measure_id
                )
            ).get()

            if section.section_name != self.section_name:
                continue

            # if _optimization_step.step_number not in _iterated_step_number:
            _iterated_step_number.append(_optimization_step.step_number)

            _optimum_section_optimization_steps = (
                OptimizationStep.select()
                .join(OptimizationSelectedMeasure)
                .where(
                    (OptimizationSelectedMeasure.optimization_run == run_id)
                    & (OptimizationStep.step_number == _optimization_step.step_number)
                )
            )

            _measure = _get_measure(_optimum_section_optimization_steps, self.active_mechanisms, self.assessment_time)
            _measure["LCC"] = _get_section_lcc(_optimization_step)
            _measure["cost"] = _get_measure_cost(_optimum_section_optimization_steps)
            _measure["measure_results_ids"] = _get_measure_result_ids(_optimum_section_optimization_steps)
            _step_measures.append(_measure)
            _previous_step_number = _step_number

        return _step_measures

    def import_measures(self) -> DataFrame:
        """
        Import all the (single) measures for the considered dike section.
        :return:

        Return a DataFrame with columns: beta, LCC, name, dberm, dcrest.
        """
        _measure_results = (
            MeasureResult.select()
            .join(MeasurePerSection)
            .join(
                SectionData,
                JOIN.INNER,
                on=(SectionData.section_name == self.section_name),
            )
            .where(
                # MeasurePerSection.measure_id.in_([measure.id for measure in _measure]),
                MeasurePerSection.section_id
                == SectionData.id
            )
        )
        list_results = []

        for measure_result in _measure_results:
            # select only the first occurence of the measure result section
            if self.mechanism == "Section":
                _measure_result = (
                    MeasureResultSection()
                    .select()
                    .where(
                        MeasureResultSection.measure_result == measure_result.id,
                        MeasureResultSection.time == self.time,
                    )
                    .get()
                )
                _beta, _cost = _measure_result.beta, _measure_result.cost
            else:

                _measure_result = (
                    MeasureResultMechanism()
                    .select()
                    .join(
                        MechanismPerSection,
                        JOIN.INNER,
                        on=(
                                MeasureResultMechanism.mechanism_per_section
                                == MechanismPerSection.id
                        ),
                    )
                    .join(
                        ORM_Mechanism,
                        JOIN.INNER,
                        on=(MechanismPerSection.mechanism_id == ORM_Mechanism.id),
                    )
                    .where(
                        MeasureResultMechanism.measure_result == measure_result.id,
                        MeasureResultMechanism.time == self.time,
                        ORM_Mechanism.name == self.mechanism
                    )
                    .get()
                )

                _beta = _measure_result.beta
                _cost = (
                    MeasureResultSection()
                    .select()
                    .where(MeasureResultSection.measure_result == measure_result.id)
                    .get()
                    .cost
                )

                # raise NotImplementedError("Mechanism not implemented")

            # Get measure name/ measure type
            measure = (
                Measure.select()
                .join(MeasurePerSection)
                .join(MeasureResult)
                .where(Measure.id == measure_result.measure_per_section.measure_id)
                .get()
            )

            params_dberm = MeasureResultParameter.select().where(
                (MeasureResultParameter.measure_result_id == measure_result.id)
                & (MeasureResultParameter.name == "DBERM")
            )
            params_dcrest = MeasureResultParameter.select().where(
                (MeasureResultParameter.measure_result_id == measure_result.id)
                & (MeasureResultParameter.name == "DCREST")
            )

            dberm = params_dberm[0].value if params_dberm.count() > 0 else None
            dcrest = params_dcrest[0].value if params_dcrest.count() > 0 else None

            list_results.append(
                {
                    "LCC": _cost,
                    "beta": _beta,
                    "measure": measure.name,
                    "dberm": dberm,
                    "dcrest": dcrest,
                    "measure_result_id": measure_result.id
                }
            )

            # transform list into a dataframe:
            df = pd.DataFrame(list_results)

        return df
