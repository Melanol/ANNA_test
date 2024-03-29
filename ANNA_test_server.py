import os
import datetime
import hashlib
import sqlite3

from utilities import *


app = Flask(__name__)
app.config["DEBUG"] = True

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'Result': 'Resource not found'}), 404

@app.route('/api/v1/register', methods=['GET', 'POST'])
def register():
    """Query parameters: username, password"""
    query_parameters = request.args
    username = query_parameters.get('username')
    password = query_parameters.get('password')

    # https://nitratine.net/blog/post/how-to-hash-passwords-in-python/.
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt,
                              100000)

    query = """ INSERT INTO users (username, salt, key)
                VALUES (?, ?, ?); """
    values = [username, salt, key]
    conn = sqlite3.connect('anna_sqlite.db')
    cur = conn.cursor()
    try:
        cur.execute(query, values)
    except sqlite3.Error:
        return jsonify({'Result': 'SQL Error'})
    conn.commit()
    conn.close()
    time_limit = datetime.datetime.utcnow() \
                 + datetime.timedelta(days=30)
    payload = {"username": username, "exp": time_limit}
    token = jwt.encode(payload, SECRET_KEY)
    response = make_response(jsonify({'Result': 'Success'}))
    response.headers['Token'] = token
    return response

@app.route('/api/v1/login', methods=['GET', 'POST'])
def login():
    """Called when a token has expired or the user has logged off.
    Headers: username, password"""
    query_headers = request.headers
    username = query_headers.get('username')
    password = query_headers.get('password')
    query = " SELECT * FROM users WHERE username = ? "
    values = [username]
    conn = sqlite3.connect('anna_sqlite.db')
    cur = conn.cursor()
    try:
        sql_returned = cur.execute(query, values).fetchall()
    except sqlite3.Error:
        return jsonify({'Result': 'SQL Error'})
    if not sql_returned:
        return jsonify({'Result': 'User not found'})
    salt, key = sql_returned[0][1], sql_returned[0][2]
    new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                              salt, 100000)
    if new_key != key:
        return jsonify({'Result': 'Wrong password'})
    # User found, passwords match. Returning token.
    time_limit = datetime.datetime.utcnow() \
                 + datetime.timedelta(days=30)
    payload = {"username": username, "exp": time_limit}
    token = jwt.encode(payload, SECRET_KEY)
    response = make_response(jsonify({'Result': 'Success'}))
    response.headers['Token'] = token
    return response

@app.route('/api/v1/resources/tasks/all', methods=['GET'])
@token_required
def tasks_all(data):
    """No query parameters required."""
    username = data['username']
    conn = sqlite3.connect('anna_sqlite.db')
    conn.row_factory = dict_factory
    if data['username'] != username:
        return jsonify({'Result': 'Wrong user'})
    cur = conn.cursor()
    query = " SELECT * FROM tasks WHERE username=? "
    values = [username]
    sql_returned = cur.execute(query, values).fetchall()
    response = make_response(jsonify(sql_returned))
    return response

@app.route('/api/v1/resources/tasks', methods=['GET'])
@token_required
def filter(data):
    """Query parameters: [name, description, creation_time, status,
    planned_end_time]."""
    username = data['username']
    if data['username'] != username:
        return jsonify({'Result': 'Wrong user'})
    query_parameters = request.args
    id = query_parameters.get('id')
    name = query_parameters.get('name')
    description = query_parameters.get('description')
    creation_time = query_parameters.get('creation_time')
    status = query_parameters.get('status')
    planned_end_time = query_parameters.get('planned_end_time')

    query = "SELECT * FROM tasks WHERE"
    to_filter = []
    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if name:
        query += ' name=? AND'
        to_filter.append(name)
    if description:
        query += ' description=? AND'
        to_filter.append(description)
    if creation_time:
        query += ' creation_time=? AND'
        to_filter.append(creation_time)
    if status:
        query += ' status=? AND'
        to_filter.append(status)
    if planned_end_time:
        query += ' planned_end_time=? AND'
        to_filter.append(planned_end_time)
    if not (id or name or description or creation_time or status or
            planned_end_time):
        return page_not_found(404)

    query = query[:-4]

    conn = sqlite3.connect('anna_sqlite.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()
    conn.close()

    return jsonify(results)

@app.route('/api/v1/resources/tasks/create',
           methods=['GET', 'POST'])
@token_required
def create_task(data):
    """Query parameters: name, description, creation_time, status[,
    planned_end_time]."""
    username = data['username']
    query_parameters = request.args
    name = query_parameters.get('name')
    description = query_parameters.get('description')
    creation_time = query_parameters.get('creation_time')
    status = query_parameters.get('status')
    planned_end_time = query_parameters.get('planned_end_time')

    if planned_end_time:
        values = [username, name, description, creation_time, status,
                  planned_end_time]
        query = """INSERT INTO tasks (
                          username,
                          name,
                          description,
                          creation_time,
                          status,
                          planned_end_time
                      )
                      VALUES (?, ?, ?, ?, ?, ?);"""
    else:
        values = [username, name, description, creation_time, status]
        query = """INSERT INTO tasks (
                          username,
                          name,
                          description,
                          creation_time,
                          status
                      )
                      VALUES (?, ?, ?, ?, ?);"""

    conn = sqlite3.connect('anna_sqlite.db')
    cur = conn.cursor()
    try:
        cur.execute(query, values)
    except sqlite3.Error:
        return jsonify({'Result': 'SQL Error'})
    conn.commit()
    id = cur.lastrowid
    conn.close()
    response = make_response(jsonify({'Result': 'Success'}))
    response.headers['ID'] = id
    return response

@app.route('/api/v1/resources/tasks/edit', methods=['GET', 'POST'])
@token_required
def edit_task(data):
    """Query parameters: id[, new_name, description, status,
    planned_end_time]"""
    username = data['username']
    query_parameters = request.args
    if not query_parameters:
        return jsonify({'Result': 'Parameters needed.'})
    id = query_parameters.get('id')
    new_name = query_parameters.get('new_name')
    description = query_parameters.get('description')
    status = query_parameters.get('status')
    planned_end_time = query_parameters.get('planned_end_time')

    values = {'username': username, 'id': id}
    query = ' UPDATE tasks SET'
    if new_name:
        values['new_name'] = new_name
        query += ' name = :new_name,'
    if description:
        values['description'] = description
        query += ' description = :description,'
    if status:
        values['status'] = status
        query += ' status = :status,'
    if planned_end_time:
        values['planned_end_time'] = planned_end_time
        query += ' planned_end_time = :planned_end_time,'
    query = query[:-1]
    query += ' WHERE username = :username AND id = :id'

    conn = sqlite3.connect('anna_sqlite.db')
    cur = conn.cursor()
    try:
        cur.execute(query, values)
    except sqlite3.Error:
        return jsonify({'Result': 'SQL Error'})
    conn.commit()
    conn.close()
    return jsonify({'Result': 'Success'})

@app.route('/api/v1/resources/tasks/delete', methods=['GET', 'POST'])
@token_required
def delete_task(data):
    """Query parameters: id."""
    username = data['username']
    id = request.args.get('id')
    values = {'username': username, 'id': id}
    query = 'DELETE from tasks WHERE username = :username AND id = :id'
    conn = sqlite3.connect('anna_sqlite.db')
    cur = conn.cursor()
    try:
        cur.execute(query, values)
    except sqlite3.Error:
        return jsonify({'Result': 'SQL Error'})
    conn.commit()
    conn.close()
    return jsonify({'Result': 'Success'})


port = int(os.environ.get('PORT', 5000))
app.run(port=port)