import time
from datetime import datetime
from src.infrastructure.repositories.cartao_repository import CartaoRepository

def validar_performance_e_benchmark():
    repo = CartaoRepository()
    
    print("--- INICIANDO ETAPA 5: PERFORMANCE & BENCHMARK ---")
    
    # 1. Preparação: Criando índices
    print("1. Criando índices de performance...")
    repo.criar_indices()
    
    # 2. Benchmark: Inserção de 10.000 registros simultâneos
    print("2. Inserindo 10.000 registros para teste de carga...")
    repo.collection.delete_many({}) # Limpa para o teste ser puro
    
    cartoes_mock = [
        {
            "usuario_id": f"USER_{i}",
            "cartao_numero": f"NUM_{i}",
            "status": "Ativo",
            "dados_completos": {"titular_nome": f"Passageiro {i}", "saldo": 50.0},
            "data_consulta": datetime.now(),
            "data_validade_cache": datetime.now()
        } for i in range(10000)
    ]
    
    inicio_carga = time.time()
    repo.collection.insert_many(cartoes_mock)
    fim_carga = time.time()
    print(f"✅ Carga concluída em: {fim_carga - inicio_carga:.2f} segundos.")

    # 3. Exploração de Plano de Execução (.explain)
    print("\n3. Analisando Plano de Execução (.explain())...")
    query = {"cartao_numero": "NUM_9999"}
    explicacao = repo.collection.find(query).explain()
    
    winning_plan = explicacao['queryPlanner']['winningPlan']
    stage = winning_plan.get('stage')
    
    # Verifica se usou índice (IXSCAN) ou se precisou buscar o documento (FETCH)
    if stage == 'FETCH':
        stage = winning_plan.get('inputStage', {}).get('stage')

    print(f"Estágio de execução: {stage}")
    
    if stage == 'IXSCAN':
        print("✅ SUCESSO: Índice utilizado (IXSCAN).")
    else:
        print("❌ ALERTA: Full Collection Scan (COLLSCAN) detectado!")

    # 4. Teste de Velocidade de Resposta
    print("\n4. Testando velocidade de resposta individual...")
    inicio_query = time.time()
    repo.buscar_por_filtros(cartao_numero="NUM_5000")
    fim_query = time.time()
    
    latencia_ms = (fim_query - inicio_query) * 1000
    print(f"⏱️ Tempo de resposta: {latencia_ms:.4f} ms")

if __name__ == "__main__":
    validar_performance_e_benchmark()