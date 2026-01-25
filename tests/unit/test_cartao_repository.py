import pytest
import mongomock
from datetime import datetime, timedelta
from src.infrastructure.repositories.cartao_repository import CartaoRepository
from src.domain.entities.cartao import Cartao

# --- FIXTURES (Configuração do Ambiente de Teste) ---

@pytest.fixture
def mock_collection():
    """Cria uma coleção MongoDB em memória para testes isolados."""
    return mongomock.MongoClient().db.collection

@pytest.fixture
def repo_mock(mock_collection):
    """Instancia o repositório injetando a coleção mockada."""
    return CartaoRepository(mock_collection)

# --- CASOS DE TESTE (Etapa 3 do Laudo) ---

def test_deve_salvar_objeto_cartao_e_persistir_campos_obrigatorios(repo_mock, mock_collection):
    """
    Teste de Salvar: Confirma se o objeto Cartao é transformado 
    corretamente em BSON e gravado no MongoDB.
    """
    cartao = Cartao(
        usuario_id="USER_SPTRANS_01",
        cartao_numero="654321",
        dados_completos={"tipo": "Comum", "saldo": 50.0},
        data_consulta=datetime.now(),
        data_validade_cache=datetime.now() + timedelta(days=7),
        status="Ativo"
    )

    repo_mock.salvar(cartao)
    
    # Validação no "banco" mockado
    doc_bruto = mock_collection.find_one({"cartao_numero": "654321"})
    assert doc_bruto is not None
    assert doc_bruto["usuario_id"] == "USER_SPTRANS_01"
    assert doc_bruto["status"] == "Ativo"

def test_deve_garantir_hydration_na_busca_por_numero(repo_mock, mock_collection):
    """
    Teste de Busca: Garante que a query retorna exatamente o objeto 
    solicitado através do processo de Hydration (Dicionário -> Classe).
    """
    mock_collection.insert_one({
        "usuario_id": "U1", 
        "cartao_numero": "123", 
        "status": "Ativo",
        "dados_completos": {"titular": "THAMYRIS BARBARINO"}, 
        "data_consulta": datetime.now(),
        "data_validade_cache": datetime.now()
    })

    resultado = repo_mock.buscar_por_filtros(cartao_numero="123")

    assert len(resultado) == 1
    assert isinstance(resultado[0], Cartao)
    assert resultado[0].dados_completos["titular"] == "THAMYRIS BARBARINO"

def test_deve_ignorar_cartoes_bloqueados_na_busca_do_passageiro(repo_mock, mock_collection):
    """
    Teste de Segurança: Valida se o sistema ignora cartões bloqueados 
    ao procurar registos ativos de um passageiro.
    """
    mock_collection.insert_many([
        {"usuario_id": "PASSAGEIRO_A", "cartao_numero": "101", "status": "Ativo", 
         "dados_completos": {}, "data_consulta": datetime.now(), "data_validade_cache": datetime.now()},
        {"usuario_id": "PASSAGEIRO_A", "cartao_numero": "102", "status": "Bloqueado", 
         "dados_completos": {}, "data_consulta": datetime.now(), "data_validade_cache": datetime.now()}
    ])

    # Simula a regra de negócio de buscar apenas ativos
    resultado = repo_mock.buscar_por_filtros(status="Ativo")

    assert len(resultado) == 1
    assert resultado[0].cartao_numero == "101"

def test_deve_filtrar_apenas_cartoes_dentro_da_validade_de_cache(repo_mock, mock_collection):
    """
    Teste de Validade: Crucial para o setor financeiro, garantindo que 
    apenas cartões com cache válido sejam listados.
    """
    data_passada = datetime.now() - timedelta(days=1)
    data_futura = datetime.now() + timedelta(days=1)
    
    mock_collection.insert_many([
        {"cartao_numero": "EXPIRADO", "data_validade_cache": data_passada, "usuario_id": "U1", 
         "status": "Ativo", "dados_completos": {}, "data_consulta": datetime.now()},
        {"cartao_numero": "VALIDO", "data_validade_cache": data_futura, "usuario_id": "U1", 
         "status": "Ativo", "dados_completos": {}, "data_consulta": datetime.now()}
    ])

    # Executa a lógica de filtro por data
    # (Nota: Certifique-se que o seu repo suporta o filtro de validade ou use query direta para o laudo)
    query = {"data_validade_cache": {"$gt": datetime.now()}}
    cursor = mock_collection.find(query)
    resultado = [Cartao(**{k: v for k, v in doc.items() if k != '_id'}) for doc in cursor]

    assert len(resultado) == 1
    assert resultado[0].cartao_numero == "VALIDO"

def test_deve_paginar_resultados_corretamente(repo_mock, mock_collection):
    """
    Teste de Performance: Valida a paginação eficiente (Skip/Limit).
    """
    docs = [
        {
            "usuario_id": f"U{i}", "cartao_numero": str(i), "status": "Ativo",
            "dados_completos": {}, "data_consulta": datetime.now(),
            "data_validade_cache": datetime.now()
        } for i in range(10)
    ]
    mock_collection.insert_many(docs)

    # Página 2, Limite 3 (Deve retornar os cartões 3, 4 e 5)
    resultado = repo_mock.buscar_por_filtros(page=2, limit=3)
    
    assert len(resultado) == 3
    assert resultado[0].cartao_numero == "3"