import os
import sys
import types
from datetime import datetime
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.testclient import TestClient

# --- Garantir que src esteja no sys.path ---
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

# Substituir a referência dentro do módulo do controller
import src.presentation.controllers.cartao_controller as cartao_controller
from src.infrastructure.repositories.cartao_repository import CartaoRepository
from src.application.use_cases.listar_cartoes_cpf import ListarCartoesCPFPaginadoUseCase as RealUseCase

class DummyListarUseCase:
    def __init__(self):
        self._real = RealUseCase(CartaoRepository())

    async def execute(self, cpf: str, page: int, limit: int):
        return await self._real.execute(cpf, page, limit)

# Monkeypatch: substituir a classe usada pelo controller
cartao_controller.ListarCartoesCPFPaginadoUseCase = DummyListarUseCase

# Agora importar app
from src.main import app
client = TestClient(app)

@pytest.mark.asyncio
async def test_get_cartoes_por_cpf_with_real_db():
    uri = os.environ["MONGODB_URI"]
    db_name = os.environ["MONGODB_DB"]
    coll_name = os.environ["MONGODB_COLLECTION"]

    client_motor = AsyncIOMotorClient(uri)
    coll = client_motor[db_name][coll_name]
    await coll.delete_many({})

    cpf_teste = "12345678901"
    await coll.insert_many([
        {
            "usuario_id": cpf_teste,
            "cartao_numero": "DB_1",
            "dados_completos": {"titular_nome": "A"},
            "status": "Ativo",
            "tipo_cartao": "COMUM",
            "subtipo": "PERMANENTE",
            "data_consulta": datetime.utcnow(),
            "data_validade_cache": datetime.utcnow()
        },
        {
            "usuario_id": cpf_teste,
            "cartao_numero": "DB_2",
            "dados_completos": {"titular_nome": "B"},
            "status": "Ativo",
            "tipo_cartao": "COMUM",
            "subtipo": "PERMANENTE",
            "data_consulta": datetime.utcnow(),
            "data_validade_cache": datetime.utcnow()
        },
    ])

    resp = client.get(f"/v1/cartoes/pessoas/{cpf_teste}/cartoes?page=1&limit=10")
    assert resp.status_code == 200, f"status {resp.status_code} body: {resp.text}"
    body = resp.json()
    assert body["total"] == 2
    assert any(item["cartao_numero"] == "DB_1" for item in body["items"])
    assert any(item["cartao_numero"] == "DB_2" for item in body["items"])

    await coll.delete_many({"usuario_id": cpf_teste})
    client_motor.close()