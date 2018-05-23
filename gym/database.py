import os
import sqlite3
from . import settings


# module vars
_db_connection = None
_db_cursor = None


def _init_db():
    global _db_connection
    global _db_cursor
    db_dir = os.path.abspath(os.path.dirname(settings.DB_PATH))
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    if not _db_connection:
        _db_connection = sqlite3.connect(settings.DB_PATH)
        _db_cursor = _db_connection.cursor()


def close_db():
    global _db_connection
    global _db_cursor
    if _db_connection:
        _db_cursor.close()
        _db_connection.close()
        _db_cursor = None
        _db_connection = None


def _execute_query(query, args=None):
    global _db_cursor
    res = None
    if args:
        _db_cursor.execute(query, args)
    else:
        _db_cursor.execute(query)
    if (query.lower().startswith("insert") or
        query.lower().startswith("delete") or
        query.lower().startswith("update")):
        _db_connection.commit()
    elif query.lower().startswith("select"):
        res = _db_cursor.fetchall()

    return res


def init_db():

    _init_db()

    _execute_query("pragma foreign_keys=ON;")

    _execute_query(
        '''
        CREATE TABLE IF NOT EXISTS {} (
            _id INTEGER PRIMARY KEY,
            name TEXT NOT NULL CHECK (name != ''),
            acronym TEXT NOT NULL UNIQUE CHECK (acronym != ''),
            description TEXT
        );
        '''.format(settings.EXERCISE_TABLE)
    )
    _execute_query(
        '''
        CREATE TABLE IF NOT EXISTS {}  (
            _id INTEGER PRIMARY KEY,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        '''.format(settings.SESSION_TABLE)
    )
    _execute_query(
        '''
        CREATE TABLE IF NOT EXISTS {}  (
            _id INTEGER PRIMARY KEY,
            level INTEGER NOT NULL UNIQUE CHECK (level > 0 AND level < 11),
            description TEXT
        );
        '''.format(settings.INTENSITY_TABLE)
    )
    _execute_query(
        '''
        CREATE TABLE IF NOT EXISTS {}  (
            _id INTEGER PRIMARY KEY,
            session_id INTEGER REFERENCES {} (_id) ON DELETE CASCADE,
            exercise_id INTEGER REFERENCES {} (_id),
            weight_kg REAL NOT NULL DEFAULT 0 CHECK (weight_kg >= 0),
            reps_total INTEGER NOT NULL CHECK (reps_total > 0),
            sets INTEGER NOT NULL CHECK (sets > 0),
            intensity INTEGER NOT NULL CHECK(intensity>=0 AND intensity<=10)
        );
        '''.format(settings.SESSION_DETAILS_TABLE,
                  settings.SESSION_TABLE,
                  settings.EXERCISE_TABLE,
                  settings.INTENSITY_TABLE)
    )


def _construct_update_query(table, _id, fields_dct={}):
    """
    Creates and returns SQL query string
        'UPDATE <table> SET <key1>=?, <key2>=?.. WHERE _id=?'
    with values list 
        [val1, val2, .., _id]

    :return: tuple
    """
    query_list = ["UPDATE {} SET".format(table)]
    args = []
    _max = len(fields_dct) - 1
    for i, (k, v) in enumerate(fields_dct.items()):
        if i < _max:
            query_list.append("{}=?,".format(k))
        else:
            query_list.append("{}=?".format(k))
        args.append(v)
    query_list.append("WHERE _id=?")
    args.append(_id)
    return " ".join(query_list), args


def _construct_insert_query(table, fields_dct={}):
    query_list = ["INSERT INTO {}".format(table)]
    args = []
    values_string = ""
    _max = len(fields_dct) - 1
    if _max > -1:
        for i, (k, v) in enumerate(fields_dct.items()):
            if i == 0:
                if i < _max:
                    query_list.append("({},".format(k))
                    values_string += "(?,"
                else:
                    query_list.append("({})".format(k))
                    values_string += "(?)"
            elif i < _max:
                query_list.append("{},".format(k))
                values_string += "?,"
            else:
                query_list.append("{})".format(k))
                values_string += "?)"
            args.append(v)
        query_list.append("VALUES {}".format(values_string))

    return " ".join(query_list), args if args else None


def _construct_select_query(table, constraint={}):
    query_list = ["SELECT * FROM {}".format(table)]
    args = []
    _max = len(constraint) - 1
    if _max > -1:
        query_list.append("WHERE")
        for i, (k, v) in enumerate(constraint.items()):
            query_list.append("{}=?".format(k))
            args.append(v)
            if i < _max:
                query_list.append("AND")
    return " ".join(query_list), args if args else None


def _construct_delete_query(table, _id):
    return "DELETE FROM {} WHERE _id=?".format(table), [_id]


def _get_headers(table):
    global _db_cursor
    _execute_query("SELECT * FROM {} LIMIT 1".format(table))
    return list(map(lambda x: x[0], _db_cursor.description))


def insert_exercise(**kwargs):
    query, args = _construct_insert_query(settings.EXERCISE_TABLE, kwargs)
    return _execute_query(query, args)


def get_exercise(**kwargs):
    query, args = _construct_select_query(settings.EXERCISE_TABLE, kwargs)
    return _execute_query(query, args)


def delete_exercise(_id):
    query, args = _construct_delete_query(settings.EXERCISE_TABLE, _id)
    return _execute_query(query, args)


def update_exercise(_id, new_vals):
    query, args = _construct_update_query(settings.EXERCISE_TABLE, _id, new_vals)
    return _execute_query(query, args)


def insert_session(**kwargs):
    if kwargs:
        query, args = _construct_insert_query(settings.SESSION_TABLE, kwargs)
        return _execute_query(query, args)
    else:
        return _execute_query("INSERT INTO {} DEFAULT VALUES".format(settings.SESSION_TABLE))


def get_session(**kwargs):
    query, args = _construct_select_query(settings.SESSION_TABLE, kwargs)
    return _execute_query(query, args)


def update_session(_id, **kwargs):
    query, args = _construct_update_query(settings.SESSION_TABLE, _id, kwargs)
    return _execute_query(query, args)


def delete_session(_id):
    query, args = _construct_delete_query(settings.SESSION_TABLE, _id)
    return _execute_query(query, args)


def insert_intensity(**kwargs):
    query, args = _construct_insert_query(settings.INTENSITY_TABLE, kwargs)
    return _execute_query(query, args)


def get_intensity(**kwargs):
    query, args = _construct_select_query(settings.INTENSITY_TABLE, kwargs)
    return _execute_query(query, args)


def update_intensity(_id, new_vals):
    query, args = _construct_update_query(settings.INTENSITY_TABLE, _id, new_vals)
    return _execute_query(query, args)


def delete_intensity(_id):
    query, args = _construct_delete_query(settings.INTENSITY_TABLE, _id)
    return _execute_query(query, args)


def insert_session_details(**kwargs):
    query, args = _construct_insert_query(settings.SESSION_DETAILS_TABLE, kwargs)
    return _execute_query(query, args)


def get_session_details(**kwargs):
    query, args = _construct_select_query(settings.SESSION_DETAILS_TABLE, kwargs)
    return _execute_query(query, args)


def update_session_details(_id, **kwargs):
    query, args = _construct_update_query(settings.SESSION_DETAILS_TABLE, _id,
                                         kwargs)
    return _execute_query(query, args)


def delete_session_details(_id):
    query, args = _construct_delete_query(settings.SESSION_DETAILS_TABLE, _id)
    return _execute_query(query, args)


def get_session_headers():
    return _get_headers(settings.SESSION_TABLE)


def get_last_rowid():
    last = _execute_query("SELECT last_insert_rowid()")
    return last[0][0]
