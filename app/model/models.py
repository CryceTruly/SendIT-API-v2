from flask import json
import datetime


class User:
    """ user class """

    def __init__(self, user_id, username, email, phone_number, password, is_admin):
        self.user_id = user_id
        self.username = username
        self.phone_number=phone_number,
        self.email = email
        self.password = password
        self.is_admin = is_admin
        self.joined = datetime.datetime.now()

    def __str__(self):
        return "user: {} with email {} joined: {}".format(self.user_id, self.email, self.joined)


class Parcel:
    """
    class define order entities and return order dictionary
    """

    def __init__(self, parcel_id, destination_address, pickup_address, comment_description,
                 user_id, sender_email, recipient_phone,
                 recipient_email, recipient_name, weight,quantity):
        self.parcel_id = parcel_id
        self.destination_address = destination_address
        self.pickup_address = pickup_address
        self.comment_description = comment_description
        self.user_id = user_id
        self.sender_email = sender_email
        self.status = self.status()[0]
        self.recipient_name = recipient_name
        self.quantity=quantity
        self.weight = weight
        self.current_location = pickup_address
        self.recipient_email = recipient_email
        self.recipient_phone = recipient_phone

    def parcel_json(self):
        """
        return parcel order in dictionary format
        """
        return {
            "parcel_id": self.parcel_id,
            "destination_address": self.destination_address,
            "pickup_address": self.pickup_address,
            "comment_description": self.comment_description,
            "user_id": self.user_id,
            "sender_email": self.sender_email,
            "status": self.status,
            "recipient_name": self.recipient_name,
            "weight": self.weight,
            "current_location": self.current_location,
            "recipient_email":self.recipient_email,
            "recipient_phone":self.recipient_phone


        }

    def status(self):
        """
        Generate status list for parcel orders
        """
        status = ['pickup_started','rejected', 'in_transit', 'cancelled', 'delivered']
        return status




