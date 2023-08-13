import mongo_connect


def main():
    """
    Function to drop all databases used for system testing.
    """
    # Get a client connection to the MongoDB database.
    client = mongo_connect.get_client()

    # Drop the database.
    print(f"{mongo_connect.get_database_name()} database has been dropped")
    client.drop_database(mongo_connect.get_database_name())

if __name__ == "__main__":
    main()
