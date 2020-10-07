import sqlite3
from sqlite3 import Error


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def main():
    sql_create_users_table = \
        """ CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY NOT NULL,
            salt TEXT NOT NULL,
            key TEXT NOT NULL
            ); """

    sql_create_tasks_table = \
        """ CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            creation_time TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status in
                ('new', 'planned', 'working', 'finished')),
            planned_end_time TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
            );"""

    conn = sqlite3.connect(r"anna_sqlite.db")
    if conn is not None:
        create_table(conn, sql_create_users_table)
        create_table(conn, sql_create_tasks_table)
    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()