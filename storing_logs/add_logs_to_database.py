import sys
sys.path.insert(0, '/home/istvan/Desktop/sus-behav-mon/reading_logs/')
import all_logs
import mongo_connect
import pymongo
from datetime import datetime


def insert_into_collection(objs_to_add, clt="MainLogs"):  # 10 objs
    
    # Get a client connection to the MongoDB database.
    client = mongo_connect.get_client()

    # Create a connection to the database.
    db = client[mongo_connect.get_database_name()]

    # Load in collections.
    collection = db[clt]

    for document in objs_to_add:
        collection.update_one(
            filter={
                '_id': document['_id'],
            },
            update={
                '$set': {k: document[k] for k in document},
            },
            upsert=True,
        )

def set_logs_collection():

    data_all_logs = all_logs.get_logs()
    insert_into_collection(data_all_logs, "Logs")

def get_logs_collection() -> list[dict]:
    # Get a client connection to the MongoDB database.
    client = mongo_connect.get_client()

    # Create a connection to the database.
    db = client[mongo_connect.get_database_name()]

    # Load in collections.
    log_collection = db["Logs"]

    # Select all documents from collections.
    cursor = list(log_collection.find({}))
    return cursor

if __name__ == "__main__":
     # Get a client connection to the MongoDB database.
    client = mongo_connect.get_client()

    # Create a connection to the database.
    db = client[mongo_connect.get_database_name()]

    print(">> Documents in the \"Logs\" collection:")
    print(db["Logs"].count_documents({}))
    set_logs_collection()
    print(">> Documents in the \"Logs\" collection:")
    print(db["Logs"].count_documents({}))
    print(list(db["Logs"].find({
        'hostname': 'istvan-HP-ProBook-650-G1'
    }))[-1])
    