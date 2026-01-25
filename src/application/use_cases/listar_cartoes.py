from src.infrastructure.repositories.cartao_repository import CartaoRepository

class ListarCartoesUseCase:
    def __init__(self):
        self.repository = CartaoRepository()

    def execute(self, page: int = 1, limit: int = 10, status: str = None):
        # Repassa os filtros para a query otimizada
        return self.repository.buscar_por_filtros(page=page, limit=limit, status=status)