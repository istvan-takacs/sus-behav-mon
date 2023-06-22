from pyparsing import Word, alphas, Suppress, Combine, nums, string, Optional, Regex
from time import strftime

class Parser(object):
  def __init__(self):
    ints = Word(nums)

    # priority
    # priority = Suppress("<") + ints + Suppress(">")

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
    self.__pattern = timestamp + hostname + appname + message
    
  def parse(self, line):
    parsed = self.__pattern.parseString(line)
  

    payload              = {}
    # payload["priority"]  = parsed[0]
    payload["timestamp"] = strftime("%Y-%m-%d %H:%M:%S")
    payload["hostname"]  = parsed[3]
    payload["appname"]   = parsed[4]
    payload["pid"]       = parsed[5]
    payload["message"]   = parsed[6]
    
    return payload
  
def main():

    parser = Parser()



    # with open('/home/istvan/Desktop/sus-behav-mon/reading_logs/syslog') as syslogFile:
    #     list1 = [] 
    #     for line in syslogFile:
    #         # fields = parser.parse(line)
    #         list1.append(line)

    #     print(list1)


  

    tests = """\
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 systemd[1]: rsyslog.service: Sent signal SIGHUP to main process 880 (rsyslogd) on client request.
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 systemd[1]: Started Disk Manager.
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 systemd[1]: logrotate.service: Deactivated successfully.
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 systemd[1]: Finished Rotate log files.
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 udisksd[892]: Cleaning up mount point /media/istvan/One Touch (device 8:17 is not mounted)
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 udisksd[892]: Acquired the name org.freedesktop.UDisks2 on the system message bus
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089955.8873] manager: (wlo1): new 802.11 Wi-Fi device (/org/freedesktop/NetworkManager/Devices/3)
Jun 18 13:05:55 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089955.8878] device (wlo1): state change: unmanaged -> unavailable (reason 'managed', sys-iface-state: 'external')
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9144] policy: auto-activating connection 'VM3708122' (d0b49084-e343-40b6-a00f-8b57b2b4629b)
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9154] device (wlo1): Activation: starting connection 'VM3708122' (d0b49084-e343-40b6-a00f-8b57b2b4629b)
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9158] device (wlo1): state change: disconnected -> prepare (reason 'none', sys-iface-state: 'managed')
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9166] manager: NetworkManager state is now CONNECTING
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9175] device (wlo1): state change: prepare -> config (reason 'none', sys-iface-state: 'managed')
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9185] device (wlo1): Activation: (wifi) access point 'VM3708122' has security, but secrets are required.
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9188] device (wlo1): state change: config -> need-auth (reason 'none', sys-iface-state: 'managed')
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9195] sup-iface[9c817ac5d0e16f8c,0,wlo1]: wps: type pbc start...
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9214] device (wlo1): state change: need-auth -> prepare (reason 'none', sys-iface-state: 'managed')
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9226] device (wlo1): state change: prepare -> config (reason 'none', sys-iface-state: 'managed')
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9233] device (wlo1): Activation: (wifi) connection 'VM3708122' has security, and secrets exist.  No new secrets needed.
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9237] Config: added 'ssid' value 'VM3708122'
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9241] Config: added 'scan_ssid' value '1'
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9243] Config: added 'bgscan' value 'simple:30:-70:86400'
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 wpa_supplicant[895]: wlo1: WPS-CANCEL 
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9246] Config: added 'key_mgmt' value 'WPA-PSK WPA-PSK-SHA256'
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9247] Config: added 'auth_alg' value 'OPEN'
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9247] Config: added 'psk' value '<hidden>'
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 wpa_supplicant[895]: wlo1: Trying to associate with 48:d3:43:d6:fd:57 (SSID='VM3708122' freq=5220 MHz)
Jun 18 13:06:00 istvan-HP-ProBook-650-G1 NetworkManager[894]: <info>  [1687089960.9496] device (wlo1): supplicant interface state: disconnected -> associating
Jun 18 13:06:01 istvan-HP-ProBook-650-G1 dbus-daemon[862]: [system] Successfully activated service 'net.reactivated.Fprint'"""


    from pprint import pprint
    for t in tests.splitlines():
      pprint(Parser().parse(t))
      print()
  



if __name__ == "__main__":

    main()