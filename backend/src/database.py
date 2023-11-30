import psycopg2
from psycopg2 import OperationalError

# CODE FOR CONNECTING TO AND QUERYING DATABASE

#create_connection: creates a connection to the postgres database
def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection

# no_response_query: sends an SQL query with no expected response
def no_response_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Query executed successfully")
    except OperationalError as e:
        print(f"The error '{e}' occurred")

# select_query: sends an SQL query and interprets resulting evaluations as JSON
def select_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        # convert to json
        result = []
        for row in cursor.fetchall():
            dictionary = {}
            for i, value in enumerate(row):
                dictionary[cursor.description[i][0]] = value
            result.append(dictionary)
        print("Query executed successfully")
        return result
    except OperationalError as e:
        print(f"The error '{e}' occurred")
