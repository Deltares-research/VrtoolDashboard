from pathlib import Path

from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.orm_controllers import open_database

from src.linear_objects.dike_traject import DikeTraject
from src.orm.importers.dike_traject_importer import DikeTrajectImporter
from src.orm import models as orm_model


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
    print(vr_config, run_id_dsn, run_is_vr)
    _dike_traject = DikeTrajectImporter(vr_config=vr_config,
                                        run_id_dsn=run_id_dsn,
                                        run_id_vr=run_is_vr
                                        ).import_orm(
        orm_model)

    return _dike_traject
