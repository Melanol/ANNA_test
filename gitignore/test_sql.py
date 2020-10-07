import hashlib
import os
import sqlite3


sql_create_users_table = \
    """ CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY NOT NULL,
        salt TEXT NOT NULL,
        key TEXT NOT NULL
        ); """

conn = sqlite3.connect(r"test.db")
c = conn.cursor()
c.execute(sql_create_users_table)

# Add a user
username = 'Brent' # The users username
password = 'mypassword' # The users password

salt = os.urandom(32) # A new salt for this user
key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt,
                          100000)

sql_query = """ INSERT INTO users (username, salt, key)
                VALUES (?, ?, ?)"""
values = [username, salt, key]
c.execute(sql_query, values)
conn.commit()

# Verification attempt 1
username = 'Brent'
password = 'mypassword'

sql_query = """ SELECT * FROM users WHERE username = ? """
values = [username]
returned = c.execute(sql_query, values).fetchall()
print(returned)
salt, key = returned[0][1], returned[0][2]


new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt,
                              100000)

print(key == new_key) # The keys are not the same thus the passwords
# were not the same

sql_query = """ DELETE FROM users WHERE username = 'Brent' """
c.execute(sql_query)
conn.commit()