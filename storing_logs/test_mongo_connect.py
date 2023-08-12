import unittest
import mongo_connect


class TestConnection(unittest.TestCase):
    """
    Test class to verify functions in mongo_connect
    """

    def test_get_client(self):
        """
        Test function to verify client connection.
        """
        client = mongo_connect.get_client()
        self.assertIsNotNone(client)

    def test_get_database_name(self):
        """
        Test function to verify logs database
        """
        db_name = mongo_connect.get_database_name()
        client = mongo_connect.get_client()

        self.assertEqual("logs", db_name)

        db_names = client.list_database_names()
        self.assertIn("logs", db_names)

if __name__ == "__main__":
    unittest.main()
