import geopy.distance
import jwt
import requests
import os

from app.auth.decorator import response_message, get_token
from app.database.database import Database


class Helper:
    def __init__(self):
        self.base_price = 3
        self.trulyKey = os.environ.get('trulysKey')
        db = Database()
        self.parcels = db.get_all_parcels()

    def get_charge(self, weight, distance,quantity):
        """
        calculates the charge
        :param weight:
        :param distance:
        :param distance
        :return:
        """
        return self.base_price + (weight * distance * quantity)

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

            return geopy.distance.distance(cords_1, cords_2).km
        except Exception as identifier:
            return 55

    def get_latlong(self, add):
        """
        calculates the latlong given an address
        :param add:
        :return:
        """
        try:
            r = requests.get(
                "https://www.mapquestapi.com/geocoding/v1/address?key=" + self.trulyKey + "&inFormat=kvp&outFormat=json&location= " + add + "&thumbMaps=false")
            data = r.json()
            results = data['results'][0]
            locations = results['locations']
            latlng = locations[0].get('latLng') 
            return latlng
        except Exception as identifier:
            # print('Network Error')
            return {"lat": -0.90629, "lng": 27.19168}

    def get_current_user_id(self):

        try:
            token = get_token()
            data = jwt.decode(token, os.environ.get('trulysKey'))
            return data['user_id']


        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.', 401
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.', 401
