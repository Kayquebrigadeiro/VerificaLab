# Sprints — Orquestração de stress test

| Sprint | Escopo | Status | Evidência |
|---|---|---|---|
| 0 | Preparar branch, estrutura inicial e tracker sem alterar o catálogo existente | Concluído | `python -m pytest tests -q -o addopts=''`: `87 passed in 23.79s`; `git diff --exit-code -- backend/verificalab/catalog.py`: sem diferenças |
| 1 | Definir autorização explícita dos alvos | Concluído | 19 testes específicos e 106 testes globais passaram; execução manual libera loopback e rejeita alvo externo sem arquivo de autorização (evidências detalhadas abaixo) |
| 2 | Catalogar as ferramentas em `backend/config/tools.yaml` e carregar o registro tipado | Concluído | 8 ferramentas carregadas; 25 testes do registry e 131 testes globais passaram |
| 3 | Implementar runner seguro de subprocessos com encerramento em árvore | Concluído | 12 testes específicos passaram; timeout manual matou o grupo; grep sem ocorrências; suíte global passou |
| 4 | Adapter real Slowloris e teste E2E no laboratório local | Concluído | 9 testes do adapter, execução real em `127.0.0.1:8477` com `returncode=0` e suíte global com 152 testes |
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

## Evidências do Sprint 3

`core.runner.run_subprocess()` exige comando em lista, valida diretório contra
raízes permitidas, inicia sessão/grupo próprio, usa ambiente mínimo com `PATH`
explícito, drena stdout/stderr concorrentemente sob limite agregado de 1 MB e
encerra o grupo em timeout ou cancelamento. `RunResult` inclui horários UTC,
código de retorno, saídas capturadas e flags de timeout, cancelamento e
truncamento.

Testes específicos:

```text
$ cd backend && python -m pytest tests/test_runner.py -v
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/grekas/Projetos/VerificadordeSegurança/VerificaLab/backend
configfile: pytest.ini
plugins: anyio-4.12.1, typeguard-4.4.4
collected 12 items

tests/test_runner.py ............                                        [100%]

============================== 12 passed in 2.60s ==============================
```

Verificação manual de timeout e processo filho:

```text
$ cd backend && python -c "from verificalab.core.runner import run_subprocess; r=run_subprocess(['bash','-c','sleep 30 & wait'], cwd='.', timeout_s=2); print(r)"
RunResult(started_at=datetime.datetime(2026, 10, 12, 17, 30, 38, 12375, tzinfo=datetime.timezone.utc), ended_at=datetime.datetime(2026, 10, 12, 17, 30, 40, 18593, tzinfo=datetime.timezone.utc), returncode=-15, stdout='', stderr='', timeout=True, cancelled=False, truncated=False)
$ ps aux | grep 'sleep 30' | grep -v grep
(sem saída; nenhum processo encontrado)
```

Busca por invocação de shell:

```text
$ grep -rn "shell=True" backend/verificalab/
(sem saída; grep retornou 1 por não encontrar correspondências)
```

Suíte global:

```text
$ cd backend && python -m pytest tests -q
........................................................................ [ 50%]
.......................................................................  [100%]
```

O comando global terminou com código 0.

## Evidências do Sprint 4

Implementados `StressRequest`, `StressAdapter` e `StressResult` (alias do
`RunResult` do runner), além do `SlowlorisAdapter`. Os limites máximos são
declarados em `tools.yaml` (30 s e 50 sockets), validados pelo registry e
aplicados sem elevar valores menores. O adapter chama
`require_authorization()` antes da construção/execução do comando, recusa
opções upstream fora da allowlist e só permite o caminho `/`, pois o Slowloris
original não oferece configuração de caminho nem duração. O original permaneceu
inalterado; um supervisor temporizado encerra o processo ao final da duração,
com o timeout do runner como limite de segurança adicional.

O lab registra conexões TCP antes de receber cabeçalhos completos e trata
desconexões do teste como parte normal do ciclo. `backend/tests/fixtures/local_http.py`
reusa o fixture do laboratório da suíte.

Testes específicos:

```text
$ cd backend && python -m pytest tests/test_adapter_slowloris.py -v
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/grekas/Projetos/VerificadordeSegurança/VerificaLab/backend
configfile: pytest.ini
plugins: anyio-4.12.1, typeguard-4.4.4
collected 9 items

tests/test_adapter_slowloris.py .........                                [100%]

============================== 9 passed in 3.68s ==============================
```

Execução real contra o laboratório local:

```text
LAB: {'running': True, 'pid': 217263, 'endpoint': 'http://127.0.0.1:8477', 'managed_by': 'verificalab', 'message': 'lab iniciado'}
RunResult: RunResult(started_at=datetime.datetime(2026, 10, 12, 17, 38, 20, 392820, tzinfo=datetime.timezone.utc), ended_at=datetime.datetime(2026, 10, 12, 17, 38, 23, 450108, tzinfo=datetime.timezone.utc), returncode=0, stdout='', stderr='[12-10-2026 14:38:20] Attacking 127.0.0.1 with 10 sockets.\n[12-10-2026 14:38:20] Creating sockets...\n[12-10-2026 14:38:21] Sending keep-alive headers...\n[12-10-2026 14:38:21] Socket count: 10\n', timeout=False, cancelled=False, truncated=False)
LAB_STOP: {'running': False, 'pid': None, 'endpoint': 'http://127.0.0.1:8477', 'managed_by': None, 'message': 'lab encerrado'}
LAB_LOG_TAIL:
[lab] TCP 127.0.0.1
[lab] TCP 127.0.0.1
[lab] GET /[lab] GET /
[lab] GET /[lab] GET /
[lab] GET /
[lab] GET /
[lab] GET /

[lab] GET /[lab] GET /

[lab] GET /
```

Suíte global, comando solicitado:

```text
$ cd backend && python -m pytest tests -q
........................................................................ [ 47%]
........................................................................ [ 94%]
........                                                                 [100%]
```

O comando terminou com código 0. Para obter a contagem final sem o `addopts`
quiet do projeto:

```text
$ cd backend && python -m pytest tests -q -o addopts=''
........................................................................ [ 47%]
........................................................................ [ 94%]
........                                                                 [100%]
152 passed in 31.21s
```
