import unittest
import all_logs
from datetime import datetime
import pyparsing_logs
import pyparsing_logs_network

class TestParseAllLogs(unittest.TestCase):


    def test_get_all_logs(self):
        logs = all_logs.get_logs()
        log_main = pyparsing_logs.pyparse_logs()
        log_network = pyparsing_logs_network.pyparse_logs()
        
        self.assertEqual(len(logs), len(log_main+log_network))
        self.assertTrue(isinstance(logs, list))
        for log in logs:
            self.assertTrue(isinstance(log, dict))
            self.assertTrue(isinstance(log["_id"], str))
            self.assertTrue(isinstance(log["timestamp"], datetime))


if __name__ == "__main__":
    unittest.main()