import unittest
from add_logs_to_database import get_collection, insert_into_collection, set_logs_collection, get_logs_collection
import sys
sys.path.insert(0, '/home/istvan/Desktop/sus-behav-mon/reading_logs')
from all_logs import get_logs
import pymongo

class TestMongoFunctions(unittest.TestCase):

    def test_get_collection(self):

        test_clt = get_collection("test")
        self.assertIsInstance(test_clt, pymongo.collection.Collection)
        test_clt.drop()
    
    def test_insert_into_collection(self):

        test_clt = get_collection("test")
        objs_to_add = [{"_id": 1, "field2": "value2"},
                       {"_id": 2, "field2": "value2"},
                       {"_id": 2, "field2": "value3"}]
        insert_into_collection(objs_to_add, "test")
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
        self.assertEqual(list(cursor), elements)
        test_clt.drop()

    def test_set_logs_collection(self):
        
        test_clt = get_collection("test")
        set_logs_collection(clt="test")

        cursor = test_clt.find({})
        self.assertEqual(list(cursor), get_logs())
        test_clt.drop()

    def test_get_logs_collection(self):
        
        test_clt = get_collection("test")
        result = get_logs_collection("test")

        self.assertIsInstance(result, list)
        test_clt.drop()
        
    
if __name__ == '__main__':
    unittest.main()
