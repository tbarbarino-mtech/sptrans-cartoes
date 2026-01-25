from pymongo import MongoClient
from src.config.settings import settings

class MongoDBConnection:
    _client = None

    @classmethod
    def get_collection(cls):
        if cls._client is None:
            cls._client = MongoClient(settings.MONGO_URI)
        return cls._client[settings.DB_NAME][settings.COLLECTION_NAME]