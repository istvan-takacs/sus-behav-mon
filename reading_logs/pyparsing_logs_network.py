from pyparsing import Word, alphas, Suppress, Combine, nums, string, Regex, Optional
from datetime import datetime

class Parser(object):
    ASSUMED_YEAR = '2023'

    def __init__(self):
        ints = Word(nums)

        timestamp = Combine(ints + '-' + ints + '-' + ints + Suppress('T') + ints + ':' + ints + ':' + ints + Suppress('+' + Word(nums) + ':' + Word(nums)))
        
        hostname = Word(alphas + nums + "_-.")

        appname = (Word(alphas + "/-_.()1234567890@:=]")("appname") + (Suppress("[") + ints("pid") + Suppress("]"))) | (Word(alphas + "/-_.()1234567890@=[")("appname"))
        appname.setName("appname")

        message = Regex(".*")

        self._pattern = timestamp("timestamp") + hostname("hostname") + Optional(appname) + Suppress(':') + message("message")

    def parse(self, line):
        parsed = self._pattern.parseString(line)
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
              except:
                invalid_log_lines.append(line)  
              else:
                valid_log_lines.append(log_dict)
      for line in valid_log_lines:
            line["timestamp"] = datetime.strptime(line["timestamp"], "%Y-%m-%d%H:%M:%S")
  
  i = 1              
  for d in valid_log_lines:
      d["index"] = i
      i += 1

  return valid_log_lines

if __name__ == "__main__":
    pyparse_logs()


