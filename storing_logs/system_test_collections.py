import mongo_connect


def main():
    """
    Function to conduct system testing on the collections.
    """
    client = mongo_connect.get_client()
    db_name = mongo_connect.get_database_name()
    db = client[db_name]
    print(f"Collections in database \"{db_name}\":") # logs
    clts = db.list_collection_names() # ['Logs', 'Alerts']
    print(clts)
    print(db[clts[0]].find_one({"_id": "1"})) # Collection logs contains at least one document
    print(db[clts[1]].find_one({"_id": "1"})) # Collection alerts contains at least one document
    
if __name__ == "__main__":
    main()
