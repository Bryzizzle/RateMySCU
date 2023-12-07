import os

import psycopg2
from psycopg2 import OperationalError

from .structs import EvalRequest


# CODE FOR CONNECTING TO AND QUERYING DATABASE

# create_connection: creates a connection to the postgres database
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
        connection.close()
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
        connection.close()
        return result
    except OperationalError as e:
        print(f"The error '{e}' occurred")


# Create a connection to Postgres database
def get_connection():
    return create_connection(os.environ.get('POSTGRES_DATABASE'), os.environ.get('POSTGRES_USER'),
                             os.environ.get('POSTGRES_PASSWORD'), os.environ.get('POSTGRES_HOST'),
                             os.environ.get('POSTGRES_PORT'))


def request_query_builder(request: EvalRequest):
    query = "SELECT * FROM evals"
    query_builder = []
    if any(field is not None for field in dict(request).values()):
        query += (" WHERE ")
        if request.id:
            query_builder.append("id='" + request.id + "'")
        if request.classname:
            query_builder.append("classname='" + request.classname + "'")
        if request.classcode:
            query_builder.append("classcode='" + request.classcode + "'")
        if request.quarter:
            query_builder.append("quarter='" + request.quarter + "'")
        if request.year:
            query_builder.append("year=" + str(request.year))
        if request.professor:
            query_builder.append("professor='" + request.professor + "'")
        if request.overall and request.overallSearch:
            if request.overallSearch == "greaterThan":
                query_builder.append("overall>=" + str(request.overall))
            elif request.overallSearch == "lessThan":
                query_builder.append("overall<=" + str(request.overall))
            elif request.overallSearch == "equals":
                query_builder.append("overall=" + str(request.overall))
    query += " AND ".join(query_builder) + ";"
    return query
