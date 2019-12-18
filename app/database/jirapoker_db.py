from pymongo import MongoClient
import config


mongo_client = MongoClient(config.MONGO_URI)
jirapoker_db = mongo_client[config.DATABASE_NAME]