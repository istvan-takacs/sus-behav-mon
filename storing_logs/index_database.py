#!/usr/bin/env python3
import pymongo
import mongo_connect

# Get a client connection to the MongoDB database.
client = mongo_connect.get_client()

# Create a connection to the database.
db = client[mongo_connect.get_database_name()]

# Create a collection.
customers = db['Customers']

# Create an index to require unique names.
customers.create_index([('CustomerName', pymongo.ASCENDING)], unique=True)

# Create a document, which is a Python dictionary.
customer = {"CustomerId": "1",
            "CustomerName": "Barry Rayner"}

# Insert the document into the collection.
try:
    id = customers.insert_one(customer)
    print("Inserted: " + str(customer))
except pymongo.errors.DuplicateKeyError:
    print("Warning: could not insert the customer document.")
