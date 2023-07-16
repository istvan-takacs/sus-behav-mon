#!/usr/bin/env python3
import mongo_connect

# Get a client connection to the MongoDB database.
client = mongo_connect.get_client()

# Drop the database.
client.drop_database(mongo_connect.get_database_name())
