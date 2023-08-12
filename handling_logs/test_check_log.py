import unittest
import threading
import queue
from unittest.mock import patch, Mock
from datetime import datetime
import check_log
from handling_logs import get_all_services
from add_logs_to_database import get_logs_collection, get_collection

class TestCheckLog(unittest.TestCase):
    """
    Test class to verify check_log functionality
    """

    def setUp(self):
        """
        Defining the event that is going to be called to stop the thread
        """
        self.some_event = threading.Event()
        self.some_event.clear()

    def tearDown(self):
        """
        Set the event so that the thread is terminated
        """
        self.some_event.set()

    def test_log_tailer_with_threshold(self):
        """
        Test method to verify log_tailer functionality by providing a high threshold value
        """
        # Initialising variables
        some_queue = queue.Queue() # The tailed logs are to be put in the some_queue object
        threshold = 1.1
        app_list = []

        # Instantiate and start the Thread object targeting the log_tailer function
        x = threading.Thread(target=check_log.log_tailer, args=(some_queue, self.some_event, app_list, threshold,))
        x.start()

        # Putting the tailes log in the queue
        tailed_log = some_queue.get()
        # Setting the event terminating the thread
        self.some_event.set()

        # Assert that the tailed logs are correctly parsed and the alert is set to True
        self.assertIsInstance(tailed_log, dict)
        keys = sorted(["timestamp", "hostname", "appname",
                "message", "pid", "alert", "probability"])
        keys1 = sorted(list(tailed_log.keys()))
        self.assertIn("timestamp", tailed_log)
        self.assertListEqual(keys, keys1)
        self.assertEqual(tailed_log.get("alert"), True) # Because the threshold is set so high

    def test_log_tailer_with_app_list(self):
        """
        Test method to verify log_tailer functionality by blacklisting all the services
        """
        # Initialising variables
        some_queue = queue.Queue() # The tailed logs are to be put in the some_queue object
        app_list = get_all_services() 
        threshold = 0.

        # Instantiate and start the Thread object targeting the log_tailer function
        x = threading.Thread(target=check_log.log_tailer, args=(some_queue, self.some_event, app_list, threshold,))
        x.start()

        # Putting the tailes log in the queue
        tailed_log = some_queue.get()
        # Setting the event terminating the thread
        self.some_event.set()

        # Assert that the tailed logs are correctly parsed and the alert is set to True
        self.assertIsInstance(tailed_log, dict)
        keys = sorted(["timestamp", "hostname", "appname",
                "message", "pid", "alert", "probability"])
        keys1 = sorted(list(tailed_log.keys()))
        self.assertIn("timestamp", tailed_log)
        self.assertListEqual(keys, keys1)
        # Because all the services in the collection have been passed in as suspicious
        self.assertEqual(tailed_log.get("alert"), True)

    @patch("add_logs_to_database.get_logs_collection")
    def test_suspicious(self, mock_get_log_collection):
        """
        Test method to verify that the function suspicious returns the correct probability
        """
        parsed_log = {'timestamp': datetime(2023, 7, 12, 1, 33, 32), 'hostname': 'istvan-HP-ProBook-650-G1', 'appname': 'some_random_app', 'pid': '22339', 'message': 'Anacron 2.3 started on 2023-08-12'}

        mock_table = {'_id': '204', 'appname': 'some_random_app', 'hostname': 'istvan-HP-ProBook-650-G1', 'identified': False,
                'probability': {'Interval 1': 0, 'Interval 2': 1.3333333333333333, 'Interval 3': 0.6666666666666666, 'Interval 4': 2.0, 'Interval 5': 3.0,
                                '0': 0.0, '1': 0.0, '2': 0.0, '3': 0.0, '4': 0.0, '5': 0.0, '6': 0.0, '7': 0.0, '8': 0.0, '9': 0.0, 
                                '10': 0.3333333333333333, '11': 0.0, '12': 0.6666666666666666, '13': 0.0, '14': 0.0, '15': 0.0, '16': 0.0, '17': 0.0, 
                                '18': 0.0, '19': 0.0, '20': 0.0, '21': 0.0, '22': 0.0, '23': 0.0}}

        mock_get_log_collection.return_value = mock_table
        float_value = check_log.suspicious(parsed_log) 
        self.assertEqual(float_value, 0)

    def test_is_identified(self):
        """
        Test method to verify that function is_identified returns the correct value
        """
        # Define parsed object in a way where it will return False
        parsed_obj = {'timestamp': datetime(2023, 7, 12, 1, 33, 32), 'hostname': 'new_host', 'appname': 'some_random_app', 'pid': '22339', 'message': 'Anacron 2.3 started on 2023-08-12'}
        boolean = check_log.is_identified(parsed_obj)
        self.assertIsInstance(boolean, bool)
        self.assertFalse(boolean)
        
if __name__ == '__main__':
    unittest.main()
