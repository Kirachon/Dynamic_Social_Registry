from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

async def liveness_check():
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=1000)
    client.admin.command('ping')

async def readiness_check():
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=1000)
    client.admin.command('ping')

