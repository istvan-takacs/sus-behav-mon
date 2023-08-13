from pyparsing import Word, alphas, Suppress, Combine, nums, Regex, Optional, exceptions
from datetime import datetime


class Parser(object):
    """
    A Parser class to define a parsing pattern by which the sytem logs can be parsed that are in different formats

    The code for this Parser class is inspired by Leandro Silva and is available at https://gist.github.com/leandrosilva/3651640 last accessed on 12/08/2023
    """
    # Log lines don't include the year, but datetime.strptime will assume 1900 by default
    ASSUMED_YEAR = '2023'

    def __init__(self):
      ints = Word(nums)

      # Timestamp
      timestamp = Combine(ints + '-' + ints + '-' + ints + Suppress('T') + ints + ':' + ints + ':' + ints + Suppress('+' + Word(nums) + ':' + Word(nums)))
      
      # Hostname
      hostname = Word(alphas + nums + "_-.")

      # Appname
      appname = (Word(alphas + "/-_.()1234567890@:=]")("appname") + (Suppress("[") + ints("pid") + Suppress("]"))) | (Word(alphas + "/-_.()1234567890@=[")("appname"))
      appname.setName("appname")

      # Message
      message = Regex(".*")

      # Pattern build
      self._pattern = timestamp("timestamp") + hostname("hostname") + Optional(appname) + Suppress(':') + message("message")

    def parse(self, line):
        """
        Method to apply the parsing pattern to the passed in object and output them in a dictionary
        """
        parsed = self._pattern.parseString(line)
        # Fill in keys that might not have been found in the input string
        for key in ['appname', 'pid', 'message']:
            if key not in parsed:
                parsed[key] = ''
        return parsed.asDict()


def pyparse_logs():
  """
  Function to parse log lines from the server found under directory /var/log/raspberrypi
  """
  valid_log_lines = []
  invalid_log_lines = []
  
  with open("/var/log/raspberrypi/syslog.log", "r") as myfile:
      data_rb = myfile.read()
      parser = Parser()
      for line in data_rb.splitlines():
              # If the line could be parsed, append them to the list
              try:
                log_dict = parser.parse(line)
                valid_log_lines.append(log_dict)
              # If the line could not be parsed, append it to the invalid_log_lines list
              except exceptions.ParseException:
                invalid_log_lines.append(line)  
      # Convert the timestamp into a datetime format      
      for line in valid_log_lines:
            line["timestamp"] = datetime.strptime(line["timestamp"], "%Y-%m-%d%H:%M:%S")
  # If there are items that were not parsed raise a TypeError
  if len(invalid_log_lines) > 0:
     raise TypeError(f"Could not parse {len(invalid_log_lines)} items.")
  return valid_log_lines # Return the parsed dictionaries in a list
