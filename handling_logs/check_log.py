import subprocess
import threading
import syslog
import time
import select
import queue
import threading
import numpy as np
from reading_logs import pyparsing_logs
from storing_logs.add_logs_to_database import get_collection, get_logs_collection



# Tail logs on thread
def log_tailer(queue: queue, event: threading.Event, app_list: list = [], threshold: float = 0.1) -> None:
    f = subprocess.Popen(['tail', '-F', "-n" "5", "/var/log/syslog"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p = select.poll()
    p.register(f.stdout)

    existing_entries = set()  # Keep track of existing entries using a set
    while True:
        if event.is_set():
            break
        if p.poll(1):
            output = f.stdout.readline().strip()
            parsed_output = pyparsing_logs.pyparse_tail_logs(output)
            
            parsed_output = set_log_fields(parsed_output, app_list, threshold)

            # Check if the parsed_output already exists in existing_entries
            key = (parsed_output["timestamp"], parsed_output["hostname"], parsed_output["appname"], parsed_output["pid"], parsed_output["message"])
            if key not in existing_entries:
                queue.put(parsed_output)
                existing_entries.add(key)  # Add the key to existing_entries set
            time.sleep(1)


def set_log_fields(parsed_log: dict, app_list: list = [], threshold: float = 0.1) -> dict:

    if is_identified == "Safe":
        parsed_log["alert"] = False
    elif parsed_log.get("appname") in app_list:
        parsed_log["alert"] = True
    elif suspicious(parsed_log) < threshold or is_identified(parsed_log) == True:
        parsed_log["alert"] = True
    else:
        parsed_log["alert"] = False
    parsed_log["probability"] = suspicious(parsed_log)

    return parsed_log


# check if suspicios
def suspicious(some_parsed_log: dict) -> float:

    prob_table = get_logs_collection("Alerts")
    host_to_check = some_parsed_log.get("hostname")
    app_to_check = some_parsed_log.get("appname")
    time_to_check = int(some_parsed_log.get("timestamp").hour)

    for dct in prob_table:
        if dct.get("hostname") == host_to_check and dct.get("appname") == app_to_check:
            number_of_intervals = len(dct.get("probability"))-24
            interval_bin_edges = np.linspace(0, 23, number_of_intervals, dtype=int)
            for bin_edge in interval_bin_edges[1:]:
                if time_to_check <= bin_edge:
                    index = (np.where(interval_bin_edges == bin_edge)[0])[0]
                    key = f"Interval {index}"
                    probability = round(dct.get("probability").get(key), 2)
                    return probability
    # The host never called this service before
    return 0        

def is_identified(parsed_obj) -> bool | str:
    
    alerts_collection = get_collection("Alerts")

    host, app = parsed_obj["hostname"], parsed_obj["appname"]
    x = alerts_collection.find({
        "hostname":host, 
        "appname":app
    }, {"identified":1,
        "_id":0})
    # If not in collection return False
    if not list(x):
        return False
    return list(x)[0]["identified"] # To get only the relevant field