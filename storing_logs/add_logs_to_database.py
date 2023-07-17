import sys
sys.path.insert(0, '/home/istvan/Desktop/sus-behav-mon/reading_logs/')
import pyparsing_logs
import pyparsing_logs_network
from pprint import pprint
import mongo_connect
import pymongo

  
def get_main_log_collection():
    data_main = pyparsing_logs.pyparse_logs()

    # Get a client connection to the MongoDB database.
    client = mongo_connect.get_client()

    # Create a connection to the database.
    db = client[mongo_connect.get_database_name()]

    # Create collections.
    main_log_collection = db['MainLogs']

    # Create unique indexes so that no duplicate logs are accepted
    main_log_collection.create_index([("index", pymongo.ASCENDING)] , unique=True)

    # Insert the documents into the collection.
    i = 0
    for index in data_main:
        try:
            result = main_log_collection.insert_one(data_main[i])
            i += 1

        except pymongo.errors.DuplicateKeyError as dpk:
            pass

    return list([dicts for dicts in main_log_collection.find()])


def get_network_log_collection():
    data_network = pyparsing_logs_network.pyparse_logs()

    # Get a client connection to the MongoDB database.
    client = mongo_connect.get_client()

    # Create a connection to the database.
    db = client[mongo_connect.get_database_name()]

    # Create collections.
    network_log_collection = db["NetworkLogs"]

    # Create unique indexes so that no duplicate logs are accepted
    network_log_collection.create_index([("index", pymongo.ASCENDING)] , unique=True)

    # Insert the documents into the collection.
    i = 0
    for index in data_network:
        try:
            result = network_log_collection.insert_one(data_network[i])
            i += 1

        except pymongo.errors.DuplicateKeyError as dpk:
            pass 

    return list([dicts for dicts in network_log_collection.find()])
 

# print(result.inserted_ids)
# print(">> Documents in the \"MainLogs\" collection:")
# print(db["MainLogs"].count_documents({}))
# print(">> Documents in the \"NetworkLogs\" collection:")
# print(db["NetworkLogs"].count_documents({}))



# print(db["MainLogs"].distinct("appname"))
    
