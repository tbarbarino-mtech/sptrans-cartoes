import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from typing import Optional

class MongoDBConnection:
    _client: Optional[AsyncIOMotorClient] = None

    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        if cls._client is None:
            # Recupera URI do ambiente; mantém fallback seguro para dev local
            mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            # Opcional: usuário/senha separados (se preferir)
            cls._client = AsyncIOMotorClient(mongo_uri)
        return cls._client

    @classmethod
    def get_collection(
        cls,
        db_name: str = None,
        collection_name: str = None
    ) -> AsyncIOMotorCollection:
        # Permite sobrescrever via variáveis de ambiente
        db_name = db_name or os.getenv("MONGODB_DB", "sptrans_db")
        collection_name = collection_name or os.getenv("MONGODB_COLLECTION", "cartoes")
        client = cls.get_client()
        return client[db_name][collection_name]