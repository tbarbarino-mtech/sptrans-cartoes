import os
import sys
import time
import asyncio
from datetime import datetime
from pymongo import MongoClient

# Garante que a raiz do projeto esteja no sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.infrastructure.repositories.cartao_repository import CartaoRepository
from src.domain.entities.cartao import Cartao

async def validar_performance_e_benchmark():
    # Conexão Mongo
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB", "sptrans")
    collection_name = os.getenv("MONGODB_COLLECTION", "cartoes")

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    print("\n--- ETAPA 5: PERFORMANCE & BENCHMARK ---")

    # 1. Criar índices (limpando antes para evitar conflitos)
    print("1. Criando índices...")
    try:
        collection.drop_indexes()
    except Exception:
        pass
    collection.create_index([("usuario_id", 1)], name="idx_usuario_id")
    collection.create_index([("cartao_numero", 1)], unique=True)

    # 2. Inserção em massa
    print("2. Inserindo 10.000 registros...")
    collection.delete_many({})
    cartoes_mock = [
        {
            "usuario_id": f"USER_{i%100}",
            "cartao_numero": f"NUM_{i}",
            "status": "Ativo",
            "dados_completos": {"titular_nome": f"Passageiro {i}", "saldo": 50.0},
            "tipo_cartao": "COMUM",
            "subtipo": "PERMANENTE",
            "data_consulta": datetime.utcnow(),
            "data_validade_cache": datetime.utcnow()
        } for i in range(10000)
    ]
    inicio_carga = time.time()
    collection.insert_many(cartoes_mock)
    fim_carga = time.time()
    print(f"✅ Inserção concluída em {fim_carga - inicio_carga:.2f}s")

    # 3. Plano de execução
    print("\n3. Plano de execução (.explain)...")
    explicacao = collection.find({"cartao_numero": "NUM_9999"}).explain()
    stage = explicacao['queryPlanner']['winningPlan'].get('stage')
    if stage == 'FETCH':
        stage = explicacao['queryPlanner']['winningPlan'].get('inputStage', {}).get('stage')
    print(f"Estágio: {stage}")
    if stage == 'IXSCAN':
        print("✅ Índice utilizado.")
    else:
        print("❌ Full Collection Scan detectado!")

    # 4. Latência de consulta
    print("\n4. Testando latência...")
    inicio_query = time.time()
    _ = list(collection.find({"cartao_numero": "NUM_5000"}).limit(1))
    fim_query = time.time()
    print(f"⏱️ Latência: {(fim_query - inicio_query)*1000:.2f} ms")

    # 5. Evidência com CartaoRepository (async)
    print("\n5. Evidência com CartaoRepository...")
    repo = CartaoRepository()
    novo = Cartao(
        usuario_id="USER_MTECH_01",
        cartao_numero="123456",
        dados_completos={"titular": "THAMYRIS BARBARINO", "saldo": 100.0},
        data_consulta=datetime.now(),
        data_validade_cache=datetime.now(),
        status="Ativo"
    )
    inicio_salvar = time.time()
    await repo.salvar(novo)  # await aqui
    fim_salvar = time.time()
    print(f"⏱️ Tempo salvar: {(fim_salvar - inicio_salvar)*1000:.2f} ms")

    inicio_busca = time.time()
    resultados = await repo.buscar_por_filtros(cartao_numero="123456")  # await aqui
    fim_busca = time.time()
    print(f"⏱️ Tempo busca: {(fim_busca - inicio_busca)*1000:.2f} ms")

    if resultados:
        obj = resultados[0]
        print(f"Sucesso! Objeto recuperado: {obj.cartao_numero}")
        print(f"Classe de Domínio: {type(obj).__name__}")
        print(f"Dados: {obj.dados_completos}")

if __name__ == "__main__":
    asyncio.run(validar_performance_e_benchmark())