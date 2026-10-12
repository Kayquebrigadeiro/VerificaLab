# Sprints — Orquestração de stress test

| Sprint | Escopo | Status | Evidência |
|---|---|---|---|
| 0 | Preparar branch, estrutura inicial e tracker sem alterar o catálogo existente | Concluído | `python -m pytest tests -q -o addopts=''`: `87 passed in 23.79s`; `git diff --exit-code -- backend/verificalab/catalog.py`: sem diferenças |
| 1 | Definir autorização explícita dos alvos | Não iniciado | — |
| 2 | Catalogar as ferramentas em `backend/config/tools.yaml` | Não iniciado | — |
| 3 | Implementar adaptadores das ferramentas de stress test | Não iniciado | — |
| 4 | Orquestrar execuções autorizadas | Não iniciado | — |
| 5 | Integrar resultados e métricas | Não iniciado | — |
| 6 | Integrar fluxos de interface TUI | Não iniciado | — |
| 7 | Cobrir fluxos e limites com testes | Não iniciado | — |
| 8 | Validar documentação e execução integrada | Não iniciado | — |
