from pyparsing import Word, alphas, Suppress, Combine, nums, string, Regex, Optional
from datetime import datetime
from pyparsing import exceptions

class Parser(object):
    """"
    The code for this class is largely taken from...
    """
    # log lines don't include the year, but if we don't provide one, datetime.strptime will assume 1900
    ASSUMED_YEAR = '2023'

    def __init__(self):
        ints = Word(nums)

        # timestamp
        month = Word(string.ascii_uppercase, string.ascii_lowercase, exact=3)
        day   = ints
        hour  = Combine(ints + ":" + ints + ":" + ints)
        timestamp = month + day + hour
        
        # a parse action will convert this timestamp to a datetime
        timestamp.setParseAction(lambda t: datetime.strptime(Parser.ASSUMED_YEAR + ' ' + ' '.join(t), '%Y %b %d %H:%M:%S'))

        # hostname
        hostname = Word(alphas + nums + "_-.")

        # appname
        appname = (Word(alphas + "/-_.()1234567890@:]")("appname") + (Suppress("[") + ints("pid") + Suppress("]"))) | (Word(alphas + "/-_.1234567890@][")("appname"))
        appname.setName("appname")

        # message
        message = Regex(".*")

        # pattern build
        # (add results names to make it easier to access parsed fields)
        self._pattern = timestamp("timestamp") + hostname("hostname") + Optional(appname) + Suppress(':') + message("message")

    def parse(self, line):
        parsed = self._pattern.parseString(line)
        # fill in keys that might not have been found in the input string
        for key in 'appname pid'.split():
            if key not in parsed:
                parsed[key] = ''
        return parsed.asDict()
        
        parsed = Parsed(parsed)
        return parsed
    
    # Folders
    # - models.py - Dataclasses
    # - repository.py - Communication with the database
    # - service.py - General logic

    # @dataclass
    # class Parsed:
    #     timestamp: datetime
    #     hostname: Host
    #     appname: Appname
    #     pid: Optional[int]
    #     message: str

    # parsed = {'timestamp': datetime.datetime(2023, 8, 12, 10, 43, 42), 
    #           'hostname': 'raspberrypi', 
    #           'appname': 'systemd', 
    #           'pid': '1', 
    #           'message': 'Finished Cleanup of Temporary Directories.'}
  

def pyparse_logs():
  log_lines = []
  invalid_log_lines = []

  with open("/var/log/syslog", "r") as myfile:
      data_sys = myfile.read()
      parser = Parser()
      for line in data_sys.splitlines():
              try:
                log_dict = parser.parse(line)
                log_lines.append(log_dict)
              except exceptions.ParseException:
                 invalid_log_lines.append(line)         
  if len(invalid_log_lines) > 0:
     raise TypeError(f"Could not parse {len(invalid_log_lines)} items.")
  return log_lines

def pyparse_tail_logs(tail_log) -> dict:

  parser = Parser()
  try:
    log_dict = parser.parse(tail_log)
    return log_dict
  except:
    raise exceptions.ParseException(f"Could not parse this item: {tail_log}")


if __name__ == "__main__":
  pyparse_logs()