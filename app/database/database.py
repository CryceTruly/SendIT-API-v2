import psycopg2
import json
from werkzeug.security import generate_password_hash
import os


class Database(object):
    """class for the database"""

    def __init__(self):
        """initialize  connection """
        """
        creates a db
        """
        try:
            # use our connection values to establish a connection
            self.connection = psycopg2.connect(
                os.environ.get("DATABASE_URL", ""))
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            self.create_tables()
        except Exception as i:
            print(i)

    def create_tables(self):
        """ create tables """
        img = 'https://bit.ly/2GNPIyC'
        create_table = """CREATE TABLE IF NOT EXISTS users
            (user_id SERIAL PRIMARY KEY, full_name VARCHAR(255),username VARCHAR(30) UNIQUE,imageUrl VARCHAR(500) DEFAULT '{}',
            email VARCHAR(255),password VARCHAR(150), phone_number VARCHAR(100),is_verified BOOLEAN DEFAULT False,
            is_admin BOOLEAN DEFAULT FALSE ,joined TIMESTAMPTZ DEFAULT Now())""".format(img)
        self.cursor.execute(create_table)
        self.connection.commit()
        password = generate_password_hash('adminuser')
        try:
            sql = """INSERT INTO users(user_id,full_name,username,password,phone_number,email,is_admin,is_verified)
                VALUES (100,'Admin User','senditadmin','{}','0700000000','admin@sendit.com',True,True)""".format(
                password)
            self.cursor.execute(sql)
            self.connection.commit()
        except Exception as identifier:
            pass

        create_table = """ CREATE TABLE IF NOT EXISTS parcels(
            parcel_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(user_id),
            destination_address VARCHAR(500) NOT NULL,
            pickup_address VARCHAR (255),
            parcel_description VARCHAR (500),
            sender_email VARCHAR (255),
            status VARCHAR (25) DEFAULT 'order_placed',
            recipient_name VARCHAR (255),
            weight INTEGER ,
            qty INTEGER,
            current_location VARCHAR (255),
            recipient_email VARCHAR (255),
            recipient_phone VARCHAR (255),
            pickplatlng json,
            destlatlng json ,
            distance DOUBLE PRECISION,
            price DOUBLE PRECISION,
            created TIMESTAMPTZ DEFAULT Now() ,last_modified TIMESTAMPTZ DEFAULT Now())"""
        self.cursor.execute(create_table)
        self.connection.commit()

        create_table = """CREATE TABLE IF NOT EXISTS tokens
              (id SERIAL PRIMARY KEY,token TEXT, is_valid BOOLEAN DEFAULT TRUE,
              last_used TIMESTAMPTZ DEFAULT Now())"""
        self.cursor.execute(create_table)
        self.connection.commit()

    def insert_into_user(self, fullname, username, email, phone_number, password):
        """
        Query to add a new user
        :admin,user
        """
        user = """INSERT INTO users(full_name, username,email, phone_number,password)
                VALUES ('{}','{}','{}','{}','{}');
                """.format(fullname, username, email, phone_number, password)
        self.cursor.execute(user)
        self.connection.commit()

    def insert_into_parcels(self, destination_address, pickup_address,
                            parcel_description, user_id, sender_email,
                            recipient_phone, recipient_email, recipient_name, weight, qty, latlng, destlatlng, distance,
                            price):
        """
        Query to add parcel order to the database : by user
        """
        order_query = """INSERT INTO parcels(destination_address, pickup_address, parcel_description,
                     user_id, sender_email, recipient_phone,
                     recipient_email, recipient_name, weight,qty,current_location,pickplatlng,destlatlng,distance,price)
                    VALUES('{}','{}','{}','{}','{}','{}','{}','{}',{},{} ,'{}','{}','{}',{},{}); """.format(
            destination_address, pickup_address, parcel_description, user_id, sender_email, recipient_phone,
            recipient_email, recipient_name, weight, qty, pickup_address, json.dumps(
                latlng), json.dumps(destlatlng),
            distance, price)
        self.cursor.execute(order_query)
        self.connection.commit()

    def get_all_parcels(self):
        """
        Query gets all parcel-orders that are available
        :admin
        """

        self.cursor.execute("SELECT * FROM parcels ORDER BY parcel_id DESC")
        all_parcels = self.cursor.fetchall()
        parcel_list = []
        for parcel in all_parcels:
            parcel_list.append(parcel)
        return parcel_list

    def get_users(self):
        self.cursor.execute("SELECT * FROM users ORDER BY joined DESC")
        users = self.cursor.fetchall()
        user_list = []
        for user in users:
            user_list.append(user)
        return user_list

    def get_parcel_by_value(self, table_name, table_column, value):
        """
        Function  gets items from the
        same table with similar ids :admin
        """
        try:

            query = "SELECT * FROM {} WHERE {} = '{}';".format(
                table_name, table_column, value)
            self.cursor.execute(query)
            results = self.cursor.fetchone()
            return results
        except Exception as e:
            return None

    def get_user_by_value(self, table_name, column, value):
        """
        Function  gets items from the
        same table with similar email :email
        """
        query = "SELECT * FROM {} WHERE {} = '{}';".format(
            table_name, column, value)
        self.cursor.execute(query)
        results = self.cursor.fetchone()
        return results

    def get_user_parcels(self, user_id):
        """
        Select from parcels where parcel.user_id = user.user_id
        :Admin
        """
        query = "SELECT * FROM  parcels WHERE user_id = '{}' ORDER BY parcel_id DESC;".format(
            user_id)
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        if results:
            return results
        return "No parcels yet"

    def update_parcel_status(self, stat, id):
        """
        update table parcels set status ='' where parcel_id = id
        :Admin
        """

        status = ['pickup_started', 'in_transit', 'cancelled', 'delivered']
        if stat in status:
            query = """UPDATE parcels SET status = '{}'
                        WHERE parcel_id ='{}' """.format(stat, id)
            self.cursor.execute(query)
            self.connection.commit()
            return "status updated successfully"
        return "Invalid status name"

    def is_order_delivered(self, id):
        sql = "SELECT status FROM parcels WHERE parcel_id ='{}'".format(id)
        self.cursor.execute(sql)
        self.connection.commit()
        order = self.cursor.fetchone()
        status = order[0]
        if status == 'delivered':
            return True
        return False

    def update_role(self, id):
        query = """UPDATE users SET is_admin = {}
                    WHERE user_id ='{}' """.format(True, id)
        self.cursor.execute(query)
        self.connection.commit()

    def revoke_admin_previledges(self, id):
        query = """UPDATE users SET is_admin = {}
                    WHERE user_id ='{}' """.format(False, id)
        self.cursor.execute(query)
        self.connection.commit()

    def change_destination(self, new_value, parcel_id, destlatlng, new_distance, new_price):
        query = "UPDATE parcels SET destination_address = '{}' WHERE parcel_id ={};".format(
            new_value, parcel_id)
        self.cursor.execute(query)
        self.connection.commit()
        query2 = "UPDATE parcels SET destlatlng = '{}' WHERE parcel_id ={};".format(
            json.dumps(destlatlng), parcel_id)
        self.cursor.execute(query2)
        self.connection.commit()

        query3 = "UPDATE parcels SET price = '{}' WHERE parcel_id ={};".format(
            new_price, parcel_id)
        self.cursor.execute(query3)
        self.connection.commit()

        query4 = "UPDATE parcels SET distance = '{}' WHERE parcel_id ={};".format(
            new_distance, parcel_id)
        self.cursor.execute(query4)
        self.connection.commit()

        return new_value

    def delete_table_column(self, table_name, table_colum, id):
        delete_query = "DELETE from {} WHERE {} = '{}';".format(
            table_name, table_colum, id)
        self.cursor.execute(delete_query)
        self.connection.commit()

    def change_present_location(self, location, parcel_id):
        query = "UPDATE  parcels SET current_location = '{}' WHERE parcel_id ={};".format(
            location, parcel_id)
        self.cursor.execute(query)
        self.connection.commit()

    def cancel_parcel(self, id):
        sql = "UPDATE parcels SET status='{}' WHERE parcel_id = '{}'".format(
            'cancelled', id)
        self.cursor.execute(sql)
        self.connection.commit()
        return self.get_parcel_by_value('parcels', 'parcel_id', id)

    def is_parcel_owner(self, parcel_id, user_id):
        sql = "SELECT user_id FROM parcels WHERE user_id ='{}'".format(user_id)
        self.cursor.execute(sql)
        self.connection.commit()
        order = self.cursor.fetchone()
        if order:
            return True
        return False

    def drop_tables(self):
        drop_query = "DROP TABLE IF EXISTS {0} CASCADE"
        tables = ["users", "parcels"]
        for table in tables:
            self.cursor.execute(drop_query.format(table))

    def is_admin(self, user_id):
        sql = "SELECT is_admin from users WHERE user_id ={}".format(user_id)
        self.cursor.execute(sql)
        self.connection.commit()
        results = self.cursor.fetchone()
        return results[0]

    def get_user_email(self, user_id):
        sql = "SELECT email from users WHERE user_id ={}".format(user_id)
        self.cursor.execute(sql)
        self.connection.commit()
        results = self.cursor.fetchone()
        return results[0]

    def change_status(self, param, id):
        query = "UPDATE parcels SET status = '{}' WHERE parcel_id ={};".format(
            param, id)
        self.cursor.execute(query)
        self.connection.commit()

    def new_parcel_has_fishy_behaviour(self, user_id, reciever_email, desc):
        sql = "SELECT * FROM parcels WHERE user_id = {} AND recipient_email= '{}' and parcel_description = '{}'".format(
            user_id, reciever_email, desc)
        self.cursor.execute(sql)
        self.connection.commit()
        results = self.cursor.fetchall()
        return results

    def get_current_location(self, id):
        query = "SELECT current_location FROM parcels WHERE parcel_id={}".format(
            id)
        self.cursor.execute(query)
        self.connection.commit()
        results = self.cursor.fetchone()
        return results[0]

    def get_parce_owner_id(self, id):
        query = "SELECT user_id FROM parcels WHERE parcel_id={}".format(id)
        self.cursor.execute(query)
        self.connection.commit()
        results = self.cursor.fetchone()
        return results[0]

    def get_destination_address(self, id):
        query = "SELECT destination_address FROM parcels WHERE parcel_id={}".format(
            id)
        self.cursor.execute(query)
        self.connection.commit()
        results = self.cursor.fetchone()
        return results[0]

    def get_pick_up_latlng(self, id):
        query = "SELECT pickplatlng FROM parcels WHERE parcel_id={}".format(id)
        self.cursor.execute(query)
        self.connection.commit()
        results = self.cursor.fetchone()
        return results[0]

    def get_last_insert_id(self):
        query = "SELECT parcel_id FROM parcels ORDER BY parcel_id DESC"
        self.cursor.execute(query)
        self.connection.commit()
        results = self.cursor.fetchone()
        return results[0]

    def get_destination_latlng(self, id):
        query = "SELECT destlatlng  FROM parcels WHERE parcel_id={}".format(id)
        self.cursor.execute(query)
        self.connection.commit()
        results = self.cursor.fetchone()
        return results[0]

    def get_parcel_weight(self, id):
        query = "SELECT weight FROM parcels WHERE parcel_id={}".format(id)
        self.cursor.execute(query)
        self.connection.commit()
        results = self.cursor.fetchone()
        return results[0]

    def save_token(self, token):
        query = "INSERT INTO tokens(token) VALUES = '{}'".format(str(token))
        self.cursor.execute(query)
        self.connection.commit()

    def invalidate_a_token(self, token):
        query = "UPDATE tokens SET is_valid  ={} WHERE token = '{}'".format(
            False, token)
        self.cursor.execute(query)
        self.connection.commit()

    def is_token_invalid(self, token):
        query = "SELECT is_valid FROM tokens WHERE token={}".format(token)
        self.cursor.execute(query)
        self.connection.commit()
        results = self.cursor.fetchone()
        return results[0]

    def delete_parcel(self, id):
        sql = "DELETE FROM  parcels WHERE parcel_id = '{}'".format(id)
        self.cursor.execute(sql)
        self.connection.commit()
        return id

    def search_app(self, query):
        # q = """SELECT users.user_id,users.full_name,users.email FROM users WHERE email LIKE '%{}%' OR username LIKE '%{}%'
        # OR full_name LIKE '%{}%' OR phone_number LIKE '%{}%'
        #  UNION
        #  SELECT parcels.parcel_id,parcels.sender_email,parcels.status FROM parcels WHERE destination_address  LIKE '%{}%' OR sender_email LIKE '%{}%' OR  pickup_address  LIKE '%{}%' OR  recipient_email  LIKE '%{}%' OR parcel_description  LIKE '%{}%' """ \
        #     .format(query, query, query, query, query, query, query, query, query)
        q = """SELECT users.user_id,users.full_name,users.email FROM users WHERE email LIKE '%{}%' OR username LIKE '%{}%'
               OR full_name LIKE '%{}%' OR phone_number LIKE '%{}%'""".format(query, query, query, query)

        self.cursor.execute(q)
        self.connection.commit()
        results = self.cursor.fetchall()
        if results:
            return results
        return "No matches found"

    def verify_user(self, user):
        query = "UPDATE users SET is_verified = {} WHERE email = '{}';".format(
            True, str(user['email']))
        self.cursor.execute(query)
        self.connection.commit()

    def change_user_password(self, email, password):
        password_hash = generate_password_hash(password)
        query = "UPDATE users SET password = '{}' WHERE email = '{}';".format(
            password_hash, email)
        self.cursor.execute(query)
        self.connection.commit()
