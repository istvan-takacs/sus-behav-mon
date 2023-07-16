#!/usr/bin/env python3
import mongo_connect
import pprint

"""
A program to list the collections that are available in the
specified database.
"""
client = mongo_connect.get_client()
if client is not None:
    db_name = mongo_connect.get_database_name()
    db = client[db_name]
    print(f"Collections in database \"{db_name}\":")
    pprint.pprint(db.list_collection_names())
