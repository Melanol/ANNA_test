import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def populate_users(conn, user):
    sql = """ INSERT INTO users (
                      username,
                      password
                  )
                  VALUES (?, ?); """
    try:
        c = conn.cursor()
        c.execute(sql, user)
    except Error as e:
        print(e)

def populate_tasks(conn, task):
    sql = """ INSERT INTO tasks (
                      username,
                      name,
                      description,
                      creation_time,
                      status,
                      planned_end_time
                  )
                  VALUES (?, ?, ?, ?, ?, ?); """
    try:
        c = conn.cursor()
        c.execute(sql, task)
    except Error as e:
        print(e)

def main():
    database = r"anna_sqlite.db"

    # create database connection
    conn = create_connection(database)

    with conn:
        user_1 = ('Van Damme', '123')
        user_2 = ('T1000', '123')
        tasks = [user_1, user_2]
        for task in tasks:
            populate_users(conn, task)

    with conn:
        task_1 = ('Van Damme', 'Wakka wakka', 'Wakka!',
                  '2019-12-12 00:01:13', 'new','2020-12-12 00:01:13')
        task_2 = ('Van Damme', 'Smells funny', 'No, seriously!',
                  '2019-12-12 00:01:13', 'new', '2020-12-12 00:01:13')
        task_3 = ('Van Damme', 'I like bunnies', 'They cute!',
            '2019-12-12 00:01:13', 'finished', '2020-12-12 00:01:13')
        task_4 = ('T1000', 'Meh', 'MEH!',
                  '2019-12-12 00:01:13', 'new', '2020-12-12 00:01:13')
        tasks = [task_1, task_2, task_3, task_4]
        for task in tasks:
            populate_tasks(conn, task)


if __name__ == '__main__':
    main()