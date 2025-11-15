from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URL"))
db = client["geo_db"]

property_collection = db["properties"]
