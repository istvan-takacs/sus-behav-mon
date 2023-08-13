import mongo_connect


def main():
    """
    Function to drop all collections used for system testing.
    """
    # Get a client connection to the MongoDB database
    client = mongo_connect.get_client()

    # Create a connection to the database
    db = client[mongo_connect.get_database_name()]

    # Drop all collections from the database
    for collection_name in db.list_collection_names():
        db[collection_name].drop()
        print(f"{collection_name} collection has been dropped.")

if __name__ == "__main__":
    main()
