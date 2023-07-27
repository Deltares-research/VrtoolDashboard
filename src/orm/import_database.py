from pathlib import Path
from vrtool.orm.orm_controllers import open_database

from src.orm.importers.dike_traject_importer import DikeTrajectImporter
from src.orm.orm_db import vrtool_db
from src.orm import models as orm_model
#


# TODO: custom DikeTrajectImporter for the Dashboard
# TODO: this include Importe for each new table and instanticate the classes of the Dashboard.



def get_dike_traject(traject_name: str):
    """
    Returns a dike traject with all the required section data.
    """
    _path_dir = Path(r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\Case_38_1_miniset")
    _path_database = _path_dir.joinpath("vrtool_input.db")

    open_database(_path_database)

    _dike_traject = DikeTrajectImporter(_path_dir).import_orm(orm_model)
    # vrtool_db.close()
    return _dike_traject
