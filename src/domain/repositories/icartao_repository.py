from abc import ABC, abstractmethod
from typing import List, Tuple
from src.domain.entities.cartao import Cartao

class ICartaoRepository(ABC):
    @abstractmethod
    async def salvar(self, cartao: Cartao) -> None:
        """Persiste ou atualiza um cartão."""
        raise NotImplementedError

    @abstractmethod
    async def criar_indices(self) -> None:
        """Cria índices necessários no banco."""
        raise NotImplementedError

    @abstractmethod
    async def buscar_por_filtros(self, **kwargs) -> List[Cartao]:
        """Busca cartões por filtros genéricos."""
        raise NotImplementedError

    @abstractmethod
    async def buscar_por_cpf_paginado(self, cpf: str, page: int = 1, limit: int = 10) -> Tuple[List[Cartao], int]:
        """Retorna (items, total) para um CPF com paginação."""
        raise NotImplementedError