from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass
class Cartao:
    usuario_id: str              #  usuario_id VARCHAR(50)
    cartao_numero: str           #  cartao_numero VARCHAR(20)
    dados_completos: Dict[str, Any] #  dados_completos JSONB (O JSON "raw" da SPTrans)
    data_consulta: datetime      #  data_consulta TIMESTAMP
    data_validade_cache: datetime #  data_validade TIMESTAMP (expiração do cache)
    status: str                  #  status VARCHAR(20)
    metadados: Optional[Dict] = None #  metadados JSONB

    def to_dict(self):
        return {
            "usuario_id": self.usuario_id,
            "cartao_numero": self.cartao_numero,
            "dados_completos": self.dados_completos,
            "data_consulta": self.data_consulta,
            "data_validade_cache": self.data_validade_cache,
            "status": self.status,
            "metadados": self.metadados
        }