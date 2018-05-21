import datetime
import os
import shutil
import tempfile
import sqlite3
import pytest


from . import context
import gym.settings
import gym.database


def _to_list(query_result):
    return list(map(lambda x: x[0], query_result))


@pytest.fixture(scope="module")
def test_db_fixture():
    testdir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "testdir")
    db_path = os.path.join(testdir, "test.db")
    gym.settings.DB_PATH = db_path
    gym.database.init_db()
    yield db_path
    gym.database.close_db()
    shutil.rmtree(testdir)


def test_database_tables(test_db_fixture):

    conn = sqlite3.connect(test_db_fixture)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = _to_list(c.fetchall())
    c.close()
    conn.close()

    assert gym.settings.SESSION_TABLE in tables
    assert gym.settings.EXERCISE_TABLE in tables
    assert gym.settings.INTENSITY_TABLE in tables
    assert gym.settings.SESSION_DETAILS_TABLE in tables


def test_crud(test_db_fixture):

    # test insert and get
    gym.database.insert_exercise(name="test_exercise1", acronym="TEX1")
    gym.database.insert_exercise(name="test_exercise2", acronym="TEX2")
    gym.database.insert_exercise(name="test_exercise1", acronym="TEX3",
                                 description="Third exercise")
    res = gym.database.get_exercise()
    assert res == [(1, "test_exercise1", "TEX1", None),
                   (2, "test_exercise2", "TEX2", None),
                   (3, "test_exercise1", "TEX3", "Third exercise")]
    res = gym.database.get_exercise(name="test_exercise1")
    assert res == [(1, "test_exercise1", "TEX1", None),
                   (3, "test_exercise1", "TEX3", "Third exercise")]
    gym.database.insert_session()
    gym.database.insert_session(timestamp=datetime.datetime(2000, 1, 1))
    res = gym.database.get_session()
    assert len(res) == 2
    res = gym.database.get_session(_id=1)
    assert len(res[0]) > 0

    # test update
    gym.database.update_exercise(1, {"acronym": "TEX", "description": "test exercise"})
    res = gym.database.get_exercise()
    assert res == [(1, "test_exercise1", "TEX", "test exercise"),
               (2, "test_exercise2", "TEX2", None),
               (3, "test_exercise1", "TEX3", "Third exercise")]

    # test delete
    assert len(res) == 3
    gym.database.delete_exercise(1)
    res = gym.database.get_exercise()
    assert len(res) == 2


def test_get_table_headers(test_db_fixture):
    headers = gym.database.get_session_headers()
    assert headers == ["_id", "timestamp"]


def test_get_last_rowid(test_db_fixture):
    gym.database.insert_session()
    assert gym.database.get_last_rowid() == 3
    
