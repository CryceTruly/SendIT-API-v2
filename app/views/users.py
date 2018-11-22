import jwt
import re
import datetime
from app.auth.decorator import response, response_message, token_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from validate_email import validate_email
from app.database.database import Database
from app.model.models import User
from app.views.parcels import sendemail
import os
from app.auth.decorator import get_token

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
            'Bad request', 'Content-type must be json type', 400)
    request_data = request.get_json()
    try:
        if not request_data:
            return jsonify({"message": "Empty request"}), 400
        username = request_data['username']
        str(username).replace(" ", "")
        email = request_data['email']
        fullname = request_data['fullname']
        if not fullname:
            return response_message('Missing', 'FullName is required', 400)

        phone_number = str(request_data['phone_number'])
        if len(phone_number) < 10:
            return response_message('Invalid', 'Phone Number should be atleast 10 characters', 400)

        if not re.match("[0-9]", phone_number):
            return response_message('Invalid', 'Phone Number should not contain letters ex.075+++++++', 400)
        if not isinstance(fullname, str) or not isinstance(username, str):
            return response_message('Invalid', 'fullname and username should be of type string', 400)
        if len(str(fullname)) < 3 or len(username) < 3:
            return response_message('Invalid', 'FullName and username should be atleast 3 characters long', 400)
        if not username:
            return response_message('Missing', 'Username required', 400)
        if not validate_email(email):
            return response_message(
                'Error', 'Missing or wrong email format', 400)
        if not len(request_data['password']) > 5:
            return response_message(
                'Failed', 'Ensure password is atleast 6 characters', 400)
        if db.get_user_by_value('users', 'email', email):
            return response_message(
                'Failed', 'User with email ' + email + ' already exists', 409)
        password = generate_password_hash(request_data['password'])
        db.insert_into_user(fullname, username, email, phone_number, password)
        sendemail(
            email, 'Welcome to SendIT',
            'Hello there ' + fullname + ',\n We want to thank you for joining our platform and we love you\n'
                                        'For any inquiries,you can dm us on twitter or reply to this email\n Have fun \nThe SendIT Team'
        )

        return response_message('Success', 'User account successfully created, log in', 201)
    except KeyError as e:
        return jsonify({'Error': str(e) + ' is missing'}), 400


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
                'Bad request', 'Content-type must be in json', 400)
        request_data = request.get_json()
        if not request_data:
            return jsonify({"Failed": "Empty request"}), 400
        email = request_data['email']
        if not validate_email(email):
            return response_message(
                'Failed', 'email is invalid', 400)

        password = request_data['password']
        db_user = db.get_user_by_value('users', 'email', email)
        if not db_user:
            return response_message(
                'Failed', 'email or password is invalid', 401)
        new_user = User(
            db_user[0], db_user[1], db_user[2], db_user[3],
            db_user[4], db_user[5])
        if not check_password_hash(new_user.password, password):
            return response_message('Failed', 'email or password is invalid', 400)
        payload = {

            'exp': datetime.datetime.utcnow() +
                   datetime.timedelta(days=0, hours=23),
            'email': new_user.email,
            'user_id': new_user.user_id,
            'email': new_user.email,
            'is_admin': new_user.is_admin
        }
        token = jwt.encode(
            payload,
            os.environ.get('trulysKey'),
            algorithm='HS256'
        )
        if token:
            return jsonify({"message": "You have successfully logged in", "auth_token": token.decode('UTF-8')}), 200
    except Exception as er:
        return response_message(
            'Failed', 'email or password is invalid', 400)


@auth.route('/api/v2/users', methods=['GET'])
@token_required
def get_users(current_user):
    if not db.is_admin(current_user.user_id):
        return response_message('Forbidden operation', 'Only admin users can view all users', 401)
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
        if current_user.user_id != id:
            return response_message('unauthorized operation', 'You do not have permissions to access that', 401)

    """
    returns parcel requests created by a user given the users id
    """

    if not db.get_user_by_value('users', 'user_id', id) is None:
        try:

            parcel_list = []
            for parcel in db.get_user_parcels(id):
                parcel_dict = {
                    "parcel_id": parcel[0],
                    "user_id": parcel[1],
                    "pickup_address": parcel[3],
                    "destination_address": parcel[2],
                    "sender_email": parcel[5],
                    "recipient_email": parcel[10],
                    "recipient_phone_number": parcel[7]
                }
                parcel_list.append(parcel_dict)
            return jsonify({"parcels": parcel_list}), 200
        except IndexError as e:
            return jsonify({"message": 'User does not exist'}), 404

    else:
        return jsonify({"message": 'User does not exist'}), 404


@auth.route('/api/v2/auth/<int:user_id>/promote_user', methods=['PUT'])
@token_required
def change_user_type(current_user, user_id):

    if not db.is_admin(current_user.user_id):
        return response_message('unauthorised','cant access that',401)
    if db.get_user_by_value('users', 'user_id', user_id) is None:
        return response_message('Error', 'User  does not exist', 404)
    db.update_role(user_id)
    return response_message('success', 'User is now admin', 200)


@auth.route('/api/v2/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    db.invalidate_a_token(get_token())
    return response_message('success', 'you have successfully logged out', 200)
