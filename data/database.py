from mariadb import connect
from mariadb.connections import Connection
from credentials_reader.credentials_reader import credentials_reader


def _get_connection() -> Connection:
    credentials = credentials_reader()
    return connect(
        user=credentials['user'],
        password=credentials['password'],
        host=credentials['host'],
        port=credentials['port'],
        database=credentials['database']
    )


def read_query(sql: str, sql_params=()):
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)

        return list(cursor)


def insert_query(sql: str, sql_params=()) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)
        conn.commit()

        return cursor.lastrowid


def update_query(sql: str, sql_params=()) -> bool:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)
        conn.commit()

        return cursor.rowcount