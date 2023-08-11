import unittest
from datetime import datetime
from pyparsing_logs_network import Parser, pyparse_logs
from pyparsing import exceptions

class TestParser(unittest.TestCase):


    def test_parse_valid_line(self):
        self.parser = Parser()
        # Example line is taken directly from syslog
        line = "2023-07-07T13:05:29+01:00 raspberrypi systemd[1]: Stopping Light Display Manager..."
        expected_result = {
            "timestamp": "2023-07-0713:05:29",
            "hostname": "raspberrypi",
            "appname": "systemd",
            "pid": "1",
            "message": "Stopping Light Display Manager..."
        }
        self.assertEqual(self.parser.parse(line), expected_result)

    def test_parse_line_without_appname_pid(self):
        self.parser = Parser()
        # Example line is taken directly from syslog
        line = "2023-07-07T13:05:29+01:00 raspberrypi: Stopping Light Display Manager..."
        expected_result = {
            "timestamp": "2023-07-0713:05:29",
            "hostname": "raspberrypi",
            "appname": "",
            "pid": "",
            "message": "Stopping Light Display Manager..."
        }
        self.assertEqual(self.parser.parse(line), expected_result)

    def test_pyparse_logs(self):
        valid_logs = pyparse_logs()
        self.assertTrue(isinstance(valid_logs, list))
        for log in valid_logs:
            self.assertTrue(isinstance(log, dict))
            self.assertTrue(isinstance(log["timestamp"], datetime))
        

if __name__ == "__main__":
    unittest.main()
