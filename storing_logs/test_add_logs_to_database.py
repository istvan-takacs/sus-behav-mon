import pymongo
import unittest
from add_logs_to_database import get_collection, insert_into_collection, set_logs_collection, get_logs_collection, set_alerts_collection
from reading_logs.all_logs import get_logs



class TestDatabaseFunctions(unittest.TestCase):
    """
    Test class to verify logs database functions
    """

    def test_get_collection(self):
        """
        Test method to verify get_collection function
        """

        test_clt = get_collection("test")
        self.assertIsInstance(test_clt, pymongo.collection.Collection)
        test_clt.drop()

    def test_insert_into_collection(self):
        """
        Test method to verify insert_into collection function
        """

        test_clt = get_collection("test")
        objs_to_add = [{"_id": 1, "field2": "value2"},
                       {"_id": 2, "field2": "value2"},
                       {"_id": 2, "field2": "value3"}]
        # Insert custom documents into the test collection
        insert_into_collection(objs_to_add, "test")

        # Keeping track of the elements that have been added
        # adding only the elements that have not been added and updating the fields of the rest
        elements = []
        added = []
        idx = -1
        for i in objs_to_add:
            if i["_id"] not in added:
                elements.append(i)
                added.append(i["_id"] )
                idx += 1
            else:
                elements[idx] = i

        cursor = test_clt.find({})
        # Asserting that the test collection and the list have been updated correctly
        self.assertEqual(list(cursor), elements)
        test_clt.drop()

    def test_set_logs_collection(self):
        """
        Test method verifying set_logs_collection function
        """

        test_clt = get_collection("test")
        # Loads all of the syslog data into the test collection
        set_logs_collection(clt="test")

        cursor = test_clt.find({})
        # Asserting that the test collection contains all the logs
        self.assertEqual(list(cursor), get_logs())
        test_clt.drop()

    def test_set_alerts_collection(self):
        """
        Test method to verify set_alerts_collection
        """

        test_clt = get_collection("test")
        objs_to_add = [
            {"_id": 1, "field2": "value2"},
            {"_id": 2, "field2": "value2"},
            {"_id": 2, "field2": "value3"}
        ]
        # Inserting custom documents into the test collection
        set_alerts_collection(objs_to_add, "test")

        # Keeping track of the elements that have been added
        # adding only the elements that have not been added and updating the fields of the rest
        elements = []
        added = set()
        idx = -1
        for i in objs_to_add:
            # Add field "identified" to all documents and setting it to False
            new_dict = {**i, "identified": False}
            if i["_id"] not in added:  
                elements.append(new_dict)
                added.add(i["_id"])
            else:
                elements[idx] = new_dict

        cursor = test_clt.find({})
        # Asserting that the test collection contains all the logs
        self.assertEqual(list(cursor), elements)
        test_clt.drop()


    def test_get_logs_collection(self):
        """
        Test method to verify get_logs_collection function
        """
        # Get collection
        test_clt = get_collection("test")
        result = get_logs_collection("test")

        self.assertIsInstance(result, list)
        # Drop collection
        test_clt.drop()

if __name__ == '__main__':
    unittest.main()
