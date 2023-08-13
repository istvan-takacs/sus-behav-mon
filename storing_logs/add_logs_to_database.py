from reading_logs import all_logs
from storing_logs import mongo_connect
from pymongo import collection, errors
from datetime import datetime

def get_collection(clt: str) -> collection:
    """
    A function to return the collection that is passed in as an argument
    """
    # Get a client connection to the MongoDB database.
    client = mongo_connect.get_client()

    # Create a connection to the database.
    db = client[mongo_connect.get_database_name()]
    
    # Load collection
    return db[clt]

def insert_into_collection(objs_to_add: list[dict], clt: str) -> None:
    """
    A function to insert documents into a MongoDB collection
    """
    collection = get_collection(clt) # Specifying the collection to insert into
    for document in objs_to_add:
        # Query to insert the document if it does not already exist and update otherwise
        collection.update_one(
            filter={
                '_id': document['_id'],
            },
            update={
                '$set': {k: document[k] for k in document},
            },
            upsert=True,
        )

def set_logs_collection(clt: str = "Logs")-> None:
    """
    Function to insert all of the system logs that have not already been inserted into the Logs collection
    """
    data_all_logs = all_logs.get_logs()
    insert_into_collection(data_all_logs, clt)

def set_alerts_collection(alerts: list[dict], clt: str = "Alerts") -> None:
    """
    Function to insert all of the system logs that have not already been inserted into the Alerts collection
    """
    data_alerts = alerts
    # Get a client connection to the MongoDB database
    client = mongo_connect.get_client()
    # Create a connection to the database
    db = client[mongo_connect.get_database_name()]
    alerts_collection = db[clt]

    # Check if the collection exists
    try:
        db.validate_collection(clt)
        identified = {}
    except errors.OperationFailure:
        # Create an identified field if it does not exist and set it to False
        identified = {"identified":False} # This marks user feedback

    for document in data_alerts:
        temp_dct = {k: document[k] for k in document}
        alerts_collection.update_one(
            filter={
                '_id': document['_id'],
            },
            update={
                '$set': {**temp_dct,**identified}, # Insert identified as a field into the document
            },
            upsert=True
        )

def get_logs_collection(clt:str = "Logs") -> list[dict]:
    """
    Function to return all the elements from the specified collection
    """
    # Load in collection
    log_collection = get_collection(clt)

    # Select all documents from collection
    cursor = list(log_collection.find({}))
    return cursor
