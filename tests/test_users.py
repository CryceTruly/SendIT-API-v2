from app.database.database import Database
from app.model.models import User
from tests.test_base import BaseTestCase
import json

db = Database()


class TestAuth(BaseTestCase):

    def test_user_class(self):
        user = User(1, "Cryce Truly", "crycetruly","crycetruly@gmail.com", "0756778877", 'password')
        self.assertTrue(user)

    def test_details_json_format(self):
        with self.client:
            result = self.signup_user(
                "Cryce Truly", "crycetruly","crycetruly@gmail.com", "0756778877", 'password')
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
            "is_admin": False
        }
        rs = self.client.post(
            '/api/v2/auth/signup',
            content_type="application/json",
            data=json.dumps(register)
        )
        data = json.loads(rs.data.decode())
        self.assertEqual(rs.status_code, 202)
        self.assertTrue(data['status'] == 'Error')
        self.assertTrue(data['message'] == 'Missing or wrong email format')

    def test_short_password(self):
        """
        Test for short password
        """
        with self.client:
            result = self.signup_user(
                "Cryce Truly", "crycetruly", "crycetruly@gmail.com", "0756778877", 'password')
            self.assertEqual(result.status_code, 202)
            data = json.loads(result.data.decode())
            self.assertTrue(data['status'] == 'Failed')
            self.assertTrue(data['message'] == 'Ensure password is morethan 4 characters')

    def test_username_is_string(self):
        """
        Test username isstring
        """
        with self.client:
            result = self.signup_user(
                "Cryce Truly", "355", "crycetruly@gmail.com", "0756778877", 'password')
            self.assertEqual(result.status_code, 202)
            data = json.loads(result.data.decode())
            self.assertTrue(data['status'] == 'Type Error')
            self.assertTrue(data['message'] == 'username must all be string')

    def test_spaces_in_username(self):
        """
        Test username has no spaces between characters
        """
        with self.client:
            result = self.signup_user(
                "Cryce Truly", "cryce truly","crycetruly@gmail.com", "0756778877", 'password')
            self.assertEqual(result.status_code, 400)
            data = json.loads(result.data.decode())
            self.assertTrue(data['status'] == 'Space Error')
            self.assertTrue(data['message'] == 'Username should not have space, better user _')

    def test_username_not_provided(self):
        """
        Test username field left empty
        """
        with self.client:
            result = self.signup_user(
                "Cryce Truly", "","crycetruly@gmail.com", "0756778877", 'password')
            self.assertEqual(result.status_code, 400)
            data = json.loads(result.data.decode())
            self.assertTrue(data['status'] == 'Missing')
            self.assertTrue(data['message'] == 'Username required')

    def test_user_dat_not_json(self):
        """
        Test Content_type not application/json for sign up request
        """
        rv = self.client.post(
            '/api/v1/auth/signup',
            content_type="text",
            data=json.dumps(dict({'status': 'register'}))
        )
        self.assertEqual(rv.status_code, 202)
        self.assertIn(
            '"message": "Content-type must be in json"', str(rv.data))

    def test_content_type_4_login_not_json(self):
        """
        Test Content_type not application/json for login request
        """
        rv = self.client.post(
            '/api/v1/auth/login',
            content_type="text",
            data=json.dumps(dict({'status': 'register'}))
        )
        self.assertEqual(rv.status_code, 202)
        self.assertIn('"message": "Content-type must be in json"', str(rv.data))

    def test_user_already_exist(self):
        with self.client:
            self.signup_user(
                "Cryce Truly", "crycetruly","crycetruly@gmail.com", "0756778877", 'password')
            result = self.signup_user(
                "Cryce Truly", "crycetruly", "crycetruly@gmail.com", "0756778877", 'password')
            self.assertEqual(result.status_code, 409)
            data = json.loads(result.data.decode())
            self.assertTrue(data['status'] == 'Failed')

    def test_successful_login(self):
        with self.client:
            self.signup_user(
                "Cryce Truly", "crycetruly", "crycetruly@gmail.com", "0756778877", 'password')
            response = self.login_user("crycetruly", "password")
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(res['username'] == 'crycetruly')
            self.assertEqual(
                "You have succesfully logged in.", str(res['message']))
            self.assertTrue(res['auth_token'])

    def test_login_credentials(self):
        with self.client:
            self.signup_user(
                 "Cryce Truly", "crycetruly", "crycetruly@gmail.com", "0756778877", 'password')
            resp = self.login_user("crycetruly", "wrongpassw")
            res = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 401)
            self.assertTrue(res['status'] == 'Failed')
            self.assertEqual(
                'incorrect password', str(res['message']))

    def test_successful_signup(self):
        with self.client:
            result = self.signup_user(
                "Cryce Truly", "crycetruly", "crycetruly@gmail.com", "0756778877", 'password')
            self.assertEqual(result.status_code, 201)
            res = json.loads(result.data.decode())
            self.assertTrue(res['status'] == 'Success')
            self.assertEqual(
                'User account successfully created, log in',
                str(res['message']))

    def test_invalid_token(self):
        res = self.client.get(
            '/api/v2/parcels/',
            headers=dict(Authorization='Bearer ywjjkjkjkwe'))
        data = json.loads(res.data.decode())
        self.assertIn("Invalid token. Please log in again.", str(data))
        self.assertEqual(res.status_code, 401)

    def test_missing_username_keyword(self):
        register = {
            "email": "email@gmail.com",
            "location": "location",
            "password": "password",
            "is_admin": True
        }
        rs = self.client.post(
            '/api/v2/auth/signup',
            content_type="application/json",
            data=json.dumps(register)
        )
        data = json.loads(rs.data.decode())
        self.assertEqual(data['KeyError'], "'username'")

    def test_password_keyword_missing(self):
        login = {
            "username": "my name"
        }
        rv = self.client.post(
            '/api/v2/auth/login',
            content_type="application/json",
            data=json.dumps(login)
        )
        data = json.loads(rv.data.decode())
        self.assertEqual(data['KeyError'], "'password'")

    def test_all_users_details(self):
        with self.client:
            result = self.signup_user(
                "Cryce Truly", "crycetruly", "crycetruly@gmail.com", "0756778877", 'password')
            self.assertEqual(result.status_code, 201)
            res = json.loads(result.data.decode())
            self.assertTrue(res['status'] == 'Success')
            self.assertEqual(
                'User account successfully created, log in',
                str(res['message']))

            users = Database().get_users()
            user_dict = {
                "user_id": 1,
                "username": "crycetruly",
                "email": "crycetruly@gmail.com",
                "phone_number": "0756778877",
                "is_admin": False
            }
            rs = self.client.get(
                '/api/v2/users',
                content_type="application/json",
                data=json.dumps(user_dict)
            )
            data = json.loads(rs.data.decode())
            self.assertEqual(rs.status_code, 200)
            self.assertIn("'phone_number': '0756778877'", str(data['users']))




