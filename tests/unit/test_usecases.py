import os
import sys
import pytest
from unittest.mock import MagicMock, AsyncMock

import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # raiz do repositório
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from src.domain.entities.cartao import Cartao

# Import das use cases (elas importam CartaoRepository internamente)
from src.application.use_cases.listar_cartoes import ListarCartoesUseCase
from src.application.use_cases.buscar_cartao import BuscarCartaoUseCase
from src.application.use_cases.listar_cartoes_cpf import ListarCartoesCPFPaginadoUseCase

# -------------------------
# Tests for ListarCartoesUseCase
# -------------------------
def test_listar_cartoes_usecase_calls_repository_and_returns_list(monkeypatch):
    """
    Substitui a referência CartaoRepository dentro do módulo da use case,
    garantindo que a instância criada internamente seja nosso repo_fake.
    """
    repo_fake = MagicMock()
    sample = Cartao(usuario_id="U1", cartao_numero="X1", dados_completos={}, status="Ativo")
    # buscar_por_filtros é síncrono nesta use case
    repo_fake.buscar_por_filtros.return_value = [sample]

    # monkeypatcha a referência usada dentro do módulo da use case
    monkeypatch.setattr(
        "src.application.use_cases.listar_cartoes.CartaoRepository",
        lambda *args, **kwargs: repo_fake,
        raising=True
    )

    use_case = ListarCartoesUseCase()
    result = use_case.execute(page=1, limit=10, status="Ativo")

    repo_fake.buscar_por_filtros.assert_called_once_with(page=1, limit=10, status="Ativo")
    assert isinstance(result, list)
    assert result[0].cartao_numero == "X1"

def test_listar_cartoes_usecase_handles_empty_result(monkeypatch):
    repo_fake = MagicMock()
    repo_fake.buscar_por_filtros.return_value = []

    monkeypatch.setattr(
        "src.application.use_cases.listar_cartoes.CartaoRepository",
        lambda *args, **kwargs: repo_fake,
        raising=True
    )

    use_case = ListarCartoesUseCase()
    result = use_case.execute(page=1, limit=10, status=None)

    repo_fake.buscar_por_filtros.assert_called_once_with(page=1, limit=10, status=None)
    assert result == []

# -------------------------
# Tests for BuscarCartaoUseCase
# -------------------------
def test_buscar_cartao_usecase_returns_first_match(monkeypatch):
    repo_fake = MagicMock()
    sample = Cartao(usuario_id="U2", cartao_numero="CARD123", dados_completos={}, status="Ativo")
    # buscar_por_filtros síncrono retornando lista
    repo_fake.buscar_por_filtros.return_value = [sample]

    # monkeypatcha a referência dentro do módulo da use case buscar_cartao
    monkeypatch.setattr(
        "src.application.use_cases.buscar_cartao.CartaoRepository",
        lambda *args, **kwargs: repo_fake,
        raising=True
    )

    use_case = BuscarCartaoUseCase()
    result = use_case.execute("CARD123")

    repo_fake.buscar_por_filtros.assert_called_once_with(cartao_numero="CARD123")
    assert result is not None
    assert result.cartao_numero == "CARD123"

def test_buscar_cartao_usecase_returns_none_when_not_found(monkeypatch):
    repo_fake = MagicMock()
    repo_fake.buscar_por_filtros.return_value = []

    monkeypatch.setattr(
        "src.application.use_cases.buscar_cartao.CartaoRepository",
        lambda *args, **kwargs: repo_fake,
        raising=True
    )

    use_case = BuscarCartaoUseCase()
    result = use_case.execute("UNKNOWN")

    repo_fake.buscar_por_filtros.assert_called_once_with(cartao_numero="UNKNOWN")
    assert result is None

# -------------------------
# Tests for ListarCartoesCPFPaginadoUseCase
# -------------------------
@pytest.mark.asyncio
async def test_listar_cartoes_cpf_paginado_calls_repository_and_calculates_pages():
    # repo injetado (ICartaoRepository-like) com método async buscar_por_cpf_paginado
    repo_mock = MagicMock()
    sample = Cartao(usuario_id="U3", cartao_numero="C1", dados_completos={}, status="Ativo")
    total = 25
    repo_mock.buscar_por_cpf_paginado = AsyncMock(return_value=([sample], total))

    use_case = ListarCartoesCPFPaginadoUseCase(repo_mock)

    page = 2
    limit = 10
    items, returned_total, total_pages = await use_case.execute("12345678901", page, limit)

    repo_mock.buscar_por_cpf_paginado.assert_awaited_once_with("12345678901", page, limit)
    assert returned_total == total
    assert total_pages == 3
    assert items[0].cartao_numero == "C1"

@pytest.mark.asyncio
async def test_listar_cartoes_cpf_paginado_handles_zero_limit():
    repo_mock = MagicMock()
    sample = Cartao(usuario_id="U4", cartao_numero="C2", dados_completos={}, status="Ativo")
    repo_mock.buscar_por_cpf_paginado = AsyncMock(return_value=([sample], 5))

    use_case = ListarCartoesCPFPaginadoUseCase(repo_mock)

    items, returned_total, total_pages = await use_case.execute("00000000000", page=1, limit=0)

    assert returned_total == 5
    assert total_pages == 0
    assert items[0].cartao_numero == "C2"

@pytest.mark.asyncio
async def test_listar_cartoes_cpf_paginado_propagates_repository_exception():
    repo_mock = MagicMock()
    repo_mock.buscar_por_cpf_paginado = AsyncMock(side_effect=RuntimeError("db error"))

    use_case = ListarCartoesCPFPaginadoUseCase(repo_mock)

    with pytest.raises(RuntimeError):
        await use_case.execute("11111111111", page=1, limit=10)