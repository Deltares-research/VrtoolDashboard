from typing import Any, Iterator


from peewee import JOIN
from vrtool.defaults.vrtool_config import VrtoolConfig

from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.models import (
    MeasureResultSection,
    MeasureResultMechanism,
    MechanismPerSection,
)
from vrtool.orm.models import Mechanism as ORM_Mechanism

from src.orm.models import MeasureResult


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
        Import the betas for the considered measure result and mechanism.

        :param orm_model: ORM model
        :return: DikeTraject object
        """

        _measures = self.import_measures()
        return _measures

    def import_measures(self) -> list[float]:
        """
        Import all the (single) measures for the considered dike section.
        :return:

        Return a list of betas for the specified measure result id and mechanism over time.
        """
        _measure_results = (
            MeasureResult.select()

            .where(
                MeasureResult.id == self.measure_result_id
            )
        )

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
