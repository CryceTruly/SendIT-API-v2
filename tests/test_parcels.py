import json
import unittest
from app import *
import requests

from app.database.database import Database
from app.model.models import User
from tests.test_base import TestsStart


class TestsParcel(TestsStart):
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
            "api/v2/parcels",
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
            'parcel_description': 'My parcels contain a laptop,please deliver',
            'status': 'In Transit',
            'current_location': 'Mabarara Kikoni Home 13',
            'created': "Sat, 10 Nov 2018 13:46:41 GMT",
            'user_id': 1,
            'sender_email': 'sendermail@gmail.com',
            'recipient_phone': '0767876666',
            'recipient_email': 'recipient@email.com'
        }
        response = self.client.post(
            "api/v2/parcels",
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
            'parcel_description': 'My parcels contain a laptop,please deliver',
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
            "api/v2/parcels",
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
            'parcel_description': 'My parcels contain a laptop,please deliver',
            'status': 'In Transit',
            'current_location': 'Mabarara Kikoni Home 13',
            'created': "Sat, 10 Nov 2018 13:46:41 GMT",
            'sender_email': 'senderemail@g.com',
            'recipient_phone': '0767876666',
            'recipient_email': 'recipient@email.com'
        }
        response = self.client.post(
            "api/v2/parcels",
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
            "api/v2/parcels/1",
            data='',
            content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_cant_get_inexistent_parcel(self):
        response = self.client.get(
            "api/v2/parcels/b",
            data='',
            content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_can_cancel_parcel_delivery_parcel(self):
        self.testcreate_parcel()
        res = self.client.put("api/v2/parcels/1/cancel",
                              data='',
                              content_type="application/json")

        self.assertEqual(res.status_code, 400)

    def test_get_a_no_parcels_message(self):
        '''
        tests if a user gets a readable no users message when users are not there
        :return:
        '''
        response = self.client.get(
            'api/v2/parcels', content_type='application/json')
        data = json.loads(response.data.decode())
        count = data['count']
        if count == 0:
            self.assertEqual(data['msg'], 'No parcel delivery parcels posted yet')
        self.assertEqual(response.status, '200 OK')

    def test_cant_cancel_adelivered_parcel(self):
        '''
        checks if cannot cancel an parcel thats already delivered
        '''
        req = {
            "user_id": 1,
            "pickup_address": "Kigali Rwanda",
            "destination_address": "Jinja Uganda",
            "parcel_description": "parcel_description",
            "status": "started",
            "current_location": "Kigali Rwanda",
            "sender_email": "crycetruly@gmail.com",
            "recipient_phone": "07666777665",
            "recipient_email": "getaplott@gmail.com",
            "recipient_name": "name",
            "id": 11,
            "weight": 20
        }
        self.client.post(
            "api/v2/parcels",
            data=json.dumps(req),
            content_type="application/json")
        response = self.client.put(
            "api/v2/parcels/11/cancel",
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
            'parcel_description': 'My parcels contain a laptop,please deliver',
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
            'parcel_description': 'My parcels contain a laptop,please deliver',
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
            "api/v2/parcels",
            data=json.dumps(req),
            content_type="application/json")
        response = self.client.put(
            "api/v2/parcels/1/update",
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
            "api/v2/parcels/1/changedest",
            data=json.dumps(req2),
            content_type="application/json")
        self.assertEqual(response.status_code, 415)

    def test_use_an_invalid_token(self):
        """
        User with invalid token can't access
        any secure route
        """
        token = """eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Imthc3VsZTAwMDAwMDBqb3NlcEBnbWFpbC5jb20iLCJyb2xlIjoidXNlciIsImlhdCI6MTUzODY2NzU2OSwiZXhwIjoxNTQzODUxNTY5LCJzdWIiOjF9.6xtUvM3ULJWuPq2Nd8yPfBwZGfX1s7GzMXA5pZWx_OU"""
        res = self.client.get(
            '/api/v2/parcels/',
            headers=dict(Authorization='Bearer' " " + token)
        )
        data = json.loads(res.data.decode())
        self.assertTrue(data['message'], 'User not loged in')
        self.assertEqual(res.status_code, 400)

    def test_user_cant_accessTrue_route(self):
        """
        Only users who signed up with
    True role can accessTrue routes
        """
        with self.client:
            self.signup_user(
                "", "crycetruly@gmail.com", "0758939187", "password", "user")
            response = self.login_user("crycetruly", "password")
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(res['username'] == 'crycetruly')
            self.assertEqual(
                "You have succesfully logged in.", str(res['message']))
            self.assertTrue(res['access_token'])
            token = res['access_token']
            result = self.client.get(
                '/api/v2/parcels/',
                headers=dict(Authorization='Bearer' " " + token)
            )
            data = json.loads(result.data.decode())
            self.assertIn(
                'You dont have permission to access this route', str(data))
            self.assertEqual(result.status_code, 409)

    def testTrue_can_access_get_all_parcel_route(self):
        """
        OnlyTrue can get all parcels posted by all users
        """
        with self.client:
            self.signup_user(
                "crycetruly", "crycetruly@gmail.com", "0758939187", "password", True)
            response = self.login_user("crycetruly", "password")
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(res['username'] == 'crycetruly')
            self.assertEqual(
                "You have succesfully logged in.", str(res['message']))
            self.assertTrue(res['access_token'])
            token = res['access_token']
            result = self.client.get(
                '/api/v2/parcels/',
                headers=dict(Authorization='Bearer' " " + token)
            )
            data = json.loads(result.data.decode())
            self.assertIn(
                'no parcels posted yet', str(data))
            self.assertEqual(result.status_code, 404)

    def testTrue_fetch_all_parcels_submited_by_users(self):
        """
        All parcels submit by different users
        can be fetched by onlyTrue
        """
        with self.client:
            self.signup_user(
                "crycetruly", "crycetruly@gmail.com", "0758939187", "password", True)
            response = self.login_user("crycetruly", "password")
            res = json.loads(response.data.decode())
            self.assertTrue(res['access_token'])
            token = res['access_token']
            Database().insert_into_parcels("katogo", "all kind", 6000, "image.jpg")

            self.client.post(
                '/api/v2/users/parcels/',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="application/json",
                data=json.dumps({'parcel_id': 1})
            )
            id_menu = 1
            Database().get_parcel_by_value('parcels', 'parcel_id', parcel_id)

            all = Database().get_all_parcels()
            result = self.client.get(
                '/api/v2/parcels/',
                headers=dict(Authorization='Bearer' " " + token),
                data=json.dumps(str(all))
            )
            da = json.loads(result.data.decode())
            self.assertGreater(len(da), 0)
            self.assertIn('parcels', str(result.data))
            self.assertEqual(result.status_code, 200)

    def test_user_parcel_request_not_in_json(self):
        with self.client:
            self.signup_user(
                "crycetruly", "crycetruly@gmail.com", "0758939187", "password", True)
            response = self.login_user("crycetruly", "password")
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(res['username'] == 'crycetruly')
            self.assertEqual(
                "You have succesfully logged in.", str(res['message']))
            self.assertTrue(res['access_token'])
            token = res['access_token']
            result = self.client.post(
                '/api/v2/parcels/',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="text/javascript"
            )
            data = json.loads(result.data.decode())
            self.assertEqual(result.status_code, 401)
            self.assertEqual(
                data['message'], 'Content type must be application/json')

    def test_no_parcel_found_by_id(self):
        """
    True trying to get all parcel requests
        for a parcel id which does not exist
        """
        with self.client:
            self.signup_user(
                "crycetruly", "crycetruly@gmail.com", "0758939187", "password", True)
            response = self.login_user("crycetruly", "password")
            res = json.loads(response.data.decode())
            self.assertTrue(res['access_token'])
            token = res['access_token']
            Database().get_parcel_by_value('parcels', 'parcel_id', 1)

            result = self.client.get(
                '/api/v2/parcels/1',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="application/json"
            )
            data = json.loads(result.data.decode())
            self.assertEqual(result.status_code, 404)
            self.assertEqual(data['status'], 'Failed')
            self.assertTrue(data['message'] == 'No parcel by that Id')

    def testTrue_get_parcel_request_of_users_by_id(self):
        """
        tests if admin can see all the parcels and who created them
        """
        with self.client:
            self.signup_user(
                "crycetruly", "crycetruly@gmail.com", "0758939187", "password", True)
            response = self.login_user("crycetruly", "password")
            res = json.loads(response.data.decode())
            self.assertTrue(res['access_token'])
            token = res['access_token']
            Database().insert_into_parcels("katogo", "all kind", 6000, "image.jpg")

            self.client.post(
                '/api/v2/users/parcels/',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="application/json",
                data=json.dumps({'parcel_id': 1})
            )
            Database().get_parcel_by_value('parcels', 'parcel_id', 1)
            result = self.client.get(
                '/api/v2/parcels/1',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="application/json"
            )
            data = json.loads(result.data.decode())
            self.assertEqual(result.status_code, 200)
            self.assertEqual(data['BY'], True)
            self.assertIn("'parcel': 'katogo'", str(data))

    def test_user_cannot_update_parcel_status(self):
        """
        parcel status can only be updated byTrue
        """
        with self.client:
            self.signup_user(
                "crycetruly", "crycetruly@gmail.com", "0758939187", "password", False)
            response = self.login_user("crycetruly", "password")
            res = json.loads(response.data.decode())
            self.assertTrue(res['access_token'])
            token = res['access_token']
            result = self.client.put(
                '/api/v2/parcels/1',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="application/json",
                data=json.dumps({'status': 'delivered'})
            )
            data = json.loads(result.data.decode())
            self.assertEqual(result.status_code, 409)
            self.assertEqual(
                data['Failed'], 'You dont have permission to access this route')

    def test_nothing_passed_in_status_request(self):
        with self.client:
            self.signup_user(
                "crycetruly", "crycetruly@gmail.com", "0758939187", "password", True)
            response = self.login_user("crycetruly", "password")
            res = json.loads(response.data.decode())
            self.assertTrue(res['access_token'])
            token = res['access_token']
            result = self.client.put(
                '/api/v2/parcels/1',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="application/json",
                data=json.dumps({})
            )
            data = json.loads(result.data.decode())
            self.assertEqual(result.status_code, 404)
            self.assertEqual(data['message'], "empty request")

    def test_status_update_request_not_in_json_format(self):
        with self.client:
            status = {"status": "delivered"}
            self.signup_user(
                "crycetruly", "crycetruly@gmail.com", "0758939187", "password", True
            ")
            response = self.login_user("crycetruly", "password")
            res = json.loads(response.data.decode())
            self.assertTrue(res['access_token'])
            token = res['access_token']

            Database().insert_into_parcels("katogo", "all kind", 6000, "image.jpg")
            self.client.post(
                '/api/v2/users/parcels/',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="application/json",
                data=json.dumps({'parcel_id': 1})
            )
            result = self.client.put(
                '/api/v2/parcels/1',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="text",
                data=json.dumps(status)
            )
            data = json.loads(result.data.decode())
            self.assertEqual(result.status_code, 401)
            self.assertEqual(
                data['message'], 'Content type must be application/json')
            self.assertEqual(data['status'], 'Failed')

    def test_is_not_string_parcel_status_update(self):
        with self.client:
            status = {"status": True}
            self.signup_user(
                "crycetruly", "crycetruly@gmail.com", "0758939187", "password", True
            ")
            response = self.login_user("crycetruly", "password")
            res = json.loads(response.data.decode())
            self.assertTrue(res['access_token'])
            token = res['access_token']
            self.client.post(
                '/api/v2/users/parcels/',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="application/json",
                data=json.dumps({'parcel_id': 1})
            )

            result = self.client.put(
                '/api/v2/parcels/1',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="application/json",
                data=json.dumps(status)
            )
            data = json.loads(result.data.decode())
            self.assertEqual(result.status_code, 400)
            self.assertEqual(
                data['message'], 'Status must only be string')
            self.assertEqual(data['status'], 'Type Error')

    def test_status_should_not_be_empty_string(self):
        with self.client:
            status = {"status": "     "}
            self.signup_user(
                "crycetruly", "crycetruly@gmail.com", "0758939187", "password", True)
            response = self.login_user("crycetruly", "password")
            res = json.loads(response.data.decode())
            self.assertTrue(res['access_token'])
            token = res['access_token']

            Database().insert_into_parcels("katogo", "all kind", 6000, "image.jpg")
            self.client.post(
                '/api/v2/users/parcels/',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="application/json",
                data=json.dumps({'parcel_id': 1})
            )
            result = self.client.put(
                '/api/v2/parcels/1',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="application/json",
                data=json.dumps(status)
            )
            data = json.loads(result.data.decode())
            self.assertEqual(result.status_code, 401)
            self.assertEqual(
                data['message'], 'Status should not be empty or have only spaces')
            self.assertEqual(data['status'], 'Failed')

    def test_admi_sucessfully_update_parcel_status(self):
        with self.client:
            status = {"status": "delivered"}
            self.signup_user(
                "crycetruly", "crycetruly@gmail.com", "0758939187", "password", True)
            response = self.login_user("crycetruly", "password")
            res = json.loads(response.data.decode())
            self.assertTrue(res['access_token'])
            token = res['access_token']

            Database().insert_into_parcels("katogo", "all kind", 6000, "image.jpg")
            self.client.post(
                '/api/v2/users/parcels/',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="application/json",
                data=json.dumps({'parcel_id': 1})
            )
            result = self.client.put(
                '/api/v2/parcels/1',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="application/json",
                data=json.dumps(status)
            )
            data = json.loads(result.data.decode())
            self.assertEqual(result.status_code, 200)
            self.assertEqual(
                data['message'], 'parcel succcessfully Updated')
            self.assertEqual(data['status'], 'message')

    def test_invalid_parcel_status(self):
        with self.client:
            status = {"status": "Etuuse"}
            self.signup_user(
                "crycetruly", "crycetruly@gmail.com", "0758939187", "password", True)
            response = self.login_user("crycetruly", "password")
            res = json.loads(response.data.decode())
            self.assertTrue(res['access_token'])
            token = res['access_token']

            Database().insert_into_parcels("katogo", "all kind", 6000, "image.jpg")
            self.client.post(
                '/api/v2/users/parcels/',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="application/json",
                data=json.dumps({'parcel_id': 1})
            )
            result = self.client.put(
                '/api/v2/parcels/1',
                headers=dict(Authorization='Bearer' " " + token),
                content_type="application/json",
                data=json.dumps(status)
            )
            data = json.loads(result.data.decode())
            self.assertEqual(result.status_code, 200)
            self.assertEqual(
                data['message'], 'Invalid Update status name')
            self.assertEqual(data['status'], 'message')

    def signup_user(self, param, param1, param2, param3, param4):
        user = User(param, param1, param2, param3, param4)
