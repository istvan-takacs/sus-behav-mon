from datetime import time
import unittest
import handling_logs
from unittest.mock import patch
from storing_logs.add_logs_to_database import get_logs_collection
import pandas as pd


class TestHandlingLogs(unittest.TestCase):
    """
    Test class to test functions in handling_logs
    """
    def test_get_all_services(self):
        """
        Test method to test get_all_services returns all appnames in collection
        """
        appnames = handling_logs.get_all_services()
        self.assertIsInstance(appnames, list)
    

    def test_hist_maker(self):
        """
        Test method for hist_maker function providing a dictionary of probabilities in certain hours and intervals
        """
        # Create a DataFrame for testing where the host calls the same service at the same time
        data = {
            "hostname": ["raspberrypi"] * 24,
            "appname": ["systemd"] * 24,
            "time": [time(16, 12, 33)]*24
            }
        df = pd.DataFrame(data)
        # Creating a histogram with 5 bins
        result = handling_logs.hist_maker(host="raspberrypi", app="systemd", df=df, number_of_bins=5)
        # Since systemd is being called at 4pm only Interval 3, and 16 should be non zero (1)
        expected_result = {
            "Interval 1": 0,
            "Interval 2": 0,
            "Interval 3": 1,
            "Interval 4": 0,
            "Interval 5": 0,
            "0": 0,
            "1": 0,
            "2": 0,
            "3": 0,
            "4": 0,
            "5": 0,
            "6": 0,
            "7": 0,
            "8": 0,
            "9": 0,
            "10": 0,
            "11": 0,
            "12": 0,
            "13": 0,
            "14": 0,
            "15": 0,
            "16": 1,
            "17": 0,
            "18": 0,
            "19": 0,
            "20": 0,
            "21": 0,
            "22": 0,
            "23": 0,
        }

        self.assertEqual(result, expected_result)

    @patch("add_logs_to_database.get_logs_collection")
    @patch("handling_logs.hist_maker")
    def test_create_alerts(self, mock_hist_maker, mock_get_logs_collection):
        """
        Test method to verify create_alerts creating the alerts in the correct format
        """
        # Mock data and functions
        mock_df = pd.DataFrame({
            "hostname": ["host1", "raspberrypi"],
            "appname": ["systemd", "app2"],
            "timestamp": [pd.Timestamp("2023-08-01 10:00:00"), pd.Timestamp("2023-08-01 11:00:00")]})
        mock_get_logs_collection.return_value = mock_df
        mock_hist_maker.return_value = {0: 0.1, 1: 0.2, 2: 0.3, 3: 0.4}

        # Call the function
        alerts = handling_logs.create_alerts()

        # Expected  results
        expected_alerts = [
            {"_id": "1", "hostname": "host1", "appname": "systemd", "probability": {0: 0.1, 1: 0.2, 2: 0.3, 3: 0.4}},
            {"_id": "2", "hostname": "host1", "appname": "app2", "probability": {0: 0.1, 1: 0.2, 2: 0.3, 3: 0.4}},
            {"_id": "3", "hostname": "raspberrypi", "appname": "systemd", "probability": {0: 0.1, 1: 0.2, 2: 0.3, 3: 0.4}},
            {"_id": "4", "hostname": "raspberrypi", "appname": "app2", "probability": {0: 0.1, 1: 0.2, 2: 0.3, 3: 0.4}},
        ]
        # Asserting the expected results match the function output
        self.assertEqual(alerts, expected_alerts)
        # Assertigng that the mock functions have been called
        mock_get_logs_collection.assert_called_once()
        self.assertEqual(mock_hist_maker.call_count, 4)



if __name__ == "__main__":
    unittest.main()