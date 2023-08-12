from reading_logs import all_logs
from storing_logs import mongo_connect
from pymongo import collection
from datetime import datetime

def get_collection(clt: str) -> collection:
    # Get a client connection to the MongoDB database.
    client = mongo_connect.get_client()

    # Create a connection to the database.
    db = client[mongo_connect.get_database_name()]
    
    # Load collections.
    return db[clt]

def insert_into_collection(objs_to_add: list[dict], clt: str) -> None: 
    
    collection = get_collection(clt)
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

def set_logs_collection(clt: str = "Logs")-> None:

    data_all_logs = all_logs.get_logs()
    insert_into_collection(data_all_logs, clt)

def set_alerts_collection(alerts: list[dict], clt: str = "Alerts") -> None:
    
    data_alerts = alerts
    alerts_collection = get_collection(clt)

    identified = {"identified":False}

    for document in data_alerts:
        temp_dct = {k: document[k] for k in document}
        alerts_collection.update_one(
            filter={
                '_id': document['_id'],
            },
            update={
                '$set': {**temp_dct,**identified},
            },
            upsert=True
        )

def get_logs_collection(clt:str = "Logs") -> list[dict]:

    # Load in collections.
    log_collection = get_collection(clt)

    # Select all documents from collections.
    cursor = list(log_collection.find({}))
    return cursor

if __name__ == "__main__":
    
    # log_clt = get_collection("Logs")
    
    # print(">> Documents in the \"Logs\" collection:")
    # print(log_clt.count_documents({}))
    # set_logs_collection()
    # print(">> Documents in the \"Logs\" collection:")
    # print(log_clt.count_documents({}))
    # print(list(log_clt.find({
    #     'hostname': 'istvan-HP-ProBook-650-G1'
    # }))[-1])
    print(get_logs_collection("Alerts"))
