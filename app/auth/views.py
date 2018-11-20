import jwt
import re
import datetime
from app.auth.decorator import response, response_message, token_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, request, jsonify
from flasgger import swag_from

from app.database.database import Database
from app.model.models import User

auth = Blueprint('auth', __name__)
db = Database()


@auth.route('/api/v2/auth/signup', methods=['POST'])
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
        fullname = detail['fullname']
        if not fullname:
            return response_message('Missing', 'FullName is required', 400)

        phone_number = str(detail['phone_number'])
        if len(phone_number) < 10:
            return response_message('Invalid', 'Phone Number should be atleast 10 characters', 400)

        if not re.match("[0-9]", phone_number):
            return response_message('Invalid', 'Phone Number should not contain letters ex.075+++++++', 400)
        if not isinstance(fullname,str):
            return response_message('Invalid', 'Fullname should be string value', 400)

        if len(str(fullname)) < 2:
               return response_message('Invalid', 'FullName should be atleaset 2 characters long', 400)

        if len(username) < 4:
            return response_message('Invalid', 'UserName  should be atleaset 4 characters long', 400)
        password = generate_password_hash(detail['password'])

        if not username:
            return response_message('Missing', 'Username required', 400)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return response_message(
                'Error', 'Missing or wrong email format', 400)
        if not len(detail['password']) > 5:
            return response_message(
                'Failed', 'Ensure password is atleast 6 characters', 400)
        if not isinstance(username, str):
            return response_message(
                'Type Error', 'username must all be string', 400)
        if not re.match("^[a-zA-Z0-9_.]+$", username):
            return response_message(
                'Space Error', 'Username should not have a whitespace',
                400)
        if db.get_user_by_value('users', 'email', email):
            return response_message(
                'Failed', 'User with email ' + email + ' already exists', 409)
        if db.get_user_by_value('users', 'username', username):
            return response_message(
                'Failed', 'User with Username ' + username + ' already exists', 409)
        db.insert_into_user(fullname, username, email, phone_number, password)
        return response_message('Success', 'User account successfully created, you can now login', 201)
    except KeyError as e:
        return jsonify({'Error': str(e) +' is missing'}),400


@auth.route('/api/v2/auth/login', methods=['POST'])
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
        password = detail['password']
        if not username and not password:
            return response_message(
                'Failed', 'Username and password are required', 400)
        db_user = db.get_user_by_value('users', 'username', username)
        if not db_user:
            return response_message(
                'Failed', 'username and password are invalid', 401)
        new_user = User(
            db_user[0], db_user[1], db_user[2], db_user[3],
            db_user[4], db_user[5])
        if not check_password_hash(new_user.password, password):
            return response_message('failed', 'username and password are invalid', 401)
        payload = {

            'exp': datetime.datetime.utcnow() +
                   datetime.timedelta(days=0, hours=23),
            'email': new_user.email,
            'user_id': new_user.user_id,
            'user_name': new_user.username,
            'is_admin': new_user.is_admin
        }
        token = jwt.encode(
            payload,
            'trulysKey',
            algorithm='HS256'
        )
        if token:
            return jsonify({"msg": "You have successfully logged in ", "auth_token ": token.decode('UTF-8')}), 200
    except KeyError as e:
        return ({'KeyError': str(e)})


@auth.route('/api/v2/users', methods=['GET'])
@token_required
def get_users(current_user):
    if not db.is_admin(current_user.user_id):
        return response_message('Fobidden operation', 'Only admin users can view all users', 403)
    users = Database().get_users()
    user_list = []
    for user in users:
        user_dict = {
            "user_id": user[0],
            "fullname": user[1],
            "username": user[2],
            "email": user[3],
            "phone_number": user[5],
            "is_admin": user[6],
            "joined": user[7]
        }
        user_list.append(user_dict)
    return jsonify({"users": user_list}), 200


@auth.route('/api/v2/users/<int:id>/parcels', methods=['GET'])
@token_required
def get_user_parcels(current_user, id):
    if not db.is_admin(current_user.user_id):
        if str(current_user.user_id) != str(id):
            return response_message('Forbidden operation', 'You do not have permissions to access that', 403)

    """
    returns parcel requests created by a user given the users id
    """
    if not db.get_user_by_value('users', 'user_id', id) is None:
        return jsonify({'user_parcels': db.get_user_parcels(id)})
    else:
        return jsonify({"msg": 'User does not exist'}), 404


@auth.route('/api/v2/auth/<int:user_id>/promote_user', methods=['PUT'])
@token_required
def promote_user(current_user, user_id):
    if db.get_user_by_value('users', 'user_id', user_id) is None:
        return response_message('Error', 'User  does not exist', 404)
    db.update_role(user_id)
    return response_message('success', 'User is now admin', 200)


@auth.route('/api/v2/auth/<int:user_id>/demote_user', methods=['PUT'])
@token_required
def demote_user(current_user, user_id):
    if db.get_user_by_value('users', 'user_id', user_id) is None:
        return response_message('Error', 'User does not exist', 404)
    db.revoke_admin_previledges(user_id)
    return response_message('success', 'User is now a regular user', 200)


@auth.route('/api/v2/auth/logout',methods=['POST'])
def logout():
    pass