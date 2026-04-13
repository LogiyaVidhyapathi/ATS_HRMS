from pymongo import MongoClient
from app.core.config import settings

client = MongoClient(settings.MONGO_URI)

db = client[settings.database_name]

interviews = db['interviews']
reports = db['transcripts']
