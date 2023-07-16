#!/usr/bin/env python3
import mongo_connect
import pprint

"""
A program to list the databases that are available in the
MongoDB server.
"""
client = mongo_connect.get_client()
if client is not None:
    print("Databases:")
    pprint.pprint(client.list_database_names())
