import os
import pymongo


def get_client():
    """
    A function to get a MongoDB client connection.
    """

    server = os.getenv('MONGODB_SERVER', 'localhost')
    client = None

    # If the user name or password is empty.

    client = pymongo.MongoClient(host=server,port=27017)

    # Test the connection to see if it is valid.
    try:
        client.server_info()
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(err)
        return None

    return client


def get_database_name():
    """
    A function to return the MongoDB database name.
    """
    return os.getenv('MONGODB_DB', 'logs')
