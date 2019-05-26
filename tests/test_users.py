
from app.model.models import User
from flask import Flask
import json
from app.model.models import Parcel, User
from tests.test_base import TestsStart


class TestAuth(TestsStart):
    def signup_user(self, fullname, username, email, phone_number, password):
        """
        Method to define user registration details
        """
        exp_obj = {
            "fullname": fullname,
            "username": username,
            "email": email,
            "phone_number": phone_number,
            "password": password
        }
        return self.app.post(
            '/api/v2/auth/signup',
            content_type="application/json",
            data=json.dumps(exp_obj)
        )

    def login_user(self, email, password):
        """
        Method to define user login details
        """
        obj = {
            "email": email,
            "password": password
        }
        return self.app.post(
            '/api/v2/auth/login',
            content_type="application/json",
            data=json.dumps(obj)
        )

    def test_user_class(self):
        user = User(1, "Cryce Truly", "crycetruly",
                    "crycetruly@gmail.com", "0756778877", 'password')
        self.assertTrue(user)

    def test_details_json_format(self):
        with self.app:
            result = self.signup_user(
                "Cryce Truly", "crycetruly", "crycetruly@gmail.com", "0756778877", 'password')
            self.assertTrue(result.content_type == "application/json")

    def test_email_not_valid(self):
        """
         Test for invalid email address
         """
        register = {
            "username": "crycetruly",
            "email": "email",
            "phone_number": "0756787865",
            "password": "password",
        }
        rs = self.app.post(
            '/api/v2/auth/signup',
            content_type="application/json",
            data=json.dumps(register)
        )
        data = json.loads(rs.data.decode())
        self.assertEqual(rs.status_code, 400)

    def test_short_password(self):
        """
        Test for short password
        """
        with self.app:
            result = self.signup_user(
                "Cryce Truly", "crycetruly", "crycetruly@gmail.com", "0756778877", 'pas')
            self.assertEqual(result.status_code, 400)
            data = json.loads(result.data.decode())
            self.assertTrue(data['status'] == 'Failed')
            self.assertTrue(data['message'] ==
                            'Ensure password is atleast 6 characters')

    def test_spaces_in_username(self):
        with self.app:
            result = self.signup_user(
                "Cryce Truly", "cryce truly", "crycetruly@gmail.com", "0756778877", 'password')
            self.assertEqual(result.status_code, 400)

    def test_user_data_not_json(self):
        """
        Test Content_type not application/json for sign up request
        """
        rv = self.app.post(
            '/api/v2/auth/signup',
            content_type="text",
            data="")

        data = json.loads(rv.data.decode())
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(
            "Content-type must be json type", data['message'])

    def test_content_type_4_login_not_json(self):
        """
        Test Content_type not application/json for login request
        """
        rv = self.app.post(
            '/api/v2/auth/login',
            content_type="text")
        data = json.loads(rv.data.decode())
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(
            "Content-type must be in json", data['message'])
        self.assertEqual(
            "Bad request", data['status'])

    def test_user_already_exist(self):
        with self.app:
            self.signup_user(
                "Cryce Truly", "crycetruly", "crycetruly@gmail.com", "0756778877", 'password')
            result = self.signup_user(
                "Cryce Truly", "crycetruly", "crycetruly@gmail.com", "0756778877", 'password')
            self.assertEqual(result.status_code, 409)
            data = json.loads(result.data.decode())
            self.assertTrue(data['status'] == 'Failed')

    def test_successful_signup(self):
        with self.app:
            result = self.signup_user(
                "Cryce Trurely", "cryceddddtrruly", "crfedydydy@gmail.com", "0756778887", "pashsword")
            self.assertEqual(result.status_code, 201)

    def test_invalid_token(self):
        res = self.app.get(
            '/api/v2/parcels',
            headers=dict(Authorization='Bearer ywjjkjkjkwe'))
        data = json.loads(res.data.decode())
        self.assertEqual("please login", data['message'])
        self.assertEqual(res.status_code, 401)

    def test_missing_username_keyword(self):
        obj = {
            "email": "email@gmail.com",
            "phone_number": "0756434545",
            "password": "password",
            "is_admin": True
        }
        rs = self.app.post(
            '/api/v2/auth/signup',
            content_type="application/json",
            data=json.dumps(obj)
        )
        self.assertEqual(rs.status_code, 400)
        data = json.loads(rs.data.decode())
        self.assertEqual(data['Error'], "'username' is missing")

    def test_password_keyword_missing(self):
        login = {
            "email": "fred@gmail.com"
        }
        rv = self.app.post(
            '/api/v2/auth/login',
            content_type="application/json",
            data=json.dumps(login)
        )
        data = json.loads(rv.data.decode())
        self.assertEqual(data['status'], "Failed")
        self.assertEqual(data['message'], "email or password is invalid")
        self.assertEqual(rv.status_code, 400)

    def test_all_users_details(self):
        with self.app:
            result = self.signup_user(
                "Cryce TrulyTest", "TrulyTest", "TrulyTest@gmail.com", "0756778877", 'pasTrulyTestsword')
            self.assertEqual(result.status_code, 201)
            res = json.loads(result.data.decode())
            self.assertTrue(res['status'] == 'Success')
            user_dict = {
                "user_id": 1,
                "fullname": "Cryce TrulyTest",
                "username": "crycetruly",
                "email": "TrulyTest@gmail.com",
                "phone_number": "0756778877",
                "is_admin": False
            }
            rs = self.app.get(
                '/api/v2/users',
                content_type="application/json",
                data=json.dumps(user_dict)
            )
            data = json.loads(rs.data.decode())
            self.assertEqual(rs.status_code, 401)

    def test_empty_user_request(self):
        response = self.signup_user("", "", "", "", "")
        res = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)

    def test_empty_user_request_text(self):
        exp_obj = {

        }
        response = self.app.post(
            '/api/v2/auth/signup',
            content_type="application/json",
            data=json.dumps(exp_obj)
        )
        res = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(res['message'], 'Empty request')

    def test_short_phone_number(self):
        response = self.signup_user(
            "geosh@gmail.com", "geoshtest", "geosh@gmail.com", "076", "pppppppppppppppppp")
        res = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            res['message'], 'phone number should be atleast 10 characters long')

    def test_string_phone(self):
        response = self.signup_user("geosgmail.com", "geoshtelst", "geoslh@gmail.com", "pppppppppppppppp",
                                    "pppppppppppppppppp")
        res = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            res['message'], 'phone number should not contain letters')

    def test_username_missing(self):
        exp_obj = {
            "fullname": "Elain",
            "email": "crycetruly@email.com",
            "phone_number": "testuserbre",
            "password": "password"
        }
        response = self.app.post(
            '/api/v2/auth/signup',
            content_type="application/json",
            data=json.dumps(exp_obj)
        )
        self.assertEqual(response.status_code, 400)
        res = json.loads(response.data.decode())
        self.assertEqual(res['Error'], "'username' is missing")

    def test_parcels_get_returned(self):
        with self.app:
            res = self.login_user('admin@sendit.com', 'adminuser')
            data = json.loads(res.data.decode())
            token = data['data']['auth_token']
            expectedreq = {
                "recipient_name": "Aron Mike",
                "parcel_description": "Here are my stuff",
                "weight": 90,
                "quantity": 22,
                "pickup_address": "Mukono",
                "destination_address": "Entebbe",
                "recipient_phone_number": "0767878787",
                "recipient_email": "rme@gmail.com"
            }
            self.app.post(
                '/api/v2/parcels',
                content_type='application/json',
                headers=dict(Authorization='Bearer' " " + token),
                data=json.dumps(expectedreq))
            rs = self.app.get(
                '/api/v2/parcels',
                content_type="application/json",
                headers=dict(Authorization='Bearer' " " + token)
            )
            data = json.loads(rs.data.decode())
            self.assertIn('message', data)
