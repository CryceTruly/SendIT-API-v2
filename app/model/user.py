import datetime
import re

from .parcel import Parcel


class User:
    """
   user data structure
    """
    PARCEL = Parcel()
    


    def __init__(self):
        self.users = []
      
    def is_user_exist(self, id):
        """check if parcel not exist in the parcel list """
        for user in self.users:
            if user['user_id'] == id:
                return True

    def create_new_user(self, request_data):
        self.newuser = {
            "user_id": len(self.users) + 1,
            "fullname": request_data['fullname'],
            "username": request_data['username'],
            "phone_number": request_data['phone_number'],
            "email": request_data['email'],
            "password": request_data['password'],
            "joined": datetime.datetime.now()

        }
        self.users.append(self.newuser)
        return {"msg": "user created", "user": self.newuser.get('user_id')}

    def get_user_parcels(self, id):
        '''
        gets parcel orders for a specific users
        '''

        user_parcels = []
        for parcel in self.PARCEL.get_all_parcel():
            if parcel['user_id'] == id:
                user_parcels.append(parcel)
        return {"user_parcel_orders": user_parcels, "count": len(user_parcels)}

    def is_valid_user_request(self, newuser):
        """
        helper to check required fields
        """

        if "fullname" in newuser and "fullname" in newuser and "phone_number" in newuser and \
                "email" in newuser and "password" in newuser:
            return True
        else:
            return False

    def is_valid(self, email):
        """helper for chcking valid emails"""

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False
        return True

    def user_exists(self, id):
        '''
        helper to check user exists
        '''

        for user in self.users:
            if user['user_id'] == id:
                return True
        return False

    def is_email_taken(self, email):
        for user in self.users:
            if user['email'] == email:
                return False
        return True

    def is_username_taken(self, username):
        for user in self.users:
            if user['username'] == username:
                return False
        return True
