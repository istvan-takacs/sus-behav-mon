import numpy as np
import pandas as pd
from storing_logs import add_logs_to_database


def hist_maker(host: str, app: str, df: pd.DataFrame, number_of_bins: int = 5) -> dict:
    """
    Function to create a dictionary of probabilities based on the frequency that a given host calls a given service in a given time period

    Currently set to create 5 intervals that can be interpreted this way:
    (all incl.)
    Morning: 0-5 
    Beforenoon: 6-11
    Afternooon: 12-17
    Evening: 18-23
    """

    my_df = df[(df.hostname == host) & (df.appname == app)]
    total_sum = my_df.time.apply(lambda x: x.hour).value_counts().sum()

    # Getting a column of probabilities that the service will be called by the host at that hour
    normalised = (my_df.time.apply(lambda x: x.hour).value_counts()/total_sum).to_frame()
    normalised.columns = ['probability']  # Define a column name
    normalised.set_index(normalised.index, inplace=True)

    # Ensure all hours are included in the index
    for i in range(0, 24):
        if i not in normalised.index:
            normalised.loc[i] = [0]
    # Sort the DataFrame by index
    normalised.sort_index(inplace=True)
    # Get interval edges based on the number of intervals we want to create 
    bins =  np.linspace(0, 23, number_of_bins, dtype=int)
    ind = np.digitize(normalised.index, bins)

    # Sum the probability across hours and assign them to their respective intervals
    intervals = normalised.groupby(ind).sum()
    indexes = []
    for i in range(1, len(intervals)+1):
        indexes.append(f"Interval {i}") # Name the intervals
    index = pd.Index(indexes)
    intervals.set_index(index, inplace=True)

    # Concatenate the 2 dataframes so we have acces to both the hours and intervals probabilities
    data = pd.concat([intervals, normalised], axis=0)
    data.index = data.index.map(str)
    return data.to_dict().get("probability")
    
    

def create_alerts() -> list[dict]:
    """
    Function to create a list of dictionaries assigning the respective probabilities to each host and app in the collection
    """
    df =  pd.DataFrame(add_logs_to_database.get_logs_collection())
    df['time'] = [d.time() for d in df['timestamp']]
    hostnames = df["hostname"].unique() # All hostnames in the dataframe
    appnames = df["appname"].unique() # All appnames in the dataframe
    alerts = []
    id = 1
    for host in hostnames:
        for app in appnames:
            hist = hist_maker(host, app, df) # The probability dictionary created by the hisy_maker function
            temp_dct = {"_id": str(id), "hostname":host, "appname":app, "probability": hist}
            alerts.append(temp_dct)
            id += 1
    return alerts

def get_all_services() -> list:
    """
    Function to get all services in the log collection so that they can be displayed to the user on the Configuration tab
    """
    df =  pd.DataFrame(add_logs_to_database.get_logs_collection())
    appnames = df["appname"].unique()
    return list(appnames)
