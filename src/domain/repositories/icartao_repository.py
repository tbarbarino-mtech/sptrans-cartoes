from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.domain.entities.cartao import Cartao

class ICartaoRepository(ABC):
    @abstractmethod
    def salvar(self, cartao: Cartao) -> None:
        pass

    @abstractmethod
    def criar_indices(self) -> None:
        pass

    @abstractmethod
    def buscar_por_filtros(self, **kwargs) -> List[Cartao]:
        pass