import psycopg2


class Database(object):
    """class for the database"""
    DATABASE_URL = "postgresql://postgres:crycetruly@localhost:5432/sendit"

    def __init__(self):
        """initialize  connection """
        try:
            self.connection = psycopg2.connect(
                str(self.DATABASE_URL))

            self.connection.autocommit = True
            self.cursor = self.connection.cursor()

        except(Exception, psycopg2.DatabaseError) as e:
            print(e)

    def create_tables(self):
        """ create tables """
        create_table = """CREATE TABLE IF NOT EXISTS users
            (user_id SERIAL PRIMARY KEY, username VARCHAR(30),
            email VARCHAR(100),password VARCHAR(150), phone_number VARCHAR(100),
            is_admin BOOLEAN DEFAULT FALSE ,joined  DEFAULT CURRENT_TIMESTAMP )"""
        self.cursor.execute(create_table)

        create_table = """ CREATE TABLE IF NOT EXISTS parcels(
            parcel_id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL,
            destination_address VARCHAR(500) NOT NULL,pickup_address VARCHAR (255),comment_description VARCHAR (500),sender_email VARCHAR (255)
            status VARCHAR (25),recipient_name VARCHAR (255),weight INTEGER ,current_location VARCHAR (255),recipient_email VARCHAR (255),recipient_phone VARCHAR (255),
            created DATE NOT NULL DEFAULT CURRENT_TIMESTAMP , FOREIGN KEY(user_id)
            REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY(sender_email) REFERENCES users(email) ON UPDATE CASCADE ON
            DELETE CASCADE)"""
        self.cursor.execute(create_table)

    def insert_into_user(self, fullname, username, email, phone_number, password):
        """
        Query to add a new user
        :admin,user
        """
        user = """INSERT INTO users
                (fullname, username,email, phone_number, password)
                VALUES ('{}','{}','{}','{}');
                """.format(fullname, username, email, phone_number, password)
        self.cursor.execute(user)
        self.connection.commit()

    def insert_into_parcels(
            self, user_id, menu_id, meal, description, price, status
    ):
        """
        Query to add parcel order to the database : user
        """
        order_query = """INSERT INTO parcels(destination_address, pickup_address, comment_description,
                     user_id, sender_email, recipient_phone,
                     recipient_email, recipient_name, weight)
                    VALUES('{}','{}','{}','{}','{}','{}'); """.format(
            user_id, menu_id, meal, description, price, status)
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

    def update_role(self, role, email):
        query = """UPDATE users SET role = '{}'
                WHERE email ='{}' """.format(role, email)
        self.cursor.execute(query)
        self.connection.commit()

    def delete_table_column(self, table_name, table_colum, id):
        delete_query = "DELETE from {} WHERE {} = '{}';".format(
            table_name, table_colum, id)
        self.cursor.execute(delete_query)
        self.connection.commit()

    def drop_tables(self):
        drop_query = "DROP TABLE IF EXISTS {0} CASCADE"
        tables = ["users", "parcels"]
        for table in tables:
            self.cursor.execute(drop_query.format(table))
