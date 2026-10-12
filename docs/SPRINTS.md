# Sprints — Orquestração de stress test

| Sprint | Escopo | Status | Evidência |
|---|---|---|---|
| 0 | Preparar branch, estrutura inicial e tracker sem alterar o catálogo existente | Concluído | `python -m pytest tests -q -o addopts=''`: `87 passed in 23.79s`; `git diff --exit-code -- backend/verificalab/catalog.py`: sem diferenças |
| 1 | Definir autorização explícita dos alvos | Concluído | 19 testes específicos e 106 testes globais passaram; execução manual libera loopback e rejeita alvo externo sem arquivo de autorização (evidências detalhadas abaixo) |
| 2 | Catalogar as ferramentas em `backend/config/tools.yaml` e carregar o registro tipado | Concluído | 8 ferramentas carregadas; 25 testes do registry e 131 testes globais passaram |
| 3 | Implementar adaptadores das ferramentas de stress test | Não iniciado | — |
| 4 | Orquestrar execuções autorizadas | Não iniciado | — |
| 5 | Integrar resultados e métricas | Não iniciado | — |
| 6 | Integrar fluxos de interface TUI | Não iniciado | — |
| 7 | Cobrir fluxos e limites com testes | Não iniciado | — |
| 8 | Validar documentação e execução integrada | Não iniciado | — |

## Evidências do Sprint 1

Implementado `require_authorization(target)` com liberação apenas de `127.0.0.1`,
`::1` e `localhost`; todos os demais alvos exigem `data/secrets/authorization.json`
com `target`, `owner`, `reason` e `expires_at` válidos. A assinatura é opcional.
O alvo registrado deve corresponder literalmente ao pedido; expiração sem fuso
horário, arquivo ausente/inválido e campos obrigatórios ausentes são recusados.

```text
$ cd backend && python -m pytest tests/test_authorization.py -v
collected 19 items
tests/test_authorization.py ...................                          [100%]
============================== 19 passed in 0.06s ==============================
```

```text
$ cd backend && python -m pytest tests -q
........................................................................ [ 67%]
..................................                                       [100%]
```

O comando global acima terminou com código 0. Como `pytest.ini` já define
`addopts = -q`, também foi executado sem essa configuração quiet para registrar
a contagem final:

```text
$ cd backend && python -m pytest tests -q -o addopts=''
........................................................................ [ 67%]
..................................                                       [100%]
106 passed in 24.81s
```

Verificações manuais:

```text
$ cd backend && python -c "from verificalab.core.authorization import require_authorization; print(require_authorization('127.0.0.1:8080'))"
Authorization(target='127.0.0.1:8080', owner='local', reason='alvo loopback', expires_at=None, signature=None)
```

```text
$ cd backend && python -c "from verificalab.core.authorization import require_authorization; require_authorization('example.com')"
verificalab.core.authorization.AuthorizationError: não foi possível ler uma autorização válida: [Errno 2] No such file or directory: '/home/grekas/Projetos/VerificadordeSegurança/VerificaLab/data/secrets/authorization.json'
```

## Evidências do Sprint 2

`backend/config/tools.yaml` declara as oito ferramentas do inventário com
camada, requisito de root, descrição, orientação de uso, exemplo, riscos e
limites curtos. `ToolRegistry.load()` lê o YAML com `safe_load` e produz
dataclasses; `all()` aceita filtro por camada, `get(id)` consulta o registro e
`installed()` limita o resultado a caminhos relativos existentes dentro da raiz.
Caminhos ausentes ou inseguros permanecem no catálogo com `installed=False`.
O catálogo estático existente em `catalog.py` não foi alterado.

Verificação do total:

```text
$ cd backend && /home/grekas/Projetos/VerificadordeSegurança/VerificaLab/.venv/bin/python -c "from verificalab.stress.registry import ToolRegistry; r=ToolRegistry.load(); print(len(r.all()))"
8
```

Verificação manual de `when_to_use` não vazio:

```text
$ cd backend && /home/grekas/Projetos/VerificadordeSegurança/VerificaLab/.venv/bin/python -c "from verificalab.stress.registry import ToolRegistry; r=ToolRegistry.load(); [print(t.id, bool(t.when_to_use)) for t in r.all()]"
mikumikubeam True
ddoslayer True
slowloris True
mhddos True
impulse True
pyddos True
overload True
ufonet True
```

Testes específicos:

```text
$ cd backend && /home/grekas/Projetos/VerificadordeSegurança/VerificaLab/.venv/bin/python -m pytest tests/test_registry.py -v
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/grekas/Projetos/VerificadordeSegurança/VerificaLab/backend
configfile: pytest.ini
plugins: anyio-4.15.1
collected 25 items

tests/test_registry.py .........................                         [100%]

============================== 25 passed in 0.35s ==============================
```

Suíte global:

```text
$ cd backend && /home/grekas/Projetos/VerificadordeSegurança/VerificaLab/.venv/bin/python -m pytest tests -q -o addopts=''
........................................................................ [ 54%]
...........................................................              [100%]
=============================== warnings summary ===============================
tests/test_api_data.py::test_log_upload_parse_and_correlation
  /home/grekas/Projetos/VerificadordeSegurança/VerificaLab/.venv/lib/python3.14/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
131 passed, 1 warning in 24.32s
```
