from pymongo import MongoClient
from config import MONGO_URI
from config import DATABASE_NAME


mongo_client = MongoClient(MONGO_URI)
jirapoker_db = mongo_client[DATABASE_NAME]