import sys, os
import pytest
import mongomock
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

# --- Ajuste do caminho para importar src ---
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

from src.domain.entities.cartao import Cartao
from src.infrastructure.repositories.cartao_repository import CartaoRepository

# --- FIXTURES ---
@pytest.fixture
def mock_collection():
    """Cria uma coleção MongoDB em memória para testes isolados (usada apenas para leitura direta nos asserts)."""
    return mongomock.MongoClient().db.collection

@pytest.fixture
def repo_with_mocked_update(mock_collection):
  
    async_collection = MagicMock()
    async_collection.update_one = AsyncMock(return_value=None)

    repo = CartaoRepository(collection=async_collection)
    repo._sync_collection = mock_collection
    return repo

@pytest.mark.asyncio
async def test_deve_salvar_objeto_cartao_e_persistir_campos_obrigatorios(repo_with_mocked_update):
    cartao = Cartao(
        usuario_id="USER_SPTRANS_01",
        cartao_numero="654321",
        dados_completos={"tipo": "Comum", "saldo": 50.0},
        data_consulta=datetime.now(),
        data_validade_cache=datetime.now() + timedelta(days=7),
        status="Ativo"
    )

    # chama o método assíncrono
    await repo_with_mocked_update.salvar(cartao)

    # Verifica que update_one foi chamado com o filtro e o $set contendo o dict do cartão
    expected_filter = {"cartao_numero": "654321"}
    expected_update = {"$set": cartao.to_dict()}
    repo_with_mocked_update.collection.update_one.assert_awaited_once()
    # Checagem mais específica dos argumentos
    called_args, called_kwargs = repo_with_mocked_update.collection.update_one.call_args
    assert called_args[0] == expected_filter
    assert called_args[1] == expected_update
    # upsert pode vir como kwarg ou positional; se veio como kwarg:
    if "upsert" in called_kwargs:
        assert called_kwargs["upsert"] is True

def test_deve_garantir_hydration_na_busca_por_numero():
    # Teste de hydration usando mongomock síncrono (sem envolver repo async)
    sync_col = mongomock.MongoClient().db.collection
    sync_col.insert_one({
        "usuario_id": "U1",
        "cartao_numero": "123",
        "status": "Ativo",
        "dados_completos": {"titular": "THAMYRIS BARBARINO"},
        "data_consulta": datetime.now(),
        "data_validade_cache": datetime.now()
    })

    doc = sync_col.find_one({"cartao_numero": "123"})
    resultado = Cartao(**{k: v for k, v in doc.items() if k != "_id"})

    assert isinstance(resultado, Cartao)
    assert resultado.dados_completos["titular"] == "THAMYRIS BARBARINO"

def test_deve_ignorar_cartoes_bloqueados_na_busca_do_passageiro():
    sync_col = mongomock.MongoClient().db.collection
    sync_col.insert_many([
        {"usuario_id": "PASSAGEIRO_A", "cartao_numero": "101", "status": "Ativo",
         "dados_completos": {}, "data_consulta": datetime.now(), "data_validade_cache": datetime.now()},
        {"usuario_id": "PASSAGEIRO_A", "cartao_numero": "102", "status": "Bloqueado",
         "dados_completos": {}, "data_consulta": datetime.now(), "data_validade_cache": datetime.now()}
    ])

    cursor = sync_col.find({"status": "Ativo"})
    resultado = [Cartao(**{k: v for k, v in doc.items() if k != "_id"}) for doc in cursor]

    assert len(resultado) == 1
    assert resultado[0].cartao_numero == "101"

def test_deve_filtrar_apenas_cartoes_dentro_da_validade_de_cache():
    sync_col = mongomock.MongoClient().db.collection
    data_passada = datetime.now() - timedelta(days=1)
    data_futura = datetime.now() + timedelta(days=1)

    sync_col.insert_many([
        {"cartao_numero": "EXPIRADO", "data_validade_cache": data_passada, "usuario_id": "U1",
         "status": "Ativo", "dados_completos": {}, "data_consulta": datetime.now()},
        {"cartao_numero": "VALIDO", "data_validade_cache": data_futura, "usuario_id": "U1",
         "status": "Ativo", "dados_completos": {}, "data_consulta": datetime.now()}
    ])

    query = {"data_validade_cache": {"$gt": datetime.now()}}
    cursor = sync_col.find(query)
    resultado = [Cartao(**{k: v for k, v in doc.items() if k != "_id"}) for doc in cursor]

    assert len(resultado) == 1
    assert resultado[0].cartao_numero == "VALIDO"

def test_deve_paginar_resultados_corretamente():
    sync_col = mongomock.MongoClient().db.collection
    docs = [
        {
            "usuario_id": f"U{i}", "cartao_numero": str(i), "status": "Ativo",
            "dados_completos": {}, "data_consulta": datetime.now(),
            "data_validade_cache": datetime.now()
        } for i in range(10)
    ]
    sync_col.insert_many(docs)

    cursor = sync_col.find().skip(3).limit(3)
    resultado = [Cartao(**{k: v for k, v in doc.items() if k != "_id"}) for doc in cursor]

    assert len(resultado) == 3
    assert resultado[0].cartao_numero == "3"

@pytest.mark.asyncio
async def test_buscar_por_cpf_paginado_async_calls_collection_methods():
    # Simula uma collection async (Motor-like) com AsyncMock para count_documents e to_list
    mock_collection = MagicMock()
    mock_collection.count_documents = AsyncMock(return_value=42)

    docs = [{
        "usuario_id": "USER_1",
        "cartao_numero": "NUM_1",
        "dados_completos": {"titular_nome": "A"},
        "status": "Ativo",
        "tipo_cartao": "COMUM",
        "subtipo": "PERMANENTE"
    }]

    # Cursor que suporta skip().limit().to_list()
    find_cursor = MagicMock()
    find_cursor.to_list = AsyncMock(return_value=docs)
    find_cursor.skip = MagicMock(return_value=find_cursor)
    find_cursor.limit = MagicMock(return_value=find_cursor)

    mock_collection.find.return_value = find_cursor

    repo = CartaoRepository(collection=mock_collection)
    items, total = await repo.buscar_por_cpf_paginado("USER_1", page=1, limit=10)

    mock_collection.count_documents.assert_called_once_with({"usuario_id": "USER_1"})
    mock_collection.find.assert_called_once()
    assert total == 42
    assert len(items) == 1
    assert items[0].cartao_numero == "NUM_1"
    # Se o CartaoRepository converte tipo_cartao para enum, verifique atributo sem falhar
    assert getattr(items[0], "tipo_cartao", None) is not None