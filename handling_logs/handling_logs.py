import sys
import datetime
import numpy as np
sys.path.insert(0, '/home/istvan/Desktop/sus-behav-mon/storing_logs/')
import pandas as pd
import mongo_connect
from datetime import datetime
import add_logs_to_database
from add_logs_to_database import get_collection


def hist_maker(host: str, app: str, df: pd.DataFrame, number_of_bins: int = 5) -> dict:
    """
    Currently set to create 5 intervals that can be interpreted this way:
    (all incl.)
    Morning: 0-5 
    Beforenoon: 6-11
    Afternooon: 12-17
    Evening: 18-23
    """

    my_df = df[(df.hostname == host) & (df.appname == app)]
    total_sum = my_df.time.apply(lambda x: x.hour).value_counts().sum()

    normalised = (my_df.time.apply(lambda x: x.hour).value_counts()/total_sum).to_frame()
    normalised.columns = ['frequency']  # Define a column name

    normalised.set_index(normalised.index, inplace=True)

    # Ensure all hours are included in the index
    for i in range(0, 24):
        if i not in normalised.index:
            normalised.loc[i] = [0]

    # Sort the DataFrame by index
    normalised.sort_index(inplace=True)
    bins =  np.linspace(0, 23, number_of_bins, dtype=int)
    ind = np.digitize(normalised.index, bins)

    intervals = normalised.groupby(ind).sum()
    indexes = []
    for i in range(1, len(intervals)+1):
        indexes.append(f"Interval {i}")
    index = pd.Index(indexes)
    intervals.set_index(index, inplace=True)

    data = pd.concat([intervals, normalised], axis=0)
    data.index = data.index.map(str)
    return data.to_dict().get("frequency")
    
    

def create_alerts() -> list[dict]:

    df =  pd.DataFrame(add_logs_to_database.get_logs_collection())
    df['time'] = [d.time() for d in df['timestamp']]

    hostnames = df["hostname"].unique()
    appnames = df["appname"].unique()
    alerts = []
    id = 1
    for host in hostnames:
        for app in appnames:
            hist = hist_maker(host, app, df)
            temp_dct = {"_id": str(id), "hostname":host, "appname":app, "probability": hist}
            alerts.append(temp_dct)
            id += 1
    return alerts

def get_all_services() -> list:

    df =  pd.DataFrame(add_logs_to_database.get_logs_collection())
    appnames = df["appname"].unique()
    return list(appnames)

if __name__ == "__main__":
    
    pass
    # print([i for i in create_alerts()])
    # add_alerts_to_db(create_alerts())
    # print(get_alerts_from_db()[-2])

    # df =  pd.DataFrame(add_logs_to_database.get_logs_collection())
    # df['time'] = [d.time() for d in df['timestamp']]
    # print(hist_maker(host="raspberrypi", app="systemd", df= df))
    # print(create_alerts())