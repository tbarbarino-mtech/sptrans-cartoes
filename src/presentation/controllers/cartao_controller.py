from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

# Importa os casos de uso
from src.application.use_cases.buscar_cartao import BuscarCartaoUseCase
from src.application.use_cases.listar_cartoes import ListarCartoesUseCase

router = APIRouter(prefix="/v1/cartoes", tags=["Cartões SPTrans"])

# --- DTOs (Data Transfer Objects) para resposta segura ---
class CartaoResponse(BaseModel):
    usuario_id: str
    cartao_numero: str
    status: str
    titular_mascarado: str  # Campo calculado para segurança
    saldo: float

    class Config:
        from_attributes = True

# Função auxiliar de Mascaramento (LGPD)
def mascarar_nome(dados: dict) -> str:
    nome = dados.get("titular_nome", "DESCONHECIDO")
    partes = nome.split()
    if len(partes) > 1:
        return f"{partes[0]} *** {partes[-1]}"
    return nome

# --- ENDPOINTS ---

@router.get("/{numero}", response_model=CartaoResponse)
def buscar_cartao_por_numero(numero: str):
    use_case = BuscarCartaoUseCase()
    cartao = use_case.execute(numero)

    if not cartao:
        raise HTTPException(status_code=404, detail="Cartão não encontrado.")

    # Transformação para saída (Presenter)
    return CartaoResponse(
        usuario_id=cartao.usuario_id,
        cartao_numero=cartao.cartao_numero,
        status=cartao.status,
        titular_mascarado=mascarar_nome(cartao.dados_completos),
        saldo=cartao.dados_completos.get("saldo", 0.0)
    )

@router.get("/", response_model=List[CartaoResponse])
def listar_cartoes(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    status: Optional[str] = None
):
    use_case = ListarCartoesUseCase()
    cartoes = use_case.execute(page=page, limit=limit, status=status)
    
    # Monta a lista de resposta segura
    resposta = []
    for c in cartoes:
        resposta.append(CartaoResponse(
            usuario_id=c.usuario_id,
            cartao_numero=c.cartao_numero,
            status=c.status,
            titular_mascarado=mascarar_nome(c.dados_completos),
            saldo=c.dados_completos.get("saldo", 0.0)
        ))
    
    return resposta