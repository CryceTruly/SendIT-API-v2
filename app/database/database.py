import psycopg2


class Database(object):
    """class for the database"""
    DB_CONNECTION_STR = "dbname='postgres' user='postgres' host='localhost' password='crycetruly' port='5432'"

    def __init__(self):
        """initialize  connection """
        try:
            """
            creates a db
            """
            self.connection = psycopg2.connect(dbname="sendit", user="postgres", password="crycetruly")
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            self.create_tables()
        except(Exception, psycopg2.DatabaseError) as e:
            print('There was an error' + str(e))

    def create_tables(self):

        """ create tables """
        create_table = """CREATE TABLE IF NOT EXISTS users
            (user_id SERIAL PRIMARY KEY, full_name VARCHAR(255),username VARCHAR(30),
            email VARCHAR(255),password VARCHAR(150), phone_number VARCHAR(100),
            is_admin BOOLEAN DEFAULT FALSE ,joined DATE DEFAULT CURRENT_TIMESTAMP )"""
        self.cursor.execute(create_table)
        self.connection.commit()

        create_table = """ CREATE TABLE IF NOT EXISTS parcels(
            parcel_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(user_id),
            destination_address VARCHAR(500) NOT NULL,
            pickup_address VARCHAR (255),
            comment_description VARCHAR (500),
            sender_email VARCHAR (255),
            status VARCHAR (25),
            recipient_name VARCHAR (255),
            weight INTEGER ,
            current_location VARCHAR (255),
            recipient_email VARCHAR (255),
            recipient_phone VARCHAR (255),
            pickplatlng TEXT,
            destlatlng TEXT ,
            distance DOUBLE PRECISION,
            price DOUBLE PRECISION,
            created DATE NOT NULL DEFAULT CURRENT_TIMESTAMP)"""
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

    def insert_into_parcels(self, destination_address, pickup_address, comment_description, user_id, sender_email,
                            recipient_phone, recipient_email, recipient_name, weight, latlng, destlatlng, distance,
                            price):
        """
        Query to add parcel order to the database : by user
        """
        order_query = """INSERT INTO parcels(destination_address, pickup_address, comment_description,
                     user_id, sender_email, recipient_phone,
                     recipient_email, recipient_name, weight,pickplatlng,destlatlng,distance,price)
                    VALUES('{}','{}','{}','{}','{}','{}'); """.format(
            destination_address, pickup_address, comment_description, user_id, sender_email, recipient_phone,
            recipient_email, recipient_name, weight, latlng, destlatlng, distance, price)
        self.cursor.execute(order_query)
        self.connection.commit()

    def get_all_parcels(self):
        """
        Query gets all parcel-orders that are available
        :admin
        """
        self.cursor.execute("SELECT * FROM parcels")
        all_parcels = self.cursor.fetchall()
        parcel_list = []
        for parcel in all_parcels:
            parcel_list.append(parcel)
        return parcel_list

    def get_users(self):
        self.cursor.execute("SELECT * FROM users")
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
        query = "SELECT * FROM {} WHERE {} = '{}';".format(
            table_name, table_column, value)
        self.cursor.execute(query)
        results = self.cursor.fetchone()
        return results

    def get_user_by_value(self, table_name, column, value):
        """
        Function  gets items from the
        same table with similar email :email
        """
        query = "SELECT * FROM {} WHERE {} = '{}';".format(table_name, column, value)
        self.cursor.execute(query)
        results = self.cursor.fetchone()
        return results

    def get_user_parcels(self, user_id):
        """
        Select from parcels where parcel.user_id = user.user_id
        :Admin
        """
        query = "SELECT * FROM  parcels WHERE user_id = '{}';".format(user_id)
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
        sql = "SELECT status FROM parcels WHERE id ='{}'".format(id)
        self.cursor.execute(sql)
        self.connection.commit()
        order = self.cursor.fetchone()
        status = order[0]
        if status == 'delivered':
            return True
        return False

    def update_role(self, role, email):
        query = """UPDATE users SET role = '{}'
                WHERE email ='{}' """.format(role, email)
        self.cursor.execute(query)
        self.connection.commit()

    def change_destination(self, table_name, column, new_value, parcel_id):
        query = "UPDATE {} SET {} = '{}' WHERE parcel_id ={};".format(table_name, column, new_value, parcel_id)
        self.cursor.execute(query)
        self.connection.commit()

    def delete_table_column(self, table_name, table_colum, id):
        delete_query = "DELETE from {} WHERE {} = '{}';".format(
            table_name, table_colum, id)
        self.cursor.execute(delete_query)
        self.connection.commit()

    def change_present_location(self, table, column, location, parcel_id):
        query = "UPDATE {} SET {} = '{}' WHERE parcel_id ={};".format(table, column, location, parcel_id)
        self.cursor.execute(query)
        self.connection.commit()

    def cancel_parcel(self, id):
        sql = "UPDATE parcels SET status='{}' WHERE parcel_id = '{}'".format('cancelled', id)
        self.cursor.execute(sql)
        self.connection.commit()
        return self.get_parcel_by_value('parcels', 'parcel_id', id)

    def is_parcel_owner(self, parcel_id, user_id):
        sql = "SELECT user_id FROM parcels WHERE user_id ='{}'".format(user_id)
        self.cursor.execute(sql)
        self.connection.commit()
        order = self.cursor.fetchone()
        if len(order) == 1:
            return True
        return False

    def drop_tables(self):
        drop_query = "DROP TABLE IF EXISTS {0} CASCADE"
        tables = ["users", "parcels"]
        for table in tables:
            self.cursor.execute(drop_query.format(table))
