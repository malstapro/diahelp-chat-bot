from pymongo import MongoClient

class DataBase(dict):
    def __init__(self,database,collection,connection=None,base_key='_id'):
        self.client = MongoClient(connection)
        self.db = self.client[database]
        self.collection = self.db[collection]
        self.base_key = base_key
