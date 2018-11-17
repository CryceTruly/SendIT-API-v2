import json
import unittest
from app import *
import requests

class TestsParcel(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client(self)

    def test_welcome(self):
        '''
        checks if the app is up and running
        '''
        response = self.client.get(
            "/",
            content_type="application/json")
        # we should get this on successful creation
        self.assertEqual(response.status_code, 200)

    def test_create_parcel_with_only_pickup_address(self):
        """
        checks if a parcel request cant be created without any data
        """
        expectedreq = {

        }
        response = self.client.post(
            "api/v1/parcels",
            data=json.dumps(expectedreq),
            content_type="application/json")
        # we should get this on successful creation
        self.assertEqual(response.status_code, 400)

    def test_cannot_create_parcel_with_no_weight(self):
        """
        checks if a parcel request can be created
        """
        expectedreq = {
            'pickup_address': 'Kampala Kikoni Makerere 13',
            'destination_address': 'Mabarara Kikoni Home 13',
            'comment_description': 'My parcels contain a laptop,please deliver',
            'status': 'In Transit',
            'current_location': 'Mabarara Kikoni Home 13',
            'created': "Sat, 10 Nov 2018 13:46:41 GMT",
            'user_id': 1,
            'sender_email': 'sendermail@gmail.com',
            'recipient_phone': '0767876666',
            'recipient_email': 'recipient@email.com'
        }
        response = self.client.post(
            "api/v1/parcels",
            data=json.dumps(expectedreq),
            content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def testcreate_parcel(self):
        """
        checks if a parcel request can be created
        """
        expectedreq = {
            'pickup_address': 'Kampala Kikoni Makerere 13',
            'destination_address': 'Mabarara Kikoni Home 13',
            'comment_description': 'My parcels contain a laptop,please deliver',
            'status': 'In Transit',
            'current_location': 'Mabarara Kikoni Home 13',
            'created': "Sat, 10 Nov 2018 13:46:41 GMT",
            'user_id': 1,
            'sender_email': 'sender@email.com',
            'recipient_phone': '0767876666',
            'recipient_email': 'recipient@email.com',
            'recipient_name': 'name',
            'weight': 200
        }
        response = self.client.post(
            "api/v1/parcels",
            data=json.dumps(expectedreq),
            content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_cannot_create_parcel_that_has_no_owner(self):
        """
        checks if a parcel request can not be created without a user
        """
        expectedreq = {
            'pickup_address': 'Kampala Kikoni Makerere 13',
            'destination_address': 'Mabarara Kikoni Home 13',
            'comment_description': 'My parcels contain a laptop,please deliver',
            'status': 'In Transit',
            'current_location': 'Mabarara Kikoni Home 13',
            'created': "Sat, 10 Nov 2018 13:46:41 GMT",
            'sender_email': 'senderemail@g.com',
            'recipient_phone': '0767876666',
            'recipient_email': 'recipient@email.com'
        }
        response = self.client.post(
            "api/v1/parcels",
            data=json.dumps(expectedreq),
            content_type="application/json")
        # we should get this on successful creation
        self.assertEqual(response.status_code, 400)

    def test_can_get_parcel(self):
        """
        checks if a single parcel can be returned given its id
        """
        self.testcreate_parcel()
        response = self.client.get(
            "api/v1/parcels/1",
            data='',
            content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_cant_get_inexistent_parcel(self):
        response = self.client.get(
            "api/v1/parcels/b",
            data='',
            content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_can_cancel_parcel_delivery_order(self):
        self.testcreate_parcel()
        res = self.client.put("api/v1/parcels/1/cancel",
                              data='',
                              content_type="application/json")

        self.assertEqual(res.status_code, 400)
    def test_get_a_no_parcels_message(self):
        '''
        tests if a user gets a readable no users message when users are not there
        :return:
        '''
        response = self.client.get(
            'api/v1/parcels', content_type='application/json')
        data = json.loads(response.data.decode())
        count = data['count']
        if count == 0:
            self.assertEqual(data['msg'], 'No parcel delivery orders posted yet')
        self.assertEqual(response.status, '200 OK')

    def test_cant_cancel_adelivered_order(self):
        '''
        checks if cannot cancel an order thats already delivered
        '''
        req = {
            "user_id":1,
            "pickup_address":"Kigali Rwanda",
            "destination_address":"Jinja Uganda",
            "comment_description":"comment_description",
            "status":"started",
            "current_location":"Kigali Rwanda",
            "sender_email":"crycetruly@gmail.com",
            "recipient_phone":"07666777665",
            "recipient_email":"getaplott@gmail.com",
            "recipient_name":"name",
            "id":11,
            "weight":20
        }
        self.client.post(
            "api/v1/parcels",
            data=json.dumps(req),
            content_type="application/json")
        response = self.client.put(
            "api/v1/parcels/11/cancel",
            data='',
            content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_can_update_location(self):
        '''
        test if user can change dest
        '''
        req = {
            'id': 1,
            'pickup_address': 'Kampala Kikoni Makerere 13',
            'destination_address': 'Mabarara Kikoni Home 13',
            'comment_description': 'My parcels contain a laptop,please deliver',
            'status': 'delivered',
            'current_location': 'Mabarara Kikoni Home 13',
            'created': "Sat, 10 Nov 2018 13:46:41 GMT",
            'user_id': 1,
            'recipient_address': 'Julie Muli',
            'recipient_phone': '0767876666',
            'recipient_email': 'recipient@email.com',
            'recipient_name': 'recipient',
            'weight': 21

        }
        req2 = {
            'id': 1,
            'pickup_address': 'Kampala Kikoni Makerere 13',
            'destination_address': 'Mubende Kikoni Home 13',
            'comment_description': 'My parcels contain a laptop,please deliver',
            'status': 'in transit',
            'current_location': 'Mabarara Kikoni Home 13',
            'created': "Sat, 10 Nov 2018 13:46:41 GMT",
            'user_id': 1,
            'recipient_address': 'Julie Muli',
            'recipient_phone': '0767876666',
            'recipient_email': 'recipient@email.com',
            'recipient_name': 'recipient',
            'weight': 21

        }
        self.client.post(
            "api/v1/parcels",
            data=json.dumps(req),
            content_type="application/json")
        response = self.client.put(
            "api/v1/parcels/1/update",
            data=json.dumps(req2),
            content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_can_change_dest(self):
        self.testcreate_parcel()
       

        req2 = {
                'destination': 'Mubende Kikoni Home 13',
                'status': 'delivered',
               
            }
        response = self.client.put(
            "api/v1/parcels/1/changedest",
            data=json.dumps(req2),
            content_type="application/json")
        self.assertEqual(response.status_code, 415)
        
    