import geopy.distance
import requests
import os

from app.auth.decorator import response_message
from app.database.database import Database


class Helper:
    def __init__(self):
        self.base_price = 2
        self.trulyKey = os.environ.get('trulysKey')
        db = Database()
        self.parcels = db.get_all_parcels()

    def is_valid_request(self, request_data):
        """
        checks if valid request parameters are sent by the user

        :param request_data:
        :return boolen:
        """
        keys = ["destination_address", "pickup_address", "comment_description",
                "user_id", "sender_email", "recipient_phone",
                "recipient_email", "status", "recipient_name", "weight", "current_location"]
        try:

            if set(request_data).issubset(keys):
                return True
            return False
        except KeyError as keyerr:
            return response_message('Failed', str(keyerr) + 'is missing', 400)

    def is_order_delivered(self, id):
        """
         checks that we cannot cancel an already delivered order
        :param id:
        :return Boolean:
        """

        for parcel in self.parcels:
            if parcel['id'] == id:
                if parcel['status'] == 'delivered':
                    return True
        return False

    def get_charge(self, weight, distance):
        """
        calculates the charge
        :param weight:
        :param distance:
        :return:
        """
        return self.base_price + (weight * distance)

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
                "https://www.mapquestapi.com/geocoding/v1/address?key=" + self.trulysKey + "&inFormat=kvp&outFormat=json&location= " + add + "&thumbMaps=false")
            data = r.json()
            results = data['results'][0]
            locations = results['locations']
            latlng = locations[0].get('latLng')
            return latlng
        except Exception as identifier:
            # print('Network Error')
            return {"lat": -24.90629, "lng": 152.19168}

    def is_parcel_owner(self, data, id):
        """
        checks if a parcel was created by loggedin user
        :param data:
        :param id:
        :return:
        """
        user_id = data['user_id']
        for p in self.parcels:
            if p['user_id'] == user_id:
                return True
        return False
