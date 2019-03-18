import os
from functools import wraps
from flask import request, jsonify, make_response
import jwt

from app.database.database import Database
from app.model.models import User




def get_token():
    token = None
    if 'Authorization' in request.headers:
        token = request.headers['Authorization']
        token = token.split(" ")[1]
    if not token:
        return make_response(jsonify({
            'status': 'failed',
            'message': 'Token is missing!'
        }), 401)

    return token


def token_required(f):
    """
    Decorator function to ensure that end points are accessed by
    only authorized users provided they have a valid token
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token()
        try:
            database = Database()
            data = jwt.decode(token, os.environ.get('TRULYSKEY', ''),)
            query = database.get_user_by_value(
                'users', 'user_id', data['user_id']
            )
            if not query:
                return {"message": "User does not exist"}, 400
            current_user = User(
                query[0], query[1], query[2], query[3], query[4], query[5])
        except jwt.ExpiredSignatureError as e:
            return response_message('Error', 'Signature expired,please login again', 401)
        except jwt.InvalidSignatureError as serr:
            return response_message('Error', 'Signature is invalid,please login again', 401)
        except jwt.DecodeError:
            return response_message('Error', 'please login', 401)

        return f(current_user, *args, **kwargs)

    return decorated


def response(id, username, message, token, status_code):
    """
    method to make http response for authorization token
    """
    return jsonify({
        "user_id": id,
        "username": username,
        "message": message,
        "auth_token": token

    }), status_code


def response_message(status, message, status_code):
    """
    method to handle response messages
    """
    return jsonify({
        "status": status,
        "message": message
    }), status_code
