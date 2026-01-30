import asyncio
from typing import List, Tuple
from pymongo import ASCENDING
from src.domain.entities.cartao import Cartao
from src.domain.enums.cartao_enums import SubtipoCartao, TipoCartao
from src.domain.repositories.icartao_repository import ICartaoRepository
from src.infrastructure.db.mongo_client import MongoDBConnection


class CartaoRepository(ICartaoRepository):
    def __init__(self, collection=None):
        if collection is not None:
            self.collection = collection
        else:
            self.collection = MongoDBConnection.get_collection()

    async def salvar(self, cartao: Cartao) -> None:
        doc = cartao.to_dict()
        await self.collection.update_one(
            {"cartao_numero": cartao.cartao_numero},
            {"$set": doc},
            upsert=True
        )

    async def criar_indices(self) -> None:
        await self.collection.create_index([("usuario_id", ASCENDING)], name="idx_usuario_cpf")
        await self.collection.create_index([("usuario_id", ASCENDING), ("cartao_numero", ASCENDING)], unique=True)
        await self.collection.create_index([("cartao_numero", ASCENDING)])
        await self.collection.create_index([("status", ASCENDING)])
        await self.collection.create_index([("dados_completos.titular_nome", ASCENDING)])

    async def buscar_por_filtros(self, cartao_numero=None, status=None, page: int = 1, limit: int = 10, **kwargs) -> List[Cartao]:
        query = {}
        if cartao_numero:
            query["cartao_numero"] = cartao_numero
        if status:
            query["status"] = status

        skip = (page - 1) * limit
        cursor = self.collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        return [
            Cartao(
                usuario_id=doc.get("usuario_id"),
                cartao_numero=doc.get("cartao_numero"),
                dados_completos=doc.get("dados_completos", {}),
                data_consulta=doc.get("data_consulta"),
                data_validade_cache=doc.get("data_validade_cache"),
                status=doc.get("status")
            )
            for doc in docs
        ]

    async def buscar_por_cpf_paginado(self, cpf: str, page: int = 1, limit: int = 10) -> Tuple[List[Cartao], int]:
        query = {"usuario_id": cpf}
        skip = (page - 1) * limit

        projection = {
            "usuario_id": 1,
            "cartao_numero": 1,
            "dados_completos": 1,
            "tipo_cartao": 1,
            "subtipo": 1,
            "status": 1,
            "data_consulta": 1,
            "data_validade_cache": 1
        }

        total_task = self.collection.count_documents(query)
        cursor_task = self.collection.find(query, projection).skip(skip).limit(limit).to_list(length=limit)

        total, docs = await asyncio.gather(total_task, cursor_task)

        items = []
        for doc in docs:
            tipo = None
            subtipo = None
            if doc.get("tipo_cartao"):
                try:
                    tipo = TipoCartao(doc["tipo_cartao"])
                except ValueError:
                    tipo = None
            if doc.get("subtipo"):
                try:
                    subtipo = SubtipoCartao(doc["subtipo"])
                except ValueError:
                    subtipo = None

            items.append(Cartao(
                usuario_id=doc.get("usuario_id"),
                cartao_numero=doc.get("cartao_numero"),
                dados_completos=doc.get("dados_completos", {}),
                tipo_cartao=tipo,
                subtipo=subtipo,
                data_consulta=doc.get("data_consulta"),
                data_validade_cache=doc.get("data_validade_cache"),
                status=doc.get("status")
            ))

        return items, int(total)