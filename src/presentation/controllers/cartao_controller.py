import re
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Optional, List

# Importa os casos de uso, repositórios e schemas
from src.application.use_cases.listar_cartoes_cpf import ListarCartoesCPFPaginadoUseCase
from src.application.use_cases.buscar_cartao import BuscarCartaoUseCase
from src.application.use_cases.listar_cartoes import ListarCartoesUseCase
from src.infrastructure.repositories.cartao_repository import CartaoRepository
from src.presentation.schemas.cartao_schemas import CartaoResponse, PaginatedResponse

router = APIRouter(prefix="/v1/cartoes", tags=["Cartões SPTrans"])

# --- Injeção de Dependências (Providers) ---

def get_repository() -> CartaoRepository:
    return CartaoRepository()

def get_buscar_use_case(repo: CartaoRepository = Depends(get_repository)) -> BuscarCartaoUseCase:
    return BuscarCartaoUseCase(repo)

def get_listar_use_case(repo: CartaoRepository = Depends(get_repository)) -> ListarCartoesUseCase:
    return ListarCartoesUseCase(repo)

def get_listar_cpf_use_case(repo: CartaoRepository = Depends(get_repository)) -> ListarCartoesCPFPaginadoUseCase:
    return ListarCartoesCPFPaginadoUseCase(repo)

# --- Funções Auxiliares ---

def mascarar_nome(dados: dict) -> str:
    if not dados:
        return "DESCONHECIDO"
    nome = dados.get("titular_nome") or dados.get("titular") or "DESCONHECIDO"
    partes = nome.split()
    if len(partes) > 1:
        return f"{partes[0]} *** {partes[-1]}"
    return nome

# --- Rotas ---

@router.get("/{numero}", response_model=CartaoResponse)
async def buscar_cartao_por_numero(
    numero: str = Path(..., description="Número do cartão SPTrans"),
    use_case: BuscarCartaoUseCase = Depends(get_buscar_use_case)
):
    # CORREÇÃO: Adicionado await e injeção de dependência
    cartao = await use_case.execute(numero)

    if not cartao:
        raise HTTPException(status_code=404, detail="Cartão não encontrado.")

    return CartaoResponse(
        usuario_id=cartao.usuario_id,
        cartao_numero=cartao.cartao_numero,
        status=cartao.status,
        titular_mascarado=mascarar_nome(cartao.dados_completos),
        saldo=cartao.dados_completos.get("saldo", 0.0)
    )

@router.get("/", response_model=List[CartaoResponse])
async def listar_cartoes(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    status: Optional[str] = None,
    use_case: ListarCartoesUseCase = Depends(get_listar_use_case)
):
    # CORREÇÃO: Adicionado await e injeção de dependência
    cartoes = await use_case.execute(page=page, limit=limit, status=status)

    return [
        CartaoResponse(
            usuario_id=c.usuario_id,
            cartao_numero=c.cartao_numero,
            status=c.status,
            titular_mascarado=mascarar_nome(c.dados_completos),
            saldo=c.dados_completos.get("saldo", 0.0)
        ) for c in cartoes
    ]

@router.get("/pessoas/{cpf}/cartoes", response_model=PaginatedResponse)
async def get_cartoes_por_cpf(
    cpf: str = Path(..., min_length=11, max_length=14),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    use_case: ListarCartoesCPFPaginadoUseCase = Depends(get_listar_cpf_use_case)
):
    # 1. Normalização do CPF
    cpf_clean = re.sub(r"\D", "", cpf)
    if len(cpf_clean) != 11:
        raise HTTPException(status_code=422, detail="CPF deve conter 11 dígitos numéricos")

    # 2. Execução
    items, total, total_pages = await use_case.execute(cpf_clean, page, limit)

    # 3. Mapeamento
    items_out = [
        CartaoResponse(
            usuario_id=c.usuario_id,
            cartao_numero=c.cartao_numero,
            status=c.status,
            tipoCartao=getattr(c.tipo_cartao, "value", None) if hasattr(c, "tipo_cartao") else None,
            subtipo=getattr(c.subtipo, "value", None) if hasattr(c, "subtipo") else None,
            titular_mascarado=mascarar_nome(c.dados_completos),
            saldo=c.dados_completos.get("saldo", 0.0)
        ) for c in items
    ]

    return PaginatedResponse(
        items=items_out,
        total=total,
        page=page,
        size=limit,
        total_pages=total_pages
    )