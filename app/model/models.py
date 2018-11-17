from flask import json
import datetime

class User:
    """ user class """
    def __init__(self, user_id, username, email, phone_number, password, role):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.joined=datetime.datetime.now()

    def __str__(self):
        return "user: {} with email {} joined: {}".format(self.user_id,self.email,self.joined)


class Parcel:
    """
    class define order entities and return order dictionary
    """
    def __init__(self,parcel_id,destination_address, pickup_address, comment_description,
                user_id, sender_email, recipient_phone,
                recipient_email, status, recipient_name, weight, current_location):
        self.parcel_id=parcel_id
        self.destination_address=destination_address
        self.pickup_address=pickup_address
        self.comment_description=comment_description
        self.user_id=user_id
        self.sender_email=sender_email
        self.status=status
        self.recipient_name=recipient_name
        self.weight=weight
        self.current_location=pickup_address




    def parcel_json(self):
        """
        return parcel order in dictionary format
        """
        return {
               "parcel_id":self.parcel_id,
               "destination_address":self.destination_address,
               "pickup_address":self.pickup_address,
               "comment_description":self.comment_description,
               "user_id": self.user_id,
               "sender_email":self.sender_email,
               "status":self.status,
               "recipient_name":self.recipient_name,
               "weight":self.weight,
               "current_location":self.current_location

            }

    def status(self):
        """
        Generate status list for orders
        """
        status = ['pickup_started', 'in_transit', 'cancelled', 'delivered']
        return status
