import jwt
from flask import *

from secret_key import *

def dict_factory(cursor, row):
    """Returns items from the database
    as dictionaries rather than lists."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def token_required(func):
    def wrapper():
        try:
            token_passed = request.headers['Token']
            if request.headers['Token'] != '' and \
                    request.headers['Token'] != None:
                try:
                    data = jwt.decode(token_passed, SECRET_KEY,
                                      algorithms=['HS256'])
                    return func(data)
                except jwt.exceptions.ExpiredSignatureError:
                    return_data = {
                        "error": "1",
                        "message": "Token has expired"
                        }
                    return app.response_class(response=json.dumps(
                        return_data), mimetype='application/json'), 401
                except Exception :
                    return_data = {
                        "error": "1",
                        "message": "Invalid Token"
                    }
                    return app.response_class(response=json.dumps(
                        return_data), mimetype='application/json'), 401
            else:
                return_data = {
                    "error" : "2",
                    "message" : "Token required",
                }
                return app.response_class(response=json.dumps(
                    return_data), mimetype='application/json'), 401
        except Exception:
            return_data = {
                "error" : "3"
                }
            return app.response_class(response=json.dumps(
                return_data), mimetype='application/json'), 500

    wrapper.__name__ = func.__name__
    return wrapper