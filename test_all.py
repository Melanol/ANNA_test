"""Execute with "pytest" in-console on this folder."""

import datetime
import os
import argparse
import shutil  # High level file operations.
import pytest
import requests
import jwt
import sqlite3


SECRET_KEY = "7hkBxrbZ9Td4dfwgRewV6gZSVH4q78vBia4GFGqd09SsiMghjH7"
V1_URL = 'http://127.0.0.1:5000/api/v1/'

test_user_username = 'Leonidas'
test_user_password = 'THIS IS SPARTA'
def create_test_user():
    payload = {'username': test_user_username,
               'password': test_user_password}
    r = requests.post(V1_URL+'register', params=payload)
    token = r.headers['Token']
    return token

def delete_test_user():
    conn = sqlite3.connect(r"anna_sqlite.db")
    c = conn.cursor()
    query = f""" DELETE FROM users 
                 WHERE username = '{test_user_username}' """
    c.execute(query)
    conn.commit()
    conn.close()

TIME_F = "%Y-%m-%d %H:%M:%S"
now = datetime.datetime.now()
end = now + datetime.timedelta(days=30)
test_task_name = 'Test task name 1'
test_task_description = 'Test task description 1'
test_task_status = 'new'
def create_task(token):
    payload = {'name': test_task_name,
               'description': test_task_description,
               'creation_time': now.strftime(TIME_F),
               'status': test_task_status,
               'planned_end_time': end.strftime(TIME_F)}
    headers = {'Token': token}
    r = requests.post(V1_URL+'resources/tasks/create_task',
                      params=payload, headers=headers)
    return r

def delete_task(token, id):
    payload = {'id': id}
    headers = {'Token': token}
    r = requests.post(V1_URL+'resources/tasks/delete_task',
                      params=payload, headers=headers)
    return r

class TestClass:
    # Basic tests:
    def test_404(self):
        """Get 404 from trying to access an non-existent resource."""
        r = requests.get(V1_URL+'not+found')
        assert r.json() == {'Result': 'Resource not found'}

    def test_register(self):
        """/api/v1/register. If the returned token is equal to
        the sent, usernames match. No need to test if the db received
        changes, as an SQL error would fail the test anyway."""
        token = create_test_user()
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        assert data['username'] == test_user_username
        delete_test_user()

    def test_login(self):
        """/api/v1/login."""
        create_test_user()

        payload = {'username': test_user_username,
                   'password': test_user_password}
        r = requests.post(V1_URL+'login', params=payload)
        assert r.json() == {'Result': 'Success'}
        delete_test_user()

    def test_all_n_filter(self):
        """/api/v1/resources/tasks/all,
        /api/v1/resources/tasks (filter)"""
        global test_task_name, test_task_description
        errors = []
        token = create_test_user()
        headers = {'Token': token}
        try:
            # Create 3 tasks:
            id = create_task(token).headers['ID']
            ids = [id]

            test_task_name = 'Test task name 2'
            test_task_description = 'Test task description 2'
            id = create_task(token).headers['ID']
            ids.append(id)

            test_task_name = 'Test task name 3'
            test_task_description = 'Test task description 3'
            id = create_task(token).headers['ID']
            ids.append(id)

            try:
                # Request all:
                r = requests.get(V1_URL+'resources/tasks/all',
                                 headers=headers)
                json0 = r.json()
                for i in (1, 2, 3):
                    errors.append('Test task name '+str(i) == \
                           json0[i-1]['name'])
                # Filter:
                payload = {'description': 'Test task description 3'}
                r = requests.get(V1_URL+'resources/tasks',
                                 params=payload, headers=headers)
                name = r.json()[0]['name']
                errors.append(name == 'Test task name 3')
                assert False not in errors
            finally:
                for id in ids:
                    delete_task(token, id)
        finally:
            delete_test_user()

    def test_create_n_delete_task(self):
        """/api/v1/resources/tasks/create_task,
        /api/v1/resources/tasks/delete_task."""
        token = create_test_user()
        try:
            r = create_task(token)
            id = r.headers['ID']
            r = delete_task(token, id)
            assert r.json() == {'Result': 'Success'}
        finally:
            delete_test_user()

    def test_edit_task(self):
        """/api/v1/resources/tasks/edit_task."""
        token = create_test_user()
        try:
            r = create_task(token)
            id = r.headers['ID']
            # Edit task:
            payload = {'name': 'Test task name',
                       'new_name': 'New test task name',
                       'description': 'New test task description',
                       'status': 'working',
                       'planned_end_time': end.strftime(TIME_F)}
            headers = {'Token': token}
            r = requests.post(V1_URL+'resources/tasks/edit_task',
                              params=payload, headers=headers)
            assert r.json() == {'Result': 'Success'}
        finally:
            delete_task(token, id)
            delete_test_user()

    # Advanced tests:
    def test_login_wrong_user(self):
        create_test_user()
        try:
            payload = {'username': "Wrong user",
                       'password': test_user_password}
            r = requests.post(V1_URL+'login', params=payload)
            assert r.json() == {'Result': 'User not found'}
        finally:
            delete_test_user()

    def test_login_wrong_password(self):
        create_test_user()
        try:
            payload = {'username': test_user_username,
                       'password': 'Wrong password'}
            r = requests.post(V1_URL+'login', params=payload)
            assert r.json() == {'Result': 'Wrong password'}
        finally:
            delete_test_user()