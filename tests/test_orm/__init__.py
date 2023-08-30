from pathlib import Path

import pytest

from peewee import SqliteDatabase
from vrtool.orm.orm_controllers import open_database


@pytest.fixture(autouse=False)
def empty_db_fixture():
    _db_file = Path(__file__).parent.parent / "data/Case_38_1_miniset" / f"vrtool_input_with_sections.db"
    _db = open_database(_db_file)
    assert isinstance(_db, SqliteDatabase)

    with _db.atomic() as transaction:
        yield _db
        transaction.rollback()
    _db.close()
