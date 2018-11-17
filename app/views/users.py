from flask import jsonify, request, Blueprint

from app.model.parcel import Parcel
from app.model.user import User

PARCEL = Parcel()
USER = User()
user_print = Blueprint('user_print', __name__)
all = PARCEL.get_all_parcel()


@user_print.route('/api/v1/users', methods=['GET'])
def getall_users():
    ''''
    returns a list of all users
    '''
    if len(USER.users) == 0:
        return jsonify({"msg": "No users yet", "count": len(USER.users)}), 200
    return jsonify({"users": USER.users, "count": len(USER.users)}), 200


@user_print.route('/api/v1/users', methods=['POST'])
def create_user():
    """creates new user"""
    if not request.content_type == 'application/json':
        return jsonify({"failed": 'Content-type must be application/json'}), 401
    request_data = request.get_json()
    if not USER.is_valid_user_request(request_data):
        return jsonify({"success": False, "msg": "Bad request"}), 400
    if not USER.is_valid(request_data['email']):
        return jsonify({"success": False, "msg": "Email is badly formatted"}), 400
    if not USER.is_email_taken(request_data['email']):
        return jsonify({"success": False, "msg": "Email is already in use"}), 409
    if not USER.is_username_taken(request_data['username']):
        return jsonify({"success": False, "msg": "Username is already taken"}), 409
    if len(str(request_data['password']))<6:
         return jsonify({"success": False, "msg": "Password should be atleast 6 characters long"}), 409

    return jsonify(USER.create_new_user(request_data)), 201


@user_print.route('/api/v1/users/<int:id>/parcels')
def get_user_parcels(id):
    """
    returns parcel requests created by a user given the users id
    """
    if USER.is_user_exist(id):
        return jsonify(USER.get_user_parcels(id))


    else:
        return jsonify({"msg": 'User does not exist'}), 404
