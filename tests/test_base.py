import json
import unittest

from app import app
from app.models import Parcel


class TestsStart(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_if_can_get_users(self):
        response = self.app.get('api/v1/users')
        data = json.loads(response.data.decode())
        self.assertIn('count', data)


    def test_if_can_get_parcels(self):
        response = self.app.get('api/v1/parcels')
        data = json.loads(response.data.decode())
        self.assertIn('count', data)

    def test_parcel_request_not_json(self):
        """ Test order content to be posted not in json format """
        expectedreq = {
            'pickup_address': 'Kampala Kikoni Makerere 13',
            'destination_address': 'Mabarara Kikoni Home 13',
            'comment_description': 'My parcels contain a laptop,please deliver',
            'status': 'In Transit',
            'current_location': 'Mabarara Kikoni Home 13',
            'created': "Sat, 10 Nov 2018 13:46:41 GMT",
            'recipient_address': 'Julie Muli',
            'recipient_phone': '0767876666',
            'recipient_email': 'recipient@email.com'

        }
        result = self.app.post(
            '/api/v1/parcels',
            content_type='text/html',
            data=json.dumps(expectedreq)
        )
        self.assertEqual(result.status_code, 415)
        self.assertIn('Content-type must be application/json', str(result.data))

    def test_create_user_request_not_json(self):
        """ Test order content to be posted not in json format """
        expectedreq = {
            'pickup_address': 'Kampala Kikoni Makerere 13',
            'destination_address': 'Mabarara Kikoni Home 13',
            'comment_description': 'My parcels contain a laptop,please deliver',
            'status': 'In Transit',
            'current_location': 'Mabarara Kikoni Home 13',
            'created': "Sat, 10 Nov 2018 13:46:41 GMT",
            'recipient_address': 'Julie Muli',
            'recipient_phone': '0767876666',
            'recipient_email': 'recipient@email.com'
        }
        result = self.app.post(
            '/api/v1/users',
            content_type='text/html',
            data=json.dumps(expectedreq)
        )
        self.assertEqual(result.status_code, 401)
        self.assertIn('Content-type must be application/json', str(result.data))

    def test_parcel(self):
        parcel = Parcel(1, 'startadd', 'endadd', 'myc comment', 'delivered', 'dest addree', 'now', 1, 'recipt add',
                        '075633333333'
                        , 'testuser@gmail.com')
        self.assertIn("id:1",str(parcel))









if __name__ == "__main__":
    unittest.main()
