from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI not set in environment")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")

db = client["fypdb"]

videos_collection = db["videos"]
transcripts_collection = db["transcripts"]
users_collection = db["users"]
