from pyparsing import Word, alphas, Suppress, Combine, nums, string, Regex, Optional
from datetime import datetime
from pyparsing import exceptions

class Parser(object):
    """"
    A Parser class to define a parsing pattern by which the sytem logs can be parsed

    The code for this Parser class is inspired by Leandro Silva and is available at https://gist.github.com/leandrosilva/3651640 last accessed on 12/08/2023
    """
    # Log lines don't include the year, but datetime.strptime will assume 1900 by default
    ASSUMED_YEAR = '2023'

    def __init__(self):
        ints = Word(nums)

        # Timestamp
        month = Word(string.ascii_uppercase, string.ascii_lowercase, exact=3)
        day   = ints
        hour  = Combine(ints + ":" + ints + ":" + ints)
        timestamp = month + day + hour
        
        # A parse action will convert this timestamp to a datetime
        timestamp.setParseAction(lambda t: datetime.strptime(Parser.ASSUMED_YEAR + ' ' + ' '.join(t), '%Y %b %d %H:%M:%S'))

        # Hostname
        hostname = Word(alphas + nums + "_-.")

        # Appname
        appname = (Word(alphas + "/-_.()1234567890@:]")("appname") + (Suppress("[") + ints("pid") + Suppress("]"))) | (Word(alphas + "/-_.1234567890@][")("appname"))
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
        for key in 'appname pid'.split():
            if key not in parsed:
                parsed[key] = ''
        return parsed.asDict()



def pyparse_logs():
  """
  Function to parse log lines found in the default directory /var/log/syslog
  """
  log_lines = []
  invalid_log_lines = []

  with open("/var/log/syslog", "r") as myfile:
      data_sys = myfile.read()
      parser = Parser()
      for line in data_sys.splitlines():
              # If the line could be parsed, append them to the list
              try:
                log_dict = parser.parse(line)
                log_lines.append(log_dict)
              # If the line could not be parsed, append it to the invalid_log_lines list
              except exceptions.ParseException:
                 invalid_log_lines.append(line)         
  # If there are items that were not parsed raise a TypeError
  if len(invalid_log_lines) > 0:
     raise TypeError(f"Could not parse {len(invalid_log_lines)} items.")
  return log_lines # Return the parsed dictionaries in a list

def pyparse_tail_logs(tail_log) -> dict:
  """
  Function to parse the passed in tailed log line
  """
  parser = Parser()
  try:
    log_dict = parser.parse(tail_log)
    return log_dict
  except:
    raise exceptions.ParseException(f"Could not parse this item: {tail_log}")
