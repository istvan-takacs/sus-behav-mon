import sys
import datetime
sys.path.insert(0, '/home/istvan/Desktop/sus-behav-mon/storing_logs/')
import pandas as pd
import mongo_connect
from datetime import datetime
import pymongo
import add_logs_to_database



def hist_maker(host, app):
    
    my_df = df[(df.hostname == host) & (df.appname == app)]
    total_sum = my_df.time.apply(lambda x: x.hour).value_counts().sum()

    normalised = (my_df.time.apply(lambda x: x.hour).value_counts()/total_sum)

    normal_dict = normalised.to_dict()

    for i in range(0, 25):
        if i not in normal_dict:
            normal_dict[i] = 0
    """
    (all incl.)
    
    Morning: 0-5 
    Beforenoon: 6-11
    Afternooon: 12-17
    Evening: 18-24
    """
    
    normal_dict["morning"] = sum([normal_dict.get(i) for i in normal_dict if type(i) is int and i < 6])
    normal_dict["beforenoon"] = sum([normal_dict.get(i) for i in normal_dict if type(i) is int and i < 12 and i >= 6])
    normal_dict["afternoon"] = sum([normal_dict.get(i) for i in normal_dict if type(i) is int and i < 18 and i >= 12])
    normal_dict["evening"] = sum([normal_dict.get(i) for i in normal_dict if type(i) is int and i < 24 and i >= 18])
    
    keyorder = ['morning', 'beforenoon', 'afternoon', 'evening'] + [i for i in range(0, 24)]
    new_dct = {str(k): normal_dict[k] for k in keyorder if k in normal_dict}

    return new_dct

def create_alerts() -> list[dict]:

    global df
    df =  pd.DataFrame(add_logs_to_database.get_logs_collection())
    # df['date'] = [d.date() for d in df['timestamp']]
    df['time'] = [d.time() for d in df['timestamp']]
    # df["ttime"] = [datetime.datetime.combine(datetime.date.today(), t) for t in df["time"]]

    hostnames = df["hostname"].unique()
    appnames = df["appname"].unique()
    d = []
    id = 1
    for host in hostnames:
        for app in appnames:
            hist = hist_maker(host, app)
            temp_dct = {"_id": str(id), "hostname":host, "appname":app, "probability": hist}
            # merged = {**temp_dct, **hist}
            d.append(temp_dct)
            id += 1
    return d
    # print(d[('raspberrypi', 'polkitd(authority=local)')]) # dict{tuple:dict}

def add_alerts_to_db(alerts) -> None:
    
    data_alerts = alerts

    # Get a client connection to the MongoDB database.
    client = mongo_connect.get_client()

    # Create a connection to the database.
    db = client[mongo_connect.get_database_name()]

    # Create collections.
    alerts_collection = db["Alerts"]

    now = datetime.now()
    last_update = {"last_update":now}
    identified = {"identified":False}

    for document in data_alerts:
        temp_dct = {k: document[k] for k in document}

        alerts_collection.update_one(
            filter={
                '_id': document['_id'],
            },
            update={
                '$set': {**temp_dct, **last_update, **identified},
            },
            upsert=True,
        )

   
def get_alerts_from_db() -> list[dict]:

    # Get a client connection to the MongoDB database.
    client = mongo_connect.get_client()

    # Create a connection to the database.
    db = client[mongo_connect.get_database_name()]

    # Create collections.
    alerts_collection = db["Alerts"]

    return list(alerts_collection.find({}))

if __name__ == "__main__":

    print([i for i in create_alerts()])
    add_alerts_to_db(create_alerts())
    print(get_alerts_from_db()[-2])