import sys
import datetime
sys.path.insert(0, '/home/istvan/Desktop/sus-behav-mon/storing_logs/')
sys.path.insert(0, '/home/istvan/Desktop/sus-behav-mon/handling_logs/')
from handling_logs import get_alerts
import pandas as pd
import mongo_connect
import pymongo


def get_threshold(threshold=0.1):
    return threshold


def get_data_from_db() -> list[dict]:
    # Get a client connection to the MongoDB database.
    client = mongo_connect.get_client()

    # Create a connection to the database.
    db = client[mongo_connect.get_database_name()]

    # Load in collections.
    main_log_collection = db["MainLogs"]
    network_log_collection = db["NetworkLogs"]

    # Update collections.
    new_value = {"$set": {"alert":True}}
    query = {}
    network_log_collection.update_many(query, new_value)

    # Select all documents from collections.
    cursor_main = list(main_log_collection.find({}, {"_id":False}))
    cursor_network = list(network_log_collection.find({}, {"_id":False}))
    cursor = cursor_main + cursor_network
    return cursor


print(get_data_from_db()[-1])
print(get_alerts().keys())

