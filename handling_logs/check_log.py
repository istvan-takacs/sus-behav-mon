import subprocess
import threading
import time
import select
import queue
import threading
import numpy as np
from reading_logs import pyparsing_logs
from storing_logs.add_logs_to_database import get_collection, get_logs_collection


def log_tailer(queue: queue, event: threading.Event, app_list: list = [], threshold: float = 0.1) -> None:
    """
    Function to tail, parse, and analyse the logs of the system created to run on a thread
    """
    # Tail logs with subprocess
    f = subprocess.Popen(['tail', '-F', "-n" "5", "/var/log/syslog"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p = select.poll()
    p.register(f.stdout)

    existing_entries = set()  # Keep track of existing entries using a set
    while True:
        # The while loop is only broken when the event is set
        if event.is_set():
            break
        if p.poll(1):
            output = f.stdout.readline().strip()
            parsed_output = pyparsing_logs.pyparse_tail_logs(output) # Parsing the logs line
            parsed_output = set_log_fields(parsed_output, app_list, threshold) # Set some of the fields of the parsed line
            # Check if the parsed_output already exists in existing_entries
            key = (parsed_output["timestamp"], parsed_output["hostname"], parsed_output["appname"], parsed_output["pid"], parsed_output["message"])
            if key not in existing_entries:
                # If it does not exist add them to the queue
                queue.put(parsed_output)
                existing_entries.add(key)  # Add the key to the existing_entries set
            time.sleep(1) # Blocking implementation of the thread

def set_log_fields(parsed_log: dict, app_list: list = [], threshold: float = 0.1) -> dict:
    """
    Function to set the alert and probability fields of the tailed log so that they can be displayed
    """
    if is_identified == "Safe": # If marked by the user as safe set alert to False (takes precedence over blacklisting or threshold conditions)
        parsed_log["alert"] = False
    elif parsed_log.get("appname") in app_list: # If the app is blacklisted set alert True
        parsed_log["alert"] = True
    # If the probability is lower than the threshold or the user reported it suspicious
    elif suspicious(parsed_log) < threshold or is_identified(parsed_log) == True: 
        parsed_log["alert"] = True
    else:
        parsed_log["alert"] = False
    parsed_log["probability"] = suspicious(parsed_log)

    return parsed_log

def suspicious(some_parsed_log: dict) -> float:
    """
    Function to return the probability of the line being logged by that user, that service and in that interval
    """
    prob_table = get_logs_collection("Alerts")
    host_to_check = some_parsed_log.get("hostname")
    app_to_check = some_parsed_log.get("appname")
    time_to_check = int(some_parsed_log.get("timestamp").hour)

    for dct in prob_table:
        # In the alerts collection select the dictionary that has matching host and appnames
        if dct.get("hostname") == host_to_check and dct.get("appname") == app_to_check:
            number_of_intervals = len(dct.get("probability"))-24 # Get the number of intervals passed in the alerts collection
            interval_bin_edges = np.linspace(0, 23, number_of_intervals, dtype=int) # Reconstruct the intervals
            for bin_edge in interval_bin_edges[1:]:
                # If the time is in the bin we know the interval
                if time_to_check <= bin_edge:
                    index = (np.where(interval_bin_edges == bin_edge)[0])[0]
                    key = f"Interval {index}"
                    # Return the probability at that interval rounded to 2 decimals
                    probability = round(dct.get("probability").get(key), 2)
                    return probability
    return 0 # If the host never called this service before the probability is 0   

def is_identified(parsed_obj) -> bool | str:
    """
    Function to check whether the user reported the service or marked it safe
    """
    alerts_collection = get_collection("Alerts")
    host, app = parsed_obj["hostname"], parsed_obj["appname"]
    x = alerts_collection.find({
        "hostname":host, 
        "appname":app
    }, {"identified":1,
        "_id":0})
    result = list(x)
    # If not in collection return False
    if not result:
        return False
    return result[0]["identified"] # To get only the relevant field