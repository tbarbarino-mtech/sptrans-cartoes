from typing import Tuple, List
from src.domain.entities.cartao import Cartao
from src.domain.repositories.icartao_repository import ICartaoRepository

class ListarCartoesCPFPaginadoUseCase:
    def __init__(self, repository: ICartaoRepository):
        self.repository = repository

    async def execute(self, cpf: str, page: int, limit: int) -> Tuple[List[Cartao], int, int]:
        items, total = await self.repository.buscar_por_cpf_paginado(cpf, page, limit)
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        return items, total, total_pages