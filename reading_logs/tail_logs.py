# import time
# import subprocess
# import select

# f = subprocess.Popen(['tail','-F',"-n", "5", "/var/log/syslog"],\
#         stdout=subprocess.PIPE,stderr=subprocess.PIPE)
# p = select.poll()
# p.register(f.stdout)

# while True:
#     if p.poll(1):
#         print(f.stdout.readline())
#     time.sleep(1)

import time
import datetime
import subprocess
import select
import threading
import sys
sys.path.insert(0, '/home/istvan/Desktop/sus-behav-mon/reading_logs/')
import pyparsing_logs
## Non blocking implementation of tailing --> system does not have to wait before receiving new data

def log_tailer() -> None:
    f = subprocess.Popen(['tail','-F',"-n", "5", "/var/log/syslog"],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text = True)

    while True:
        output = f.stdout.readline().strip()
        parsed_output = pyparsing_logs.pyparse_tail_logs(output)
        if is_suspicious_tail(parsed_output):
            print("ALERT!!")
        print(parsed_output)

def time_of_day(hour: int) -> str:
    if hour <= 5:
        return "morning"
    elif hour > 5 and hour <= 11:
        return "beforenoon"
    elif hour > 11 and hour <= 17:
        return "afternoon"
    elif hour > 17 and hour <= 24:
        return "evening"
    
def set_threshold() -> float:
    return int(input("Enter the likelihood in percentages..."))/100

    
def is_suspicious_tail(log_dict: dict) -> bool:
    hour = log_dict.get("timestamp").hour
    period = time_of_day(hour)
    host = log_dict.get("hostname")
    app = log_dict.get("appname")
    threshold = 0.1
#     threshold = set_threshold()

    #The probability below which it would be suspicious
    print(threshold) 
    
    #The probability of this host calling this app at this time
    print(log_dict[(host, app)][period]) 
    
    return log_dict[(host, app)][period] < threshold

def test_thread():
    while True:
        var = True
        print("kaka")
        time.sleep(1)
        var = False
        # if not var:
        #     raise InterruptedError
        # sys.exit()

    

# some_d = {'timestamp': datetime.datetime(2023, 7, 31, 17, 51, 23), 'hostname': 'istvan-HP-ProBook-650-G1', 'appname': 'avahi-daemon', 'pid': '648', 'message': 'Interface enp0s25.IPv6 no longer relevant for mDNS.'}
# print(is_suspicious_tail(some_d))
# log_tailer()
x = threading.Thread(target=log_tailer())
x.start()
time.sleep(10)
sys.exit()