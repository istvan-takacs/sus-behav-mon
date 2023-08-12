import unittest
import all_logs
from datetime import datetime
import pyparsing_logs
import pyparsing_logs_network

class TestParseAllLogs(unittest.TestCase):
    """
    Test class to verify the function all_logs
    """

    def test_get_all_logs(self):
        """
        Test method to verify the function get_all_logs 
        """
        # Load in all logs from all sources
        logs = all_logs.get_logs()
        log_main = pyparsing_logs.pyparse_logs()
        log_network = pyparsing_logs_network.pyparse_logs()

        # Assert that the length of the concatenated logs equal the sum of the parts
        self.assertEqual(len(logs), len(log_main+log_network))
        self.assertTrue(isinstance(logs, list))
        for log in logs:
            # Assert the type of the logs as well as some of the fields
            self.assertTrue(isinstance(log, dict))
            self.assertTrue(isinstance(log["_id"], str))
            self.assertTrue(isinstance(log["timestamp"], datetime))


if __name__ == "__main__":
    unittest.main()