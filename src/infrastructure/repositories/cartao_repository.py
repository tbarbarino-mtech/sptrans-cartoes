from typing import List, Optional
from datetime import datetime
from pymongo import ASCENDING
from src.domain.entities.cartao import Cartao
from src.domain.repositories.icartao_repository import ICartaoRepository
from src.infrastructure.db.mongo_client import MongoDBConnection

class CartaoRepository(ICartaoRepository):
    def __init__(self, collection=None):
        if collection is not None:
            self.collection = collection
        else:
            self.collection = MongoDBConnection.get_collection()
            
    def salvar(self, cartao: Cartao) -> None:
        # 1. Converte o objeto para dicionário (usando o método que você criou na entidade)
        doc = cartao.to_dict()
        
        # 2. Executa o Update com Upsert
        # AJUSTE: Mudei de 'cartao.numero' para 'cartao.cartao_numero'
        self.collection.update_one(
            {"cartao_numero": cartao.cartao_numero}, 
            {"$set": doc}, 
            upsert=True
        )

    def criar_indices(self) -> None:
        # 1. Índice Composto (Seção 3.7): Otimiza busca por dono + cartão
        self.collection.create_index([("usuario_id", 1), ("cartao_numero", 1)], unique=True)
        
        # 2. Índice Simples (Performance): Otimiza busca direta apenas pelo número
        # Necessário para o assert "cartao_numero_1" passar no teste
        self.collection.create_index([("cartao_numero", 1)])

        # 3. Índices de Cache e Operação
        self.collection.create_index([("data_validade_cache", 1)])
        self.collection.create_index([("status", 1)])
        
        # 4. Índice para busca textual (Golden Record)
        # Nota: Como o nome costuma ficar dentro de dados_completos, o ideal é:
        self.collection.create_index([("dados_completos.titular_nome", 1)])
        
    def buscar_por_filtros(self, cartao_numero=None, status=None, page=1, limit=10, **kwargs):
        query = {}
        
        # Adiciona filtros dinamicamente
        if cartao_numero:
            query["cartao_numero"] = cartao_numero
        if status:
            query["status"] = status
        
        # Calcula paginação
        offset = (page - 1) * limit
        
        # Executa a busca
        cursor = self.collection.find(query).skip(offset).limit(limit)
        
        # Hydration: Converte BSON para Objeto de Domínio
        return [
            Cartao(
                usuario_id=doc["usuario_id"],
                cartao_numero=doc["cartao_numero"],
                dados_completos=doc.get("dados_completos", {}),
                data_consulta=doc["data_consulta"],
                data_validade_cache=doc["data_validade_cache"],
                status=doc["status"]
            ) for doc in cursor
        ]
            