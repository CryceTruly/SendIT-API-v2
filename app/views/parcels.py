from flask import jsonify, request, Blueprint
import psycopg2
from app.database.database import Database
from app.auth.decorator import response_message
import re

from app.helper import Helper

ap = Blueprint('parcels', __name__)
db = Database()


@ap.route("/")
def welcome():
    return response_message("ok", "Welcome to the sendit api v2", 200)


# GET parcels
@ap.route('/api/v2/parcels')
def get_parcels():
    '''
        returns a list of all order requests
    '''
    all = db.get_all_parcels()
    if all:
        parcel_list = []
        for parcel in all:
            parcel_dict = {
                "parcel_id": parcel[0],
                "user_id": parcel[1],
                "pickup_address": parcel[2],
                "destination_address": parcel[3],
                "sender_email": parcel[5],
                "recipient_email": parcel[10],
                "recipient_phone": parcel[7]
            }
            parcel_list.append(parcel_dict)
        return jsonify({"parcels": parcel_list}), 200
    return jsonify({'msg': 'No parcel delivery orders posted yet', 'count': len(all)}), 404


# GET parcels/id
@ap.route('/api/v2/parcels/<int:id>')
def get_a_parcel(id):
    """
    return order request details for a specific order
    :param id:
    :return:
    """
    if db.get_parcel_by_value('parcels', 'parcel_id', id) is None:
        return jsonify({"msg": "parcel delivery request order not found"}), 404
    results = db.get_parcel_by_value('parcels', 'parcel_id', id)
    parcel_dict = {
        "parcel_id": results[0],
        "user_id": results[1],
        "pickup_address": results[2],
        "destination_address": results[3],
        "sender_email": results[5],
        "recipient_email": results[10],
        "recipient_phone": results[7],
        "current_location": results[9],
        "recipient fullname": results[11],
        "destination latlng ": results[12],
        "pickuplatlng": results[13],
        "pickup latlong": results[14],
        "price": results[15],
        "created": results[16],
        "last_modified": results[17]

    }
    return jsonify(parcel_dict), 200


# POST parcels
@ap.route('/api/v2/parcels', methods=['POST'])
def add_parcel():
    """
    creates a new parcel order
    :return:
    """
    if not request.content_type == 'application/json':
        return jsonify({"failed": 'Content-type must be application/json'}), 415
    request_data = request.get_json()
    helper = Helper()
    try:

        if not helper.is_valid_request(request_data):
            return not_validresponse()
        if not is_valid(request_data['sender_email']):
            return jsonify({"msg": "Sender email is invalid"}), 400
        if not is_valid(request_data['recipient_email']):
            return jsonify({"msg": "Recipient email is invalid"}), 400
        if len(str(request_data['recipient_phone'])) < 10:
            return jsonify({"msg": "Recipient Phone number should be atleast 10 characters"}), 400

        if len(str(request_data['comment_description'])) < 5:
            return jsonify({"msg": "Your Parcel description should be atleast 5 characters"}), 400
        if not isinstance(request_data['comment_description'], str):
            return jsonify({"msg": "Description should be string values"}), 400
        if not isinstance(request_data['pickup_address'], str):
            return jsonify({"msg": "pickup_address should be string values"}), 400

        if not isinstance(request_data['destination_address'], str):
            return jsonify({"msg": "destination_address should be string values"}), 400
        if not isinstance(request_data['status'], str):
            return jsonify({"msg": "current status should be string values"}), 400
        if not isinstance(request_data['weight'], int):
            return jsonify({"msg": "weight should be integer values"}), 400
    except KeyError as keyerr:
        return response_message('Failed', str(keyerr) + 'is missing', 400)
    dest_lat_lng = helper.get_latlong(request_data['destination_address'])
    pickup_latlng = helper.get_latlong(request_data['pickup_address'])
    distance = helper.get_distance(pickup_latlng, dest_lat_lng)
    price = helper.get_charge(request_data['weight'], distance)

    try:

        db.insert_into_parcels(request_data['destination_address'],
                               request_data['pickup_address'],
                               request_data['comment_description'],
                               request_data['user_id'],
                               request_data['sender_email'],
                               request_data['recipient_name'],
                               request_data['recipient_email'],
                               request_data['recipient_phone'],
                               request_data['weight'],
                               pickup_latlng,
                               dest_lat_lng,
                               distance,
                               price)
    except psycopg2.IntegrityError:
        return response_message('Failed', 'Integrity Error:the user is being provided is inexistent', 403)
    return response_message('success', 'Parcel request has been created successfully', 201)


# PUT /parcels/<parcelId>/cancel
@ap.route('/api/v2/parcels/<int:id>/cancel', methods=['PUT'])
def cancel_parcel_request(id):
    '''
    cancels a specific request given its identifier
    '''
    if not 'user_id' in request.get_json():
        return jsonify({'msg': 'user_id is required'}), 400
    if db.get_parcel_by_value('parcels', 'parcel_id', id) != 1:
        return jsonify({"msg": "parcel delivery request not found"}), 404

    if db.is_order_delivered(id):
        return jsonify({"msg": "Not allowed parcel request has already been delivered"}), 403
    if not db.is_parcel_owner(id, 1):
        return jsonify({"msg": "You are not the parcel owner cannot cancel order"}), 403

    db.cancel_parcel(id)
    return jsonify(
        {"msg": "parcel request was cancelled successfully", "status": db.cancel_parcel(id).get("status"),
         "id": db.cancel_parcel(id).get("id")}), 200


@ap.route('/api/v1/parcels/<int:id>/presentLocation', methods=['PUT'])
def update_order_request(id):
    request_data = request.get_json()
    if not db.get_parcel_by_value('parcels', 'parcel_id', id):
        return jsonify({'msg': 'order not found'}), 404
    if is_should_update(request_data):
        db.change_destination('parcels', 'current_location', (request_data['current_location'], id))
        # TODO SEND AN EMAIL
        return jsonify({'msg': 'updated successfully'}), 200
    else:
        return jsonify({'msg': 'bad request object, params missing'}), 400


@ap.route('/api/v1/parcels/<int:id>/destination', methods=['PUT'])
def changedestination(id):
    '''
    changes destination address
    '''
    rdata = request.get_json()
    if not "destination_address" in rdata:
        return jsonify({'msg': 'Please add a new destination address'}), 415
    newdest = rdata['destination_address']
    if len(db.get_parcel_by_value('parcels', 'id', id)) != 1:
        return jsonify({"msg": "parcel delivery request not found"}), 404

    if not db.is_order_delivered(id):
        db.change_destination(newdest, id)
        return jsonify({'msg': 'updated successfully'}), 200
    else:
        return jsonify({'msg': 'order already delivered cant update'}), 403


def not_validresponse():
    '''
    helper to refactor similar response
    '''
    return jsonify({"error": 'Bad Request object,expected data is missing'}), 400


def is_should_update(data):
    if 'current_location' in data:
        return True
    return False


# def sendemail(email, parceltoupdate):
#     try:
#         msg = Message("My SendIT Order Delivery Update",
#                       sender="aacryce@gmail.com",
#                       recipients=[email])
#         msg.body = 'hello there'
#         mail.send(msg)
#         return jsonify({'msg': 'updated successfully'}), 200
#     except Exception as identifier:
#         return jsonify(identifier)


def is_valid(email):
    """helper for checking valid emails"""

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    return True
