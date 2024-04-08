from sqlalchemy import create_engine
from dotenv import dotenv_values

config = dotenv_values(".env")

connection_string = config["DATABASE_URI"]

def get_database():
    connection = create_engine(connection_string, echo=True).connect()
    return connection
