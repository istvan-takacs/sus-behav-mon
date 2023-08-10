import sys
sys.path.insert(0, '/home/istvan/Desktop/sus-behav-mon/handling_logs/')
sys.path.insert(0, '/home/istvan/Desktop/sus-behav-mon/reading_logs/')
import pyparsing_logs
import handling_logs
import mongo_connect
import datetime
from datetime import datetime
import subprocess
import threading
import syslog
import time
import select
import queue


# Tail logs on thread

def log_tailer(queue, event, app_list = [], threshold=0.1) -> None:
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
            if is_identified == "Safe":
                parsed_output["alert"] = False
            elif parsed_output.get("appname") in app_list:
                parsed_output["alert"] = True
            elif suspicious(parsed_output) < threshold or is_identified(parsed_output) == True:
                parsed_output["alert"] = True
            else:
                parsed_output["alert"] = False
            parsed_output["probability"] = suspicious(parsed_output)

            # Check if the parsed_output already exists in existing_entries
            key = (parsed_output["timestamp"], parsed_output["hostname"], parsed_output["appname"], parsed_output["pid"], parsed_output["message"])
            if key not in existing_entries:
                queue.put(parsed_output)
                existing_entries.add(key)  # Add the key to existing_entries set
            time.sleep(1)



# Parse tailed logs
#output below
# some_parsed_log = {'_id': 5800, 'appname': 'CRON', 'hostname': 'istvan-HP-ProBook-650-G1', 'message': '(root) CMD (   cd / && run-parts --report /etc/cron.hourly)', 'pid': '9272', 'timestamp': datetime.datetime(2023, 8, 6, 14, 17, 1)}


#create function for time of day
"""
(all incl.)

Morning: 0-5 
Beforenoon: 6-11
Afternooon: 12-17
Evening: 18-24
"""

def time_period(hr: int) -> str:
    lst = [int(i) for i in range(0, 24)]
    dct_morning = {str(k): "morning" for k in lst if k < 6}
    dct_beforenoon = {str(k): "beforenoon" for k in lst if k > 5 and k < 12 }
    dct_afternoon = {str(k): "afternoon" for k in lst if k > 11 and k < 18}
    dct_evening = {str(k): "evening" for k in lst if k > 17 and k < 24}
    merged = {**dct_morning, **dct_beforenoon, **dct_afternoon, **dct_evening}
    return merged.get(str(hr))


# check if suspicios
def suspicious(some_parsed_log) -> float:

    prob_table = handling_logs.get_alerts_from_db()
    
    host_to_check = some_parsed_log.get("hostname")
    app_to_check = some_parsed_log.get("appname")
    time_to_check = str(some_parsed_log.get("timestamp").hour)
    time_period_to_check = time_period(int(time_to_check))

    for dct in prob_table:
        if dct.get("hostname") == host_to_check and dct.get("appname") == app_to_check:
            return round(dct.get("probability").get(time_period_to_check), 2)


def is_identified(parsed_obj):
    client = mongo_connect.get_client()

    # Create a connection to the database.
    db = client[mongo_connect.get_database_name()]

    # Create collections.
    alerts_collection = db["Alerts"]
    host, app = parsed_obj["hostname"], parsed_obj["appname"]
    x = alerts_collection.find({
        "hostname":host, 
        "appname":app
    }, {"identified":1,
        "_id":0})
    return list(x)[0]["identified"] # To get only the boolean
    

def append_log():

    while True:
        syslog.syslog("This should show up in the logs")
        time.sleep(1)
        

                
if __name__ == "__main__":
    event = threading.Event()
    queue = queue.Queue()
    app_list = ['rtkit-daemon', 'goa-daemon', 'xbrlapi.desktop', "systemd"]
    x = threading.Thread(target=log_tailer, args=(queue, event, app_list, ),  daemon=True)
    x.start()
    # while True:
    print(queue.get())
    time.sleep(3)
    event.set()
    # o = {'timestamp': datetime(2023, 8, 9, 18, 35, 11), 'hostname': 'istvan-HP-ProBook-650-G1', 'appname': 'dbus-daemon', 'pid': '1614', 'message': "[session uid=1000 pid=1614] Successfully activated service 'org.gnome.Terminal'"}         
    # print(is_identified(o))