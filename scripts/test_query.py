from src.infrastructure.repositories.cartao_repository import CartaoRepository
from src.domain.entities.cartao import Cartao
from pymongo import MongoClient
from datetime import datetime

# Conexão
client = MongoClient("mongodb://root:example@localhost:27017/")
db = client["sptrans"]
repo = CartaoRepository(db["cartoes"])

# Criar um dado para garantir que a query retorne algo no print
novo = Cartao(
    usuario_id="USER_MTECH_01",
    cartao_numero="123456",
    dados_completos={"titular": "THAMYRIS BARBARINO", "saldo": 100.0},
    data_consulta=datetime.now(),
    data_validade_cache=datetime.now(),
    status="Ativo"
)
repo.salvar(novo)

print("\n--- EVIDÊNCIA ETAPA 2: QUERY DE CARTÃO ---")
# Buscando pelo nome correto do argumento
resultados = repo.buscar_por_filtros(cartao_numero="123456")

if resultados:
    obj = resultados[0]
    print(f"Sucesso! Objeto recuperado: {obj.cartao_numero}")
    print(f"Classe de Domínio: {type(obj).__name__}")
    print(f"Dados do Golden Record: {obj.dados_completos}")