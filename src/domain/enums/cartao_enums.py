from enum import Enum

class TipoCartao(str, Enum):
    COMUM = "COMUM"
    ESTUDANTE = "ESTUDANTE"
    IDOSO = "IDOSO"
    PCD = "PCD"
    BILHETE_UNICO = "BILHETE_UNICO"
    BOM = "BOM"
    VALE_TRANSPORTE = "VALE_TRANSPORTE"

class SubtipoCartao(str, Enum):
    PERMANENTE = "PERMANENTE"
    TEMPORARIO = "TEMPORARIO"
    PROVISORIO = "PROVISORIO"