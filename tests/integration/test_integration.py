import os, sys
import pytest
import pytest_asyncio # Certifique-se de ter instalado: pip install pytest-asyncio
from motor.motor_asyncio import AsyncIOMotorClient

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from src.infrastructure.repositories.cartao_repository import CartaoRepository

@pytest_asyncio.fixture
async def db_collection():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_uri)
    db = client.cadastro_unificado
    collection = db.cartoes
    
    # O yield entrega a COLLECTION real, não o gerador
    yield collection
    
    client.close()

@pytest.mark.asyncio
async def test_integracao_completa_infraestrutura(db_collection):
   
    repo = CartaoRepository(collection=db_collection)

    try:
        # 2. Valida Conexão (Acessando a database da coleção resolvida)
        await repo.collection.database.command("ping")
        print("\n✅ Conexão MongoDB OK.")
    except Exception as e:
        pytest.fail(f"Falha na conexão com Docker: {e}")

    # 3. Limpa e cria índices
    await repo.collection.drop_indexes()
    
    # Se o seu método criar_indices for async:
    await repo.criar_indices() 

    # 4. Validação final
    indices = await repo.collection.index_information()
    # Ajuste o nome conforme o que você definiu no repositório
    assert any("usuario_id" in idx for idx in indices.keys()), "Índice não encontrado!"