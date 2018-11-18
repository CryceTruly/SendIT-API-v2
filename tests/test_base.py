import unittest
import json

from app import app, helper
from app.database.database import Database as db
from app.helper import Helper


class BaseTestCase(unittest.TestCase):

    def create_app(self):
        """
        Create an instance of a class with testing
        """
        return app

    def setUp(self):
        self.client = app.test_client(self)
        with app.app_context():
            connect = db()
            connect.drop_tables()
            connect.create_tables()

    def tearDown(self):
        with app.app_context():
            connect = db()
            connect.drop_tables()
            connect.create_tables()

    def signup_user(self, username, email, telephone_number, password, is_admin):
        """
        Method to define user registration details
        """
        register = {
            "username": username,
            "email": email,
            "phone_number": telephone_number,
            "password": password,
            "is_admin": is_admin
        }
        return self.client.post(
            '/api/v1/auth/signup',
            content_type="application/json",
            data=json.dumps(register)
        )

    def login_user(self, username, password):
        """
        Method to define user login details
        """
        login = {
            "username": username,
            "password": password
        }
        return self.client.post(
            '/api/v1/auth/login',
            content_type="application/json",
            data=json.dumps(login)
        )

    def post_parcel(self, destination_address, pickup_address, comment_description, user_id, sender_email,
                    recipient_phone, recipient_email, recipient_name, weight, status, latlng, destlatlng,
                 token):
        """
        Define post attributes and route
        """
        helper = Helper()
        data = {
            "user_id": user_id,
            "pickup_address": pickup_address,
            "destination_address": destination_address,
            "comment_description": comment_description,
            "status": status,
            "current_location": pickup_address,
            "sender_email": sender_email,
            "recipient_phone": recipient_phone,
            "recipient_email": recipient_email,
            "recipient_name": recipient_name,
            "weight": weight,
            "distance": helper.get_distance(latlng, destlatlng),
            "price": helper.get_charge(weight, helper.get_distance(latlng, destlatlng))
        }
        return self.client.post(
            '/api/v2/parcels',
            headers=dict(Authorization='Bearer' " " + token),
            content_type="application/json",
            data=json.dumps(data)
        )