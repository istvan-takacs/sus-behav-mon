import unittest
import mongo_connect


class TestConnection(unittest.TestCase):

    def test_get_client(self):
        client = mongo_connect.get_client()
        self.assertIsNotNone(client)
    
    def test_get_database_name(self):
        db_name = mongo_connect.get_database_name()
        client = mongo_connect.get_client()

        self.assertEqual("logs", db_name)

        db_names = client.list_database_names()
        self.assertIn("logs", db_names)

if __name__ == "__main__":
    unittest.main()