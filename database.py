from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Direct connection string
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://sumitup:sumitup345@fyp-cluster.x0opo1n.mongodb.net/fypdb?retryWrites=true&w=majority")

try:
    # Set serverSelectionTimeoutMS to avoid hanging
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Test connection
    client.admin.command('ping')
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    raise

db = client["fypdb"]

videos_collection = db["videos"]
transcripts_collection = db["transcripts"]
users_collection = db["users"]