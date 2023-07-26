from pathlib import Path
from peewee import *
from vrtool.orm.orm_controllers import open_database

from src.orm.importers.dike_traject_importer import DikeTrajectImporter
from src.orm.orm_db import vrtool_db
from src.orm import models as orm
#
# from vrtool.orm import models as orm


# TODO: custom DikeTrajectImporter for the Dashboard
# TODO: this include Importe for each new table and instanticate the classes of the Dashboard.



def get_dike_traject(traject_name: str):
    """
    Returns a dike traject with all the required section data.
    """

    _path_database = Path(r"C:\Users\hauth\bitbucket\VRtoolDashboard\tests\data\Case_38_1_miniset\vrtool_input.db")
    open_database(_path_database)

    a = orm.SectionData
    print(a, type(a))
    b = orm.DikeTrajectInfo.get(orm.DikeTrajectInfo.traject_name == traject_name)
    # orm_model.dike_sections.select()
    print(b, type(b))
    c =  orm.ComputationScenarioResult.get(orm.ComputationScenarioResult.id == 1)
    print(c, type(c), c.id, c.year, c.beta)

    stop
    _dike_traject = DikeTrajectImporter().import_orm(
        orm.DikeTrajectInfo.get(orm.DikeTrajectInfo.traject_name == traject_name)
    )
    vrtool_db.close()
    return _dike_traject
