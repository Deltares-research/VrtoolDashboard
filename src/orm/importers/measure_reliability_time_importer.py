from pathlib import Path
from typing import Optional, Any, Iterator

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
    _get_section_lcc,
)
from src.orm.models import OptimizationSelectedMeasure, OptimizationStep, MeasureResult

from src.orm.orm_controller_custom import get_optimization_steps_ordered

from src.orm import models as orm


class TrajectMeasureResultsTimeImporter(OrmImporterProtocol):

    def __init__(
            self,
            vr_config: VrtoolConfig,
            measure_result_id: int,
            mechanism: str,

    ) -> None:
        self.vr_config = vr_config
        self.measure_result_id = measure_result_id
        self.mechanism = mechanism

    def import_orm(self, orm_model) -> Any:
        """
        Import the single measures and the step measures.

        :param orm_model: ORM model
        :return: DikeTraject object
        """

        _measures = self.import_measures()
        return _measures

    def import_measures(self) -> DataFrame:
        """
        Import all the (single) measures for the considered dike section.
        :return:

        Return a DataFrame with columns: beta, LCC, name, dberm, dcrest.
        """
        _measure_results = (
            MeasureResult.select()

            .where(
                MeasureResult.id == self.measure_result_id
            )
        )
        print(_measure_results, 9999)

        for measure_result in _measure_results:
            # select only the first occurence of the measure result section
            if self.mechanism == "Section":
                betas = [row.beta for row in _get_section_measure_beta(measure_result)]
            else:
                betas = [row.beta for row in _get_mechanism_measure_beta(measure_result, self.mechanism)]

        return betas


def _get_section_measure_beta(measure_result: MeasureResult) -> Iterator[orm.OptimizationStepResultSection]:
    """
    Get the section beta values for a given measure result

    :param measure_result:
    :return:


    """
    _query = (
        MeasureResultSection()
        .select()
        .where(
            MeasureResultSection.measure_result == measure_result.id,
        )
    )

    return _query


def _get_mechanism_measure_beta(measure_result: MeasureResult, mechanism: str) -> Iterator[
    orm.OptimizationStepResultMechanism]:
    """
    Get the beta values for a mechanism for a given measure result
    :param measure_result: measure result for which the betas are retrieved
    :param mechanism: string name of the mechanism
    :return:

    """
    _query = (
        MeasureResultMechanism
        .select(MeasureResultMechanism.beta)
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
            ORM_Mechanism.name == mechanism
        )

    )

    return _query
