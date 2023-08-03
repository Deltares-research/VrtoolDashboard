from pathlib import Path
from vrtool.orm.orm_controllers import open_database

from src.linear_objects.dike_traject import DikeTraject
from src.orm.importers.dike_traject_importer import DikeTrajectImporter
from src.orm import models as orm_model






def get_dike_traject_from_ORM(traject_name: str) -> DikeTraject:
    """
    Returns a DikeTraject object with all the required data from the ORM for the specified traject.

    :param traject_name: The name of the traject to be imported.
    """
    _path_dir = Path(r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\Case_38_1_miniset")
    # _path_database = _path_dir.joinpath("vrtool_input.db")
    _path_database = _path_dir.joinpath("vrtool_input_with_sections.db")

    open_database(_path_database)

    _dike_traject = DikeTrajectImporter(_path_dir).import_orm(orm_model)
    # vrtool_db.close()
    return _dike_traject
