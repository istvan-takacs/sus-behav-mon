#!/usr/bin/env python3
import mongo_connect

"""
A program to test the connection settings for the
MongoDB server.
"""
client = mongo_connect.get_client()
if client is not None:
    print('\033[92m' + "Successfully connected to MongoDB server." + '\033[0m')
else:
    print('\033[91m' + "Failed to connect to MongoDB server." + '\033[0m')
