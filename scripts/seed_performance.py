import asyncio
import random
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Configurações
MONGO_URI = "mongodb://root:example@localhost:27018/sptrans?authSource=admin"
DB_NAME = "sptrans"
COLLECTION_NAME = "cartoes"
USUARIO_TESTE_ID = "12345678900"  # CPF usado como usuario_id
TOTAL_CARTOES_TESTE = 100

async def seed_performance():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    print(f"🚀 Iniciando seed de performance para o usuário/CPF: {USUARIO_TESTE_ID}...")

    # 1. Limpa dados antigos do usuário de teste
    await collection.delete_many({"usuario_id": USUARIO_TESTE_ID})

    cartoes_para_inserir = []

    # 2. Gerar 100 cartões para o mesmo usuário/CPF
    for i in range(1, TOTAL_CARTOES_TESTE + 1):
        numero_cartao = f"PERF-{1000 + i}"
        tipo = random.choice(["COMUM", "ESTUDANTE", "VALE_TRANSPORTE"])

        cartao = {
            "usuario_id": USUARIO_TESTE_ID,
            "cartao_numero": numero_cartao,
            "status": "ATIVO" if i % 10 != 0 else "BLOQUEADO",
            "tipo_cartao": tipo,
            "subtipo": "COMUM_MENSAL" if tipo == "COMUM" else "INTEIRA",
            "dados_completos": {
                "titular_nome": "JOSE DA PERFORMANCE TESTE",
                "cpf": USUARIO_TESTE_ID,
                "saldo": round(random.uniform(0, 500), 2),
                "data_emissao": datetime.utcnow().isoformat()
            },
            "data_consulta": datetime.utcnow(),
            "data_validade_cache": datetime.utcnow()
        }
        cartoes_para_inserir.append(cartao)

    # 3. Inserção em lote
    if cartoes_para_inserir:
        result = await collection.insert_many(cartoes_para_inserir)
        print(f"✅ Sucesso! {len(result.inserted_ids)} cartões inseridos para CPF {USUARIO_TESTE_ID}.")

    # 4. Verificação
    total_no_banco = await collection.count_documents({"usuario_id": USUARIO_TESTE_ID})
    print(f"📊 Total de cartões para CPF {USUARIO_TESTE_ID} no banco: {total_no_banco}")

    client.close()

if __name__ == "__main__":
    asyncio.run(seed_performance())