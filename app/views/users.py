import jwt
import re
import datetime
from app.auth.decorator import response_message, token_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, request, jsonify, redirect
from flasgger import swag_from
from validate_email import validate_email
from app.database.database import Database
from app.model.models import User
from app.views.parcels import sendemail
from app.auth.decorator import get_token
from flask_cors import CORS
import os
auth = Blueprint('auth', __name__)

db = Database()
CORS(auth)


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
        username = str(request_data['username'])
        if not username.isalnum():
            return response_message('Missing',
                                    'Usernames must contain only letters and numbers', 400)
        email = request_data['email']
        fullname = request_data['fullname']
        if not fullname:
            return response_message('Missing', 'FullName is required', 400)

        phone_number = str(request_data['phone_number'])
        if len(phone_number) < 10:
            return response_message('Invalid',
                                    'phone number should be atleast 10 characters long', 400)

        if not re.match("[0-9]", phone_number):
            return response_message('Invalid',
                                    'phone number should not contain letters',
                                    400)
        if not isinstance(fullname, str) or not isinstance(username, str):
            return response_message('Invalid',
                                    'fullname and username should be of type string', 400)
        if len(str(fullname)) < 3 or len(username) < 3:
            return response_message('Invalid',
                                    'FullName and username should be atleast 3 characters long', 400)
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
        if db.get_user_by_value('users', 'username', username):
            return response_message(
                'Failed', username + ' is taken', 409)
        password = generate_password_hash(request_data['password'])
        db.insert_into_user(fullname, username, email, phone_number, password)
        redirect_url = f"{request.url_root}api/v2/auth/email_verify?token={jwt.encode({'email':email},os.environ.get('TRULYS_SECRET','TRULYS_SECRET')).decode('utf-8')}"
        email_message = {
            "subject": 'Welcome to SendIT',
            "body": 'Hello there ' + fullname +
            '\nClick this link to verify your email\n' +
            '\n '+redirect_url
        }
        send_mail(request, email, email_message)

        return response_message('Success',
                                'Please visit your email to verify your account', 201)
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
        if not db_user[7]:
            return response_message(
                'Failed', 'email is not verified,please visit your mailbox',
                401)
        new_user = User(
            db_user[0], db_user[1], db_user[2], db_user[3],
            db_user[5], db_user[7])
        passed = check_password_hash(new_user.password, password)

        if not passed:
            return response_message('Failed', 'email or password is invalid',
                                    400)
        payload = {

            'exp': datetime.datetime.utcnow() +
            datetime.timedelta(days=0, hours=23),
            'user_id': new_user.user_id,
            'email': new_user.email,
            'is_admin': new_user.is_admin
        }
        token = jwt.encode(
            payload,
            os.environ.get('TRULYS_SECRET', 'TRULYS_SECRET'),
            algorithm='HS256'
        )
        if token:
            results = db.get_user_by_value(
                'users', 'user_id', new_user.user_id)
            user_dict = {
                "user_id": results[0],
                "fullname": results[1],
                "username": results[2],
                "telephone_number": results[6],
                "is_admin": results[8],
                "joined": results[9],
                "email": results[4],
                "imageUrl": results[3]

            }
            response = {
                "data": {
                    "auth_token": token.decode('UTF-8'),
                    "user": user_dict,
                    "status": "success",
                    "message": "successfully loged in"
                }
            }
            return jsonify(response), 200
    except Exception as er:
        return response_message(
            'Failed', 'email or password is invalid', 400)


@auth.route('/api/v2/users', methods=['GET'])
@token_required
def get_users(current_user):
    if not db.is_admin(current_user.user_id):
        return response_message('unauthorized operation',
                                'Only admin users can view all users', 401)
    users = Database().get_users()
    user_list = []
    for user in users:
        user_dict = {
            "user_id": user[0],
            "fullname": user[1],
            "username": user[2],
            "telephone_number": user[6],
            "is_admin": user[8],
            "joined": user[9],
            "email": user[4],
            "imageUrl": user[3]
        }
        user_list.append(user_dict)
    return jsonify({"users": user_list}), 200


@auth.route('/api/v2/users/<int:id>/parcels', methods=['GET'])
@token_required
@swag_from('../doc/user_parcels.yml')
def get_user_parcels(current_user, id):
    if not db.is_admin(current_user.user_id):
        if current_user.user_id != id:
            return response_message('unauthorized operation',
                                    'You do not have permissions to access that', 401)
    if not db.get_user_by_value('users', 'user_id', id) is None:
        try:
            parcel_list = []
            for results in db.get_user_parcels(id):
                parcel_dict = {
                    "parcel_id": results[0],
                    "recipient": {
                        "email": results[11],
                        "fullname": results[12],
                        "phone_number": results[7]
                    },
                    "addresses": {
                        "pickup": results[3],
                        "destination": results[2],
                        "current": results[10],
                    },
                    "latLngCodinates": {
                        "pickup": results[13],
                        "destination": results[14],
                    },
                    "stats": {
                        "weight": results[9],
                        "status": results[6],
                        "price": results[16],
                        "tripDistance": results[15],
                        "quantity": results[8]
                    },
                    "created": results[18],
                    "last_modified": results[17],
                    "parcel_description": results[4]
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
        return response_message('unauthorised', 'cant access that', 401)
    if db.get_user_by_value('users', 'user_id', user_id) is None:
        return response_message('Error', 'User  does not exist', 404)
    db.update_role(user_id)
    return response_message('success', 'User is now admin', 200)


# GET user/id
@auth.route('/api/v2/users/<int:id>')
@token_required
@swag_from('../doc/get_user.yml')
def get_a_user(current_user, id):
    """
    return order request details for a specific order
    :param id:
    :return:
    """
    if db.get_user_by_value('users', 'user_id', id) is None:
        return jsonify({"message": "user does not exist"}), 404
    results = db.get_user_by_value('users', 'user_id', id)
    user_dict = {
        "user_id": results[0],
        "fullname": results[1],
        "username": results[2],
        "telephone_number": results[6],
        "is_admin": results[8],
        "joined": results[9],
        "email": results[4],
        "imageUrl": results[3]

    }
    return jsonify(user_dict), 200


@auth.route('/api/v2/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    db.invalidate_a_token(get_token())
    return response_message('success', 'you have successfully logged out', 200)


@auth.route('/api/v2/auth/email_verify', methods=['GET'])
def verify_user():
    "verifies a users email"
    try:
        user = jwt.decode(request.args.get('token'), os.environ.get(
            'TRULYS_SECRET', 'TRULYS_SECRET'))
        db.verify_user(user)
        return redirect(os.environ.get('FRONT_END_URL', ''), code=302)

    except jwt.InvalidSignatureError as identifier:
        return jsonify({"message": "verification is invalid or expired"}), 400

    except jwt.exceptions.DecodeError as e:
        return jsonify({"message": "Verification link is invalid"}), 400


@auth.route('/api/v2/auth/reset_password/', methods=['POST'])
def send_password_reset_link():
    "sends a reset email to a user"
    email = request.get_json().get("email", None)
    if not email:
        return jsonify({"message": "Please provide your email"}), 400

    user = db.get_user_by_value("users", "email", email)
    if not user:
        return jsonify({"message": "There is no account associated with that email"}), 404
    redirect_url = f"{request.url_root}api/v2/auth/password_change?token={jwt.encode({'email':email},os.environ.get('TRULYS_SECRET','TRULYS_SECRET')).decode('utf-8')}"

    email_message = {
        "subject": "Password reset",
        "body": f"Please click the link below to reset your password \n {redirect_url}"
    }
    send_mail(request, email_message, user[4])
    return response_message("success", "Please check your email for reset instructions", 200)

    try:
        user = jwt.decode(request.args.get('token'), os.environ.get(
            'TRULYS_SECRET', 'TRULYS_SECRET'))
        db.verify_user(user)
        return redirect(os.environ.get("FRONT_END_URL", 'https://senditfrontend.herokuapp.com/login')+"login?status=verified", code=302)

    except jwt.InvalidSignatureError as identifier:
        return jsonify({"message": "verification is invalid or expired"}), 400

    except jwt.exceptions.DecodeError as e:
        return jsonify({"message": "Verification link is invalid"}), 400


@auth.route("/api/v2/auth/password_change", methods=["GET"])
def change_password():
    token = request.args.get("token", "tamperedwith")
    return redirect(os.environ.get("FRONT_END_URL")+"change_password?auth_token="+token)


@auth.route("/api/v2/auth/password_change", methods=["POST"])
def comfirmchange_password():
    try:
        token = request.get_json().get("token", None)
        user = jwt.decode(token, os.environ.get(
            'TRULYS_SECRET', 'TRULYS_SECRET'))
        password = request.get_json().get("new_password", None)
        if password is None:
            return response_message("Error", "New password is required", 400)
        if len(password) < 6:
            return response_message("Error", "Password is too short", 400)
        db.change_user_password(user['email'], password)
        return response_message("success", "changed", 200)
    except jwt.DecodeError as identifier:
        return response_message("Error", "link is invalid", 400)
    except jwt.ExpiredSignatureError as e:
        return response_message(
            "Error", "Reset Link is expired,Please request a new one", 400)


def send_mail(request, email_message, email):
    sendemail(
        email,
        email_message["subject"],
        email_message["body"]
    )
