from app.database.database import Database
from app.model.models import User
from flask import Flask, json
from app.model.models import Parcel,User

from tests.test_base import TestsStart

db = Database()


class TestAuth(TestsStart):
    def signup_user(self, fullname,username, email, phone_number, password):
        """
        Method to define user registration details
        """
        exp_obj = {
            "fullname":fullname,
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

    def login_user(self, username, password):
        """
        Method to define user login details
        """
        obj = {
            "username": username,
            "password": password
        }
        return self.app.post(
            '/api/v2/auth/login',
            content_type="application/json",
            data=json.dumps(obj)
        )

    def test_user_class(self):
        user = User(1, "Cryce Truly", "crycetruly","crycetruly@gmail.com", "0756778877", 'password')
        self.assertTrue(user)

    def test_details_json_format(self):
        with self.app:
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
            self.assertTrue(data['message'] == 'Ensure password is atleast 6 characters')

    def test_username_is_string(self):
        """
        Test username isstring
        """
        with self.app:
            result = self.signup_user(
                "Cryce Truly", 35566, "crycetruly@gmail.com", "0756778877", 'password')
            self.assertEqual(result.status_code, 400)
            data = json.loads(result.data.decode())
            self.assertEqual(data['status'],'Invalid')
            self.assertEqual(data['message'], 'Username should be string value')

    def test_spaces_in_username(self):
        with self.app:
            result = self.signup_user(
                "Cryce Truly", "cryce truly","crycetruly@gmail.com", "0756778877", 'password')
            self.assertEqual(result.status_code, 201)


    def test_username_not_provided(self):
        """
        Test username field left empty
        """
        with self.app:
            result = self.signup_user(
                "Cryce Truly", "","crycetruly@gmail.com", "0756778877", 'password')
            self.assertEqual(result.status_code, 400)
            data = json.loads(result.data.decode())
            self.assertEqual(data['message'] ,'Username  should be atleast 4 characters long')

    def test_user_data_not_json(self):
        """
        Test Content_type not application/json for sign up request
        """
        rv = self.app.post(
            '/api/v2/auth/signup',
            content_type="text",
            data="")
        
        data=json.loads(rv.data.decode())
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
        data=json.loads(rv.data.decode())
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(
          "Content-type must be in json", data['message'])
        self.assertEqual(
          "Bad request", data['status'])

    def test_user_already_exist(self):
        with self.app:
            self.signup_user(
                "Cryce Truly", "crycetruly","crycetruly@gmail.com", "0756778877", 'password')
            result = self.signup_user(
                "Cryce Truly", "crycetruly", "crycetruly@gmail.com", "0756778877", 'password')
            self.assertEqual(result.status_code, 409)
            data = json.loads(result.data.decode())
            self.assertTrue(data['status'] == 'Failed')

    def test_successful_login(self):
        with self.app:
            self.signup_user(
                "Cryce Truly", "crycetruly", "crycetruly@gmail.com", "0756778877", 'password')
            response = self.login_user("crycetruly", "password")
            res = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                "You have successfully logged in", str(res['message']))
        

    def test_login_credentials(self):
        with self.app:
            self.signup_user(
                 "Cryce Truly", "crycetruly", "crycetruly@gmail.com", "0756778877", 'password')
            resp = self.login_user("crycetruly", "wrongpassw")
            res = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(res['status'],'Failed')
            self.assertEqual(
                'username and password are invalid', str(res['message']))

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
        self.assertEqual("Signature is invalid,please login again", data['message'])
        self.assertEqual(res.status_code, 403)

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
        self.assertEqual(rs.status_code,400)
        data = json.loads(rs.data.decode())
        self.assertEqual(data['Error'], "'username' is missing")

    def test_password_keyword_missing(self):
        login = {
            "username": "my name"
        }
        rv = self.app.post(
            '/api/v2/auth/login',
            content_type="application/json",
            data=json.dumps(login)
        )
        data = json.loads(rv.data.decode())
        self.assertEqual(data['status'], "Failed")
        self.assertEqual(data['message'], "username and password are invalid")
        self.assertEqual(rv.status_code,400)

    def test_all_users_details(self):
        with self.app:
            result = self.signup_user(
                "Cryce TrulyTest", "TrulyTest", "TrulyTest@gmail.com", "0756778877", 'pasTrulyTestsword')
            self.assertEqual(result.status_code, 201)
            res = json.loads(result.data.decode())
            self.assertTrue(res['status'] == 'Success')


            users = Database().get_users()
            user_dict = {
                "user_id": 1,
                "fullname":"Cryce TrulyTest",
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

    def test_desc_not_string(self):
        """
        description and meal should be of string data type
        """
        self.signup_user(
                "Greg Fred","fred", "fred@gmail.com", "0756432356", "12389894")
        response = self.login_user("fred", "12389894")
        res = json.loads(response.data.decode())
        self.assertTrue(res['auth_token'])
        token = res['auth_token']
        ord = {
           	"recipient_name": "Aron Mike",
            "parcel_description": 11111111111111,
            "weight":90,
            "quantity": 22,
            "pickup_address":"Mukono",
            "destination_address":"Entebbe",
            "recipient_phone_number":"0767878787",
            "recipient_email":"rme@gmail.com"
        }
        rs = self.app.post(
            '/api/v2/parcels',
            content_type="application/json",
            headers=dict(Authorization='Bearer' " " + token),
            data=json.dumps(ord)
            )
        self.assertEqual(rs.status_code, 400)
        data = json.loads(rs.data.decode())
        self.assertTrue(data['message'] == 'Description should be string values')
    def test_empty_request(self):
        """
        description and meal should be of string data type
        """
        self.signup_user(
                "Greg Fred","fred", "fred@gmail.com", "0756432356", "12389894")
        response = self.login_user("fred", "12389894")
        res = json.loads(response.data.decode())
        self.assertTrue(res['auth_token'])
        token = res['auth_token']
        ord = {
           	
        }
        rs = self.app.post(
            '/api/v2/parcels',
            content_type="application/json",
            headers=dict(Authorization='Bearer' " " + token),
            data=json.dumps(ord)
            )
        self.assertEqual(rs.status_code, 400)
        data = json.loads(rs.data.decode())
        self.assertTrue(data['status'] == 'Failed')


    def test_recipient_email_invalid(self):
        """
        description and meal should be of string data type
        """
        self.signup_user(
                "Greg Fred","fred", "fred@gmail.com", "0756432356", "12389894")
        response = self.login_user("fred", "12389894")
        res = json.loads(response.data.decode())
        self.assertTrue(res['auth_token'])
        token = res['auth_token']
        ord = {
           	"recipient_name": "Aron Mike",
            "parcel_description": 11111111111111,
            "weight":90,
            "quantity": 22,
            "pickup_address":"Mukono",
            "destination_address":"Entebbe",
            "recipient_phone_number":"0767878787",
            "recipient_email":"rmegmail.com"
        }
        rs = self.app.post(
            '/api/v2/parcels',
            content_type="application/json",
            headers=dict(Authorization='Bearer' " " + token),
            data=json.dumps(ord)
            )
        self.assertEqual(rs.status_code, 400)
        data = json.loads(rs.data.decode())
        self.assertTrue(data['message'] == 'Recipient email is invalid')


    def test_cannot_accessallparcels(self):
        """
       a normal user shd not view all parcels
        """
        self.signup_user(
                "Greg Fred","fred", "fred@gmail.com", "0756432356", "12389894")
        response = self.login_user("fred", "12389894")
        res = json.loads(response.data.decode())
        self.assertTrue(res['auth_token'])
        token = res['auth_token']
        rs = self.app.get(
            '/api/v2/parcels',
            content_type="application/json",
            headers=dict(Authorization='Bearer' " " + token),
            data=""
            )
        self.assertEqual(rs.status_code, 403)
        data = json.loads(rs.data.decode())
        self.assertTrue(data['message'] == 'Only admin users can view all orders')
        self.assertTrue(data['status'] == 'Forbidden operation')

    def test_should_notview_other_parcels(self):
        """
       a normal user shd not view all parcels
        """
        self.signup_user(
                "Greg Fred","fred", "fred@gmail.com", "0756432356", "12389894")
        response = self.login_user("fred", "12389894")
        res = json.loads(response.data.decode())
        self.assertTrue(res['auth_token'])
        token = res['auth_token']
        ord = {
                "recipient_name": "Aron Mike",
                "parcel_description": "Hello there,deliver stuff",
                "weight":90,
                "quantity": 22,
                "pickup_address":"Mukono",
                "destination_address":"Entebbe",
                "recipient_phone_number":"0767878787",
                "recipient_email":"rmse@gmail.com"
            }
        rs = self.app.post(
            '/api/v2/parcels',
            content_type="application/json",
            headers=dict(Authorization='Bearer' " " + token),
            data=json.dumps(ord)
            )

        self.assertEqual(rs.status_code,403)
        nrs=self.app.get(
            '/api/v2/users/1/parcels',
            content_type="application/json",
            headers=dict(Authorization='Bearer' " " + token),
            data=json.dumps(ord)
            )
        self.assertEqual(nrs.status_code,200)
