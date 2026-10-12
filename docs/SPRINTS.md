# Sprints — Orquestração de stress test

| Sprint | Escopo | Status | Evidência |
|---|---|---|---|
| 0 | Preparar branch, estrutura inicial e tracker sem alterar o catálogo existente | Concluído | `python -m pytest tests -q -o addopts=''`: `87 passed in 23.79s`; `git diff --exit-code -- backend/verificalab/catalog.py`: sem diferenças |
| 1 | Definir autorização explícita dos alvos | Concluído | 19 testes específicos e 106 testes globais passaram; execução manual libera loopback e rejeita alvo externo sem arquivo de autorização (evidências detalhadas abaixo) |
| 2 | Catalogar as ferramentas em `backend/config/tools.yaml` | Não iniciado | — |
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
