from pathlib import Path
from typing import Optional

from pandas import DataFrame
from peewee import JOIN
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.orm_controllers import open_database

from src.constants import (
    conversion_dict_measure_names,
    GreedyOPtimizationCriteria,
    Mechanism,
)
from src.linear_objects.dike_traject import DikeTraject
from src.orm.importers.custom_measures_importer import CustomMeasureImporter
from src.orm.importers.dike_traject_importer import DikeTrajectImporter
from src.orm import models as orm_model
from src.orm.importers.measure_reliability_time_importer import TrajectMeasureResultsTimeImporter
from src.orm.importers.measures_importer import TrajectMeasureResultsImporter
from src.orm.importers.optimization_run_importer import import_optimization_runs_name

def get_all_custom_measures(vr_config: VrtoolConfig):
    _path_dir = Path(vr_config.input_directory)
    _path_database = _path_dir.joinpath(vr_config.input_database_name)

    open_database(_path_database)
    _res = CustomMeasureImporter(
        vr_config=vr_config,


    ).import_orm(orm_model)
    return _res



def get_all_measure_results(
        vr_config: VrtoolConfig,
        section_name: str,
        mechanism: str,
        time: int,
        run_id_vr: int,
        run_id_dsn: int,
        active_mechanisms: Optional[list[str]] = None,
        final_step_number: Optional[int] = None,
) -> tuple[DataFrame, dict, dict]:
    """
    Import and return all the single measures and the steps measures of the GreedyOptimization for a given selected
    dike section and for a single selected time.

    :param vr_config: vr config from the VRCore
    :param section_name: name of the section for which the measures are filtered on
    :param mechanism: mechanism for which the measure betas will be imported.
    :param time: time for which measures are evaluated and available in the database
    :param run_id_vr: run id for the veiligheidsrendement optimization
    :param run_id_dsn: run id for the doorsnede eisen optimization
    :param active_mechanisms: list of active mechanisms for the section
    :param final_step_number: number of the final step for which the measures must be imported. If None, all steps are
        imported.
    :return:
    """
    _path_dir = Path(vr_config.input_directory)
    _path_database = _path_dir.joinpath(vr_config.input_database_name)

    open_database(_path_database)
    _meas_results, _vr_steps, _dsn_steps = TrajectMeasureResultsImporter(
        vr_config=vr_config,
        section_name=section_name,
        mechanism=mechanism,
        time=time,
        run_id_vr=run_id_vr,
        run_id_dsn=run_id_dsn,
        active_mechanisms=active_mechanisms,
        final_step_number=final_step_number,
    ).import_orm(orm_model)

    return _meas_results, _vr_steps, _dsn_steps


def get_measure_reliability_over_time(vr_config: VrtoolConfig,
                                      measure_result_id: int, mechanism: str) -> list[float]:
    """
    Return a list of betas for the specified measure result id and mechanism over time.
    :param vr_config:
    :param measure_result_id:
    :param mechanism:
    :return:
    """
    _path_dir = Path(vr_config.input_directory)
    _path_database = _path_dir.joinpath(vr_config.input_database_name)

    open_database(_path_database)
    _res = TrajectMeasureResultsTimeImporter(
        vr_config=vr_config,
        measure_result_id=measure_result_id,
        mechanism=mechanism,

    ).import_orm(orm_model)
    return _res


def get_dike_traject_from_config_ORM(
        vr_config: VrtoolConfig,
        run_id_dsn: int,
        run_is_vr: int,
        greedy_optimization_criteria: str = GreedyOPtimizationCriteria.ECONOMIC_OPTIMAL.name,
        greedy_criteria_year: Optional[int] = None,
        greedy_criteria_beta: Optional[float] = None,
) -> DikeTraject:
    """
    Returns a DikeTraject object with all the required data from the ORM for the specified traject via a provided
    vr_config object

    :param vr_config: VrtoolConfig object
    :param run_id_dsn: run id in the database for which the doorsnede eisen optimization results must be imported.
    :param run_is_vr: run id in the database for which the veiligheidsrendement optimization results must be
        imported

    :return: DikeTraject object
    """
    _path_dir = Path(vr_config.input_directory)
    _path_database = _path_dir.joinpath(vr_config.input_database_name)

    open_database(_path_database)
    _dike_traject = DikeTrajectImporter(
        vr_config=vr_config,
        run_id_dsn=run_id_dsn,
        run_id_vr=run_is_vr,
        greedy_optimization_criteria=greedy_optimization_criteria,
        greedy_criteria_year=greedy_criteria_year,
        greedy_criteria_beta=greedy_criteria_beta,
    ).import_orm(orm_model, _path_database)

    return _dike_traject


def get_name_optimization_runs(vr_config: VrtoolConfig) -> list[str]:
    """Returns a list of the (unique) names of the optimization runs in the database"""
    _path_dir = Path(vr_config.input_directory)
    _path_database = _path_dir.joinpath(vr_config.input_database_name)

    open_database(_path_database)

    _names = import_optimization_runs_name(orm_model)
    # Define substrings to remove
    _substrings_to_remove = ["Veiligheidsrendement", "Doorsnede-eisen"]

    # Remove specified substrings from each element and keep unique prefixes
    _unique_prefixes = {
        name.replace(_substrings_to_remove[0], "")
        .replace(_substrings_to_remove[1], "")
        .strip()
        for name in _names
    }

    # Remove empty strings
    _unique_prefixes = [prefix for prefix in _unique_prefixes if prefix]

    return _unique_prefixes


def get_run_optimization_ids(vr_config, optimization_run_name: str) -> tuple[int, int]:
    """Returns the run ids for the optimization run with the specified name for both the doorsnede eisen and

    veiligheidsrendement optimization runs.

    :param vr_config: VrtoolConfig object
    :param optimization_run_name: name of the optimization run for which the run ids must be returned.

    :return: tuple with the run ids for the veiligheidsrendement optimization and doorsnede eisen runs.
    """

    _path_dir = Path(vr_config.input_directory)
    _path_database = _path_dir.joinpath(vr_config.input_database_name)

    open_database(_path_database)

    _vr_run_name = optimization_run_name + " Veiligheidsrendement"
    _dsn_run_name = optimization_run_name + " Doorsnede-eisen"

    _run_id_vr = (
        orm_model.OptimizationRun.select()
        .where(
            orm_model.OptimizationRun.name == _vr_run_name,
        )[0]
        .id
    )

    _run_id_dsn = (
        orm_model.OptimizationRun.select()
        .where(
            orm_model.OptimizationRun.name == _dsn_run_name,
        )[0]
        .id
    )

    return _run_id_vr, _run_id_dsn


def get_measure_result_ids_per_section(
        vr_config: VrtoolConfig, section_name: str, selected_measure_type: str
):
    """Returns a list of measure result ids for the specified section and measure type.

    :param vr_config: VrtoolConfig object
    :param section_name: name of the section for which the measure result ids must be returned.
    :param selected_measure_type: measure type for which the measure result ids must be returned., e.g. GROUND_IMPROVEMENT

    :return: list of measure result ids
    """
    _path_dir = Path(vr_config.input_directory)
    _path_database = _path_dir.joinpath(vr_config.input_database_name)

    open_database(_path_database)

    _measure_type_name_orm = conversion_dict_measure_names[selected_measure_type]

    _measure_type = orm_model.MeasureType.select().where(
        orm_model.MeasureType.name == _measure_type_name_orm
    )

    if len(_measure_type) == 0:  # this checks if a measure type from the optimization table is indeed present in the ORM Table Measure.
        # If not, len= 0 and return empty list
        return []

    _measure = orm_model.Measure.select().where(
        orm_model.Measure.measure_type_id == _measure_type[0].id
    )

    _measure_results = (
        orm_model.MeasureResult.select()
        .join(orm_model.MeasurePerSection)
        .join(
            orm_model.SectionData,
            JOIN.INNER,
            on=(orm_model.SectionData.section_name == section_name),
        )
        .where(
            orm_model.MeasurePerSection.measure_id.in_(
                [measure.id for measure in _measure]
            ),
            orm_model.MeasurePerSection.section_id == orm_model.SectionData.id,
        )
    )

    return [measure_result.id for measure_result in _measure_results]


def get_all_default_selected_measure(_vr_config: VrtoolConfig) -> list[tuple]:
    """
    Returns a list of tuple (measure_result_id, investment_year) for all the default selected measures in the ORM, that
    is to say the measures for optimization run id = 1.
    :param _vr_config:
    :return:
    """
    _path_dir = Path(_vr_config.input_directory)
    _path_database = _path_dir.joinpath(_vr_config.input_database_name)

    open_database(_path_database)

    _selected_optimization_measure = orm_model.OptimizationSelectedMeasure.select()
    _meas_list = []
    for meas in _selected_optimization_measure:
        if meas.optimization_run_id == 1:
            _meas_list.append((meas.measure_result_id, meas.investment_year))

    return _meas_list
