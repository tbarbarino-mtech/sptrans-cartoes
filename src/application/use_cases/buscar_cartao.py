from src.infrastructure.repositories.cartao_repository import CartaoRepository

class BuscarCartaoUseCase:
    def __init__(self):
        # Injeção de dependência do Repositório
        self.repository = CartaoRepository()

    def execute(self, numero_cartao: str):
        # Chama o método otimizado do repositório
        resultado = self.repository.buscar_por_filtros(cartao_numero=numero_cartao)
        
        if not resultado:
            return None
            
        return resultado[0]