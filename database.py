import pymongo

class DataBase(dict):
    def __init__(self, db_name, collection_name, connect_string=None, base_key='id'):
        self.db_client = pymongo.MongoClient(connect_string)
        self.database = self.db_client[db_name]
        self.collection = self.database[collection_name]

        self.base_key = base_key
        self.load()

        # return self

    def load(self, q={}):
        upd = {item[self.base_key]: MongoItem(item, self.collection, self.base_key) for item in
               self.collection.find({})}
        # print(upd)
        self.update(upd)

    def __setitem__(self, k, v):
        v[self.base_key] = k
        if k in self:
            v = MongoItem(v, self.collection, self.base_key)
            self[k].update(v)
        else:
            self.update({k: MongoItem(v, self.collection, self.base_key)})


class MongoItem(dict):
    def __init__(self, content, collection, base_key):
        self.collection = collection
        self.base_key = base_key
        self.update(content)

    def save(self):
        self.collection.update_one({self.base_key: self[self.base_key]}, {'$set': self}, upsert=True)

    def delete_user(self):
        self.collection.delete_one({self.base_key: self[self.base_key]})

    def load(self):
        self.update(self.collection.find_one({self.base_key: self[self.base_key]}))
