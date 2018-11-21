import json
import unittest
from flask import Flask
from app.model.models import Parcel, User
from app import app
from app.auth.decorator import get_token, token_required, response_message
from app.database.database import Database


class TestsStart(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        db = Database()
        db.create_tables()
    def test_if_cant_get_userswithouttoken(self):
        response = self.app.get('api/v2/users')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 401)
        self.assertEqual('please login', data['message'])

    def test_parcel(self):
        parcel = Parcel(2, "destination_address", "pickup_address", "parcel_description",
                        2, "sender_email@gmail.com", "0789888878"
                                                     "recipient@gmail.com", "name", 22, 10, 10)
        self.assertIn("id:2 senderemail:sender_email@gmail.com recieveremail:name", str(parcel))

    def test_user(self):
        user = User(11, 'crycetruly', 'crycetruly@gmail.com', '075633434432', 'password', False)
        self.assertNotEqual(str(user), 'user: 11 username:crycetruly with email crycetruly@gmail.com:isadmin:False')

    def test_db(self):
        db = Database()
        self.assertTrue(db)

    def test_db_connection(self):
        db = Database()
        self.assertTrue(db.connection)

    # def test_see_get_token(self):
    #     self.assertTrue(get_token())

if __name__ == "__main__":
    unittest.main()
