

class BuscarCartaoUseCase:
    def __init__(self, repository):
        self.repository = repository

    async def execute(self, numero_cartao: str):
        resultado = await self.repository.buscar_por_filtros(cartao_numero=numero_cartao)
        
        if not resultado:
            return None
            
        return resultado[0]