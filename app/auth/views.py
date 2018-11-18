import jwt
import re
import datetime
from app.auth.decorator import response, response_message
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, request, jsonify
from flasgger import swag_from

from app.database.database import Database
from app.model.models import User

auth = Blueprint('auth', __name__)
db = Database()


@auth.route('/api/v2/users', methods=['GET'])
@swag_from('../doc/signup.yml')
def create_user():
    """
        User creates an account
        User sign up details are added to the data base
        """
    if request.content_type != 'application/json':
        return response_message(
            'Bad request', 'Content-type must be json type', 202)
    detail = request.get_json()
    try:
        if not detail:
            return jsonify({"Failed": "Empty request"}), 400
        username = detail['username']
        email = detail['email']
        phone_number = detail['phone_number']
        fullname = detail['fullname']
        if not fullname:
            return response_message('Missing', 'FullName is required', 400)
        password = generate_password_hash(detail['password'])

        if not username:
            return response_message('Missing', 'Username required', 400)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return response_message(
                'Error', 'Missing or wrong email format', 202)
        if not len(detail['password']) > 5:
            return response_message(
                'Failed', 'Ensure password is atleast characters', 202)
        if not isinstance(username, str):
            return response_message(
                'Type Error', 'username must all be string', 202)
        if not re.match("^[a-zA-Z0-9_.-]+$", username):
            return response_message(
                'Space Error', 'Username should not have a whitespace, better user _',
                400)
        if db.get_user_by_email('users', email):
            return response_message(
                'Failed', 'User with email ' + email + ' already eexists', 409)
        db.insert_into_user(fullname, username, email, phone_number, password)
        if detail['role']:
            db.update_role(detail['role'], email)
        return response_message(
            'Success', 'User account successfully created, you can now login', 201)
    except KeyError as e:
        return {'KeyError': str(e)}


@auth.route('/api/v2/users/auth', methods=['POST'])
@swag_from('../doc/login.yml')
def login_user():
    """
    User login if he supplies correct credentials
    token is generated and given to a user
    """
    try:
        if request.content_type != 'application/json':
            return response_message(
                'Bad request', 'Content-type must be in json', 202)
        detail = request.get_json()
        if not detail:
            return {"Failed": "Empty request"}, 400
        username = detail['username']
        password = generate_password_hash(detail['password'])
        if not username and not password:
            return response_message(
                'Failed', 'Username and password are required', 400)
        db_user = db.get_user_by_username('users', username)
        if not db_user:
            return response_message(
                'Failed', 'incorrect username', 401)
        new_user = User(
            db_user[0], db_user[1], db_user[2], db_user[3],
            db_user[4], db_user[5])
        if new_user.username == detail['username'] and check_password_hash(
                new_user.password, detail['password']):
            payload = {
                'email': new_user.email,
                'exp': datetime.datetime.utcnow() +
                       datetime.timedelta(days=0, hours=23),
                'iat': datetime.datetime.utcnow(),
                'sub': new_user.user_id,
                'role': new_user.role
            }
            token = jwt.encode(
                payload,
                'mysecret',
                algorithm='HS256'
            )
            if token:
                return response(
                    new_user.user_id, new_user.username,
                    'You have successfully logged in.',
                    token.decode('UTF-8'), 200)
        return response_message(
            'Failed', 'incorrect password', 401)
    except KeyError as e:
        return ({'KeyError': str(e)})


@auth.route('/api/v2/users', methods=['GET'])
def get_user():
    users = Database().get_users()
    user_list = []
    for user in users:
        user_dict = {
            "user_id": user[0],
            "fullname": user[1],
            "username": user[2],
            "email": user[3],
            "phone_number": user[4],
            "role": user[5]
        }
        user_list.append(user_dict)
    return ({"users": user_list}), 200
