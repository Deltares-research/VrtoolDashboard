from pathlib import Path

from vrtool.defaults.vrtool_config import VrtoolConfig
from vrtool.orm.orm_controllers import open_database

from src.linear_objects.dike_traject import DikeTraject
from src.orm.importers.dike_traject_importer import DikeTrajectImporter
from src.orm import models as orm_model


def get_dike_traject_from_config_ORM(vr_config: VrtoolConfig) -> DikeTraject:
    """
    Returns a DikeTraject object with all the required data from the ORM for the specified traject via a provided
    vr_config object
    """
    _path_dir = Path(vr_config.input_directory)
    _path_database = _path_dir.joinpath(vr_config.input_database_name)

    open_database(_path_database)

    _dike_traject = DikeTrajectImporter(vr_config=vr_config).import_orm(
        orm_model)

    return _dike_traject
