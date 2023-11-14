from pathlib import Path

from peewee import JOIN
from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.orm_controllers import open_database

from src.constants import conversion_dict_measure_names
from src.linear_objects.dike_traject import DikeTraject
from src.orm.importers.dike_traject_importer import DikeTrajectImporter
from src.orm import models as orm_model
from src.orm.importers.optimization_run_importer import import_optimization_runs_name


def get_dike_traject_from_config_ORM(vr_config: VrtoolConfig, run_id_dsn: int, run_is_vr: int) -> DikeTraject:
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
    _dike_traject = DikeTrajectImporter(vr_config=vr_config,
                                        run_id_dsn=run_id_dsn,
                                        run_id_vr=run_is_vr
                                        ).import_orm(orm_model)

    return _dike_traject


def get_name_optimization_runs(vr_config: VrtoolConfig) -> list[str]:
    """Returns a list of the (unique) names of the optimization runs in the database"""
    _path_dir = Path(vr_config.input_directory)
    _path_database = _path_dir.joinpath(vr_config.input_database_name)

    open_database(_path_database)

    _names = import_optimization_runs_name(orm_model)

    # remove duplicates
    return list(set(_names))


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

    _run = orm_model.OptimizationRun.select().where(
        orm_model.OptimizationRun.name == optimization_run_name,
    )

    _run_id_vr = _run[0].id
    _run_id_dsn = _run[1].id

    return _run_id_vr, _run_id_dsn


def get_measure_result_ids_per_section(vr_config: VrtoolConfig, section_name: str, selected_measure_type: str):
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

    _measure_type = orm_model.MeasureType.select().where(orm_model.MeasureType.name == _measure_type_name_orm)

    _measure = orm_model.Measure.select().where(orm_model.Measure.measure_type_id == _measure_type[0].id)

    _measure_results = (orm_model.MeasureResult
    .select()
    .join(orm_model.MeasurePerSection)
    .join(orm_model.SectionData, JOIN.INNER, on=(orm_model.SectionData.section_name == section_name))
    .where(
        orm_model.MeasurePerSection.measure_id.in_([measure.id for measure in _measure]),
        orm_model.MeasurePerSection.section_id == orm_model.SectionData.id
    ))

    return [measure_resutl.id for measure_resutl in _measure_results]
