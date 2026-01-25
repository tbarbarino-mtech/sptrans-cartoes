import pytest
from src.infrastructure.repositories.cartao_repository import CartaoRepository

def test_integracao_completa_infraestrutura():
    # 1. Valida Conexão
    try:
        repo = CartaoRepository()
        # Força uma operação simples para testar a conexão real
        repo.collection.database.command("ping")
        print("\n✅ Sucesso: Conexão estabelecida com MongoDB via Docker.")
    except Exception as e:
        pytest.fail(f"Falha na conexão com Docker: {e}")

    # 2. Executa criação
    repo.criar_indices()
    indices = repo.collection.index_information()

    # 3. Valida Índice Composto
    assert "usuario_id_1_cartao_numero_1" in indices
    print("✅ Sucesso: Índice Composto (usuario_id_1_cartao_numero_1) verificado!")

    # 4. Valida Índice Simples
    assert "cartao_numero_1" in indices
    print("✅ Sucesso: Índice Simples (cartao_numero_1) verificado!")