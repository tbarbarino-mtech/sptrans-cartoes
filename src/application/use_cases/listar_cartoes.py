
class ListarCartoesUseCase:
    def __init__(self, repository):
        self.repository = repository

    async def execute(self, page: int = 1, limit: int = 10, status: str = None):
        return await self.repository.buscar_por_filtros(
            page=page, 
            limit=limit, 
            status=status
        )