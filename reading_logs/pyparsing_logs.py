from pyparsing import Word, alphas, Suppress, Combine, nums, string, Optional, Regex
from time import strftime

class Parser(object):
  def __init__(self):
    ints = Word(nums)

    # priority
    priority = Suppress("<") + ints + Suppress(">")

    # timestamp
    month = Word(string.ascii_uppercase , string.ascii_lowercase, exact=3)
    day   = ints
    hour  = Combine(ints + ":" + ints + ":" + ints)
    
    timestamp = month + day + hour

    # hostname
    hostname = Word(alphas + nums + "_" + "-" + ".")

    # appname
    appname = Word(alphas + "/" + "-" + "_" + ".") + Optional(Suppress("[") + ints + Suppress("]")) + Suppress(":")

    # message
    message = Regex(".*")
  
    # pattern build
    self.__pattern = priority + timestamp + hostname + appname + message
    
  def parse(self, line):
    parsed = self.__pattern.parseString(line)

    payload              = {}
    payload["priority"]  = parsed[0]
    payload["timestamp"] = strftime("%Y-%m-%d %H:%M:%S")
    payload["hostname"]  = parsed[4]
    payload["appname"]   = parsed[5]
    payload["pid"]       = parsed[6]
    payload["message"]   = parsed[7]
    
    return payload
  
def main():

    # parser = Parser()

    # with open('/home/istvan/Desktop/sus-behav-mon/reading_logs/syslog') as syslogFile:

    #     list1 = [] 
    #     for line in syslogFile:
    #         fields = parser.parse(line)
    #         list1.append(fields)

    #     return list1

  

  tests = """\
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 systemd[1]: rsyslog.service: Sent signal SIGHUP to main process 880 (rsyslogd) on client request.
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 systemd[1]: Started Disk Manager.
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 systemd[1]: logrotate.service: Deactivated successfully.
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 systemd[1]: Finished Rotate log files.
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 udisksd[892]: Cleaning up mount point /media/istvan/One Touch (device 8:17 is not mounted)
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 udisksd[892]: Acquired the name org.freedesktop.UDisks2 on the system message bus
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089955.8873] manager: (wlo1): new 802.11 Wi-Fi device (/org/freedesktop/NetworkManager/Devices/3)
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089955.8878] device (wlo1): state change: unmanaged -> unavailable (reason 'managed', sys-iface-state: 'external')"""



  from pprint import pprint
  for t in tests.splitlines():
      pprint(Parser().parse(t))
      print()
  



if __name__ == "__main__":

    main()