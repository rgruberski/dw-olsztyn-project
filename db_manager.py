import mysql.connector
from db_config import db_config

class DBManager():

    def __init__(self):
        
        self.cnx = mysql.connector.connect(**db_config)
        self.cursor = self.cnx.cursor()

        print("Connected to database")

    def execute(self, query):
        
        self.cursor.execute(query)

    def query(self, query):

        self.execute(query)

        return self.cursor.fetchall()

    def setup_table(self):
        self.execute("""
        CREATE TABLE IF NOT EXISTS most_popular 
        (
            timestamp DATETIME NOT NULL, 
            name VARCHAR(30) NOT NULL,
            source VARCHAR(10) NOT NULL
        )
        """)

        print("DB table is up and ready")
    
    def insert_data(self, timestamp, name, source):

        sql = f"""
        INSERT INTO most_popular 
        (timestamp, name, source) 
        VALUES ('{timestamp}', '{name}', '{source}')
        """

        self.execute( sql )
        # print( sql )

