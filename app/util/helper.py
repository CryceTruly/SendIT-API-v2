import geopy.distance
import jwt
import requests
import os

from app.auth.decorator import response_message, get_token
from app.database.database import Database


class Helper:
    def __init__(self):
        self.base_price = 1.5
        self.trulyKey = os.environ.get('TRULYS_KEY', '')
        self.categories = {"0-5": 1,
                           "6-30": 3,
                           "31-60": 6,
                           "70-100": 9,
                           "101-300": 12,
                           "301-499": 15,
                           "500-1000": 18,
                           "1001-5000": 25
                           }
        db = Database()
        self.parcels = db.get_all_parcels()

    def get_charge(self, weight, distance, quantity):
        """
        calculates the charge
        :param weight:
        :param distance:
        :param distance
        :return:
        """
        return self.base_price * (self.get_my_charge(weight) + distance)

    def get_values(self, start, finish):
        return self.categories[str(start) + "-" + str(finish)]

    def get_my_charge(self, weight):
        if weight > 5000:
            return self.get_values(1001, 5000)
        for category in self.categories.keys():
            start, finish = category.split('-')[0], category.split('-')[1]
            if weight in range(int(start), int(finish)):
                return self.get_values(start, finish)

    def get_distance(self, point1, point2):
        """
        calculates distance between two latlong values
        :param point1:
        :param point2:
        :return:
        """
        ls = []
        try:
            for i in point1.values():
                ls.append(i)
            cords_1 = (tuple(ls))
            ls2 = []
            for x in point2.values():
                ls2.append(x)
            cords_2 = (tuple(ls2))

            return geopy.distance.vincenty(cords_1, cords_2).km
        except Exception as identifier:
            return 55

    def get_formatted_address(self, address):
        '''

        :param add:
        :return:
        '''

        try:
            r = requests.get(
                "https://maps.googleapis.com/maps/api/geocode/json?address=" +
                address + "&key="+os.environ.get('TRULYS_KEY', ''))
            data = r.json()
            results = data['results']
            address = results[0]
            return address['formatted_address']
        except Exception as identifier:
            return None

    def get_pickup_latlong(self, add):
        """
        calculates the latlong given an address
        :param add:
        :return:
        """
        try:
            r = requests.get(
                "https://maps.googleapis.com/maps/api/geocode/json?address=" +
                add + "&key="+os.environ.get('TRULYS_KEY', ''))
            data = r.json()
            results = data['results']
            address = results[0]
            # Geometry
            geometry = address['geometry']
            return geometry['location']
        except Exception as identifier:
            return {'lat': 37.06250000000001, 'lng': -95.677068}

    def get_dest_latlong(self, add):
        """
        calculates the latlong given an address
        :param add:
        :return:
        """
        try:
            r = requests.get(
                "https://maps.googleapis.com/maps/api/geocode/json?address=" + add + "&key="+os.environ.get('TRULYS_KEY', ''))
            data = r.json()
            results = data['results']
            address = results[0]
            # Geometry
            geometry = address['geometry']
            return geometry['location']
        except Exception as identifier:
            return {'lat': 0.3475964, 'lng': 32.5825197}

    def get_current_user_id(self):

        try:
            token = get_token()
            data = jwt.decode(token, os.environ.get('TRULYS_KEY', ''))
            return data['user_id']

        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.', 401
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.', 401
