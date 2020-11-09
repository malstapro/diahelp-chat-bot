from pymongo import MongoClient

client = MongoClient('localhost', 27017)

# Connect to our database
db = client['testDB']

# Fetch our series collection
series_collection = db['test']