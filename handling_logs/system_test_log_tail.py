from check_log import log_tailer
import threading
import queue
import syslog
import time

def main():
    """
    Function to system test tailing the log file with subprocess
    """
    syslog.syslog("Sending a message to be logged")

if __name__ == "__main__":
  main()