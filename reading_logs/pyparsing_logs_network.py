from pyparsing import Word, alphas, Suppress, Combine, nums, Regex, Optional, exceptions
from datetime import datetime


class Parser(object):
    """
    The class is largely taken from...
    """
    # log lines don't include the year, but if we don't provide one, datetime.strptime will assume 1900
    ASSUMED_YEAR = '2023'

    def __init__(self):
      ints = Word(nums)

      # timestamp
      timestamp = Combine(ints + '-' + ints + '-' + ints + Suppress('T') + ints + ':' + ints + ':' + ints + Suppress('+' + Word(nums) + ':' + Word(nums)))
      
      # hostname
      hostname = Word(alphas + nums + "_-.")

      # appname
      appname = (Word(alphas + "/-_.()1234567890@:=]")("appname") + (Suppress("[") + ints("pid") + Suppress("]"))) | (Word(alphas + "/-_.()1234567890@=[")("appname"))
      appname.setName("appname")

      # message
      message = Regex(".*")

      # pattern build
      # (add results names to make it easier to access parsed fields)
      self._pattern = timestamp("timestamp") + hostname("hostname") + Optional(appname) + Suppress(':') + message("message")

    def parse(self, line):
        parsed = self._pattern.parseString(line)
        # fill in keys that might not have been found in the input string
        for key in ['appname', 'pid', 'message']:
            if key not in parsed:
                parsed[key] = ''
        return parsed.asDict()


def pyparse_logs():
  valid_log_lines = []
  invalid_log_lines = []
  
  with open("/var/log/raspberrypi/syslog.log", "r") as myfile:
      data_rb = myfile.read()
      parser = Parser()
      for line in data_rb.splitlines():
              try:
                log_dict = parser.parse(line)
                valid_log_lines.append(log_dict)
              except exceptions.ParseException:
                invalid_log_lines.append(line)        
      for line in valid_log_lines:
            line["timestamp"] = datetime.strptime(line["timestamp"], "%Y-%m-%d%H:%M:%S")
  if len(invalid_log_lines) > 0:
     raise TypeError(f"Could not parse {len(invalid_log_lines)} items.")
  return valid_log_lines

if __name__ == "__main__":
    print(pyparse_logs())


