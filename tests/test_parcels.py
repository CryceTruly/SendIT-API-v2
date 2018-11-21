import json
import unittest
from app import *
import requests

from app.database.database import Database
from app.model.models import User
from tests.test_base import TestsStart


class TestsParcel(TestsStart):
    def test_if_can_get_parcels(self):
        response = self.app.get('api/v2/parcels')
        data = json.loads(response.data.decode())
        self.assertEqual('please login', data['message'])

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
            '/api/v2/parcels',
            content_type='text/html',
            data=json.dumps(expectedreq)
        )
        data=json.loads(result.data.decode())
        self.assertEqual(result.status_code, 401)
        self.assertEqual("please login", data['message'])
     