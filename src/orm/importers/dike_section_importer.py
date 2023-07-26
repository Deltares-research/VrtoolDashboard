from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.flood_defence_system.mechanism_reliability_collection import (
    MechanismReliabilityCollection,
)
from vrtool.flood_defence_system.section_reliability import SectionReliability
from vrtool.orm.io.importers.geometry_importer import GeometryImporter
from vrtool.orm.io.importers.mechanism_reliability_collection_importer import (
    MechanismReliabilityCollectionImporter,
)
from vrtool.orm.io.importers.orm_importer_protocol import OrmImporterProtocol
from vrtool.orm.io.importers.water_level_importer import WaterLevelImporter
from vrtool.orm.models.buildings import Buildings
from vrtool.orm.models.section_data import SectionData

from src.linear_objects.dike_section import DikeSection


class DikeSectionImporter(OrmImporterProtocol):
    input_directory: Path
    selected_mechanisms: list[str]
    computation_years: list[int]
    t_0: int
    externals: Path

    def __init__(self) -> DikeSectionImporter:
        pass

    def _get_mechanism_reliability_collection_list(
        self, section_data: SectionData
    ) -> list[MechanismReliabilityCollection]:
        _importer = MechanismReliabilityCollectionImporter(self._config)
        _mechanism_data = []
        for _mechanism_per_section in section_data.mechanisms_per_section:
            if not any(_mechanism_per_section.computation_scenarios):
                logging.error(
                    "No computation scenarios available for Section {} - Mechanism: {}".format(
                        _mechanism_per_section.section.section_name,
                        _mechanism_per_section.mechanism.name,
                    )
                )
            else:
                _mechanism_data.append(_importer.import_orm(_mechanism_per_section))
        return _mechanism_data

    def _get_mechanism_data(
        self, section_data: SectionData
    ) -> dict[str, tuple[str, str]]:
        _mechanism_data = {}
        for _mechanism_per_section in section_data.mechanisms_per_section:
            _available_cs = []
            for _cs in _mechanism_per_section.computation_scenarios:
                _available_cs.append((_cs.scenario_name, _cs.computation_type.name))
            _mechanism_data[_mechanism_per_section.mechanism.name] = _available_cs
        return _mechanism_data

    def _get_section_reliability(
        self,
        section_data: SectionData,
    ) -> SectionReliability:
        _section_reliability = SectionReliability()

        _section_reliability.load = WaterLevelImporter(gridpoints=1000).import_orm(
            section_data
        )

        _mechanism_collection = self._get_mechanism_reliability_collection_list(
            section_data
        )
        for _mechanism_data in _mechanism_collection:
            _section_reliability.failure_mechanisms.add_failure_mechanism_reliability_collection(
                _mechanism_data
            )

        return _section_reliability

    def import_orm(self, orm_model: SectionData) -> DikeSection:
        if not orm_model:
            raise ValueError(f"No valid value given for {SectionData.__name__}.")

        print('orm_model SectionData: ', orm_model, type(orm_model))
        print(orm_model.section_name)
        _dike_section = DikeSection(name=orm_model.section_name,
                                    coordinates_rd=[],
                                    in_analyse=True,
                                    )
        _dike_section.name = orm_model.section_name
        print(_dike_section.name)
        # # TODO: Not entirely sure mechanism_data is correctly set. Technically should not be needed anymore.
        # _dike_section.mechanism_data = self._get_mechanism_data(orm_model)
        # _dike_section.section_reliability = self._get_section_reliability(orm_model)
        # _dike_section.Length = orm_model.section_length

        return _dike_section
