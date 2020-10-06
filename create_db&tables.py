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
            username text PRIMARY KEY NOT NULL,
            password text NOT NULL
            ); """

    sql_create_tasks_table = \
        """ CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username text,
            name text NOT NULL,
            description text NOT NULL,
            creation_time text NOT NULL,
            status text NOT NULL CHECK(status in
                ('new', 'planned', 'working', 'finished')),
            planned_end_time text,
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