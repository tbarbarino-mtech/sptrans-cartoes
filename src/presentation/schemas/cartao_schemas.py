from pydantic import BaseModel
from typing import List

class CartaoResponse(BaseModel):
    usuario_id: str 
    cartao_numero: str
    status: str
    titular_mascarado: str
    saldo: float

    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    items: List[CartaoResponse]
    total: int
    page: int
    size: int
    total_pages: int