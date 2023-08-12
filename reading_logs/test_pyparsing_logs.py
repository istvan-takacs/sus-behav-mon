import unittest
from datetime import datetime
from pyparsing_logs import Parser, pyparse_logs, pyparse_tail_logs
from pyparsing import exceptions

class TestParser(unittest.TestCase):
    """
    Test class to verify Parser class functionality
    """

    def test_parse_valid_line(self):
        """
        Test method to verify parser object creates correct fields in the correct format
        """
        parser = Parser()
        # Example line is taken directly from syslog
        line = "Jun 18 13:05:56 istvan-HP-ProBook-650-G1 systemd[1]: Created slice User Slice of UID 128."
        expected_result = {
            "timestamp": datetime.strptime("Jun 18 13:05:56", "%b %d %H:%M:%S").replace(year=2023),
            "hostname": "istvan-HP-ProBook-650-G1",
            "appname": "systemd",
            "pid": "1",
            "message": "Created slice User Slice of UID 128."
        }
        self.assertEqual(parser.parse(line), expected_result)

    def test_parse_line_without_appname_pid(self):
        """
        Test method to verify parser object creates correct fields in the correct format even if that log is formatted differently
        """
        parser = Parser()
        line = "Jun 18 13:05:56 istvan-HP-ProBook-650-G1: Created slice User Slice of UID 128."
        expected_result = {
            "timestamp": datetime.strptime("Jun 18 13:05:56", "%b %d %H:%M:%S").replace(year=2023),
            "hostname": "istvan-HP-ProBook-650-G1",
            "appname": "",
            "pid": "",
            "message": "Created slice User Slice of UID 128."
        }
        self.assertEqual(parser.parse(line), expected_result)

    def test_pyparse_logs(self):
        """
        Test method to verify that all logs in the list are dictionaries
        """
        valid_logs = pyparse_logs()
        self.assertTrue(isinstance(valid_logs, list))
        for log in valid_logs:
            self.assertTrue(isinstance(log, dict))

    def test_pyparse_tail_logs_valid(self):
        """
        Test method to verify tailed logs are parsed correctly
        """
        log = "Jun 19 18:54:34 istvan-HP-ProBook-650-G1 gnome-shell[1815]: #0   56468fc5d148 i   resource:///org/gnome/shell/ui/messageTray.js:494 (1da469551ec0 @ 84)"
        expected_result = {
            "timestamp": datetime.strptime("Jun 19 18:54:34", "%b %d %H:%M:%S").replace(year=2023),
            "hostname": "istvan-HP-ProBook-650-G1",
            "appname": "gnome-shell",
            "pid": "1815",
            "message": "#0   56468fc5d148 i   resource:///org/gnome/shell/ui/messageTray.js:494 (1da469551ec0 @ 84)"
        }
        self.assertEqual(pyparse_tail_logs(log), expected_result)

    def test_pyparse_tail_logs_invalid(self):
        """
        Test method to verify that an exception is raised if the log is not parsed
        """
        invalid_log = "This is an invalid log"
        with self.assertRaises(exceptions.ParseException):
            pyparse_tail_logs(invalid_log)

if __name__ == "__main__":
    unittest.main()
