from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime
from src.domain.enums.cartao_enums import TipoCartao, SubtipoCartao

@dataclass
class Cartao:
    usuario_id: str
    cartao_numero: str
    dados_completos: Dict
    tipo_cartao: Optional[TipoCartao] = None
    subtipo: Optional[SubtipoCartao] = None
    data_consulta: Optional[datetime] = None
    data_validade_cache: Optional[datetime] = None
    status: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "usuario_id": self.usuario_id,
            "cartao_numero": self.cartao_numero,
            "dados_completos": self.dados_completos,
            "tipo_cartao": self.tipo_cartao.value if self.tipo_cartao else None,
            "subtipo": self.subtipo.value if self.subtipo else None,
            "data_consulta": self.data_consulta,
            "data_validade_cache": self.data_validade_cache,
            "status": self.status
        }