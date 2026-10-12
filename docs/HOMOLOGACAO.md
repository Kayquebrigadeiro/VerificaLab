# Homologação local

Data da rodada: 11 de outubro de 2026.

## Resultado atual

| Área | Evidência | Estado |
| --- | --- | --- |
| Backend | 87 testes pytest concluídos | aprovado |
| Frontend | TypeScript e bundle Vite de produção | aprovado |
| Contratos HTTP | laboratório real, incluindo falha intencional e redirect externo bloqueado | aprovado |
| Carga leve | reserva global, limites, concorrência e cancelamento cobertos | aprovado |
| Runner pytest | processo real, JUnit, timeout e encerramento de filho | aprovado |
| Importadores | JUnit XML, JSON, JSONL e DDoSlayer JSON; entradas malformadas e XXE cobertas | aprovado |
| Segurança local | Host, Origin, CSRF, path traversal, XSS/sanitização e redação | aprovado por testes automatizados |
| Browser real | Chromium headless, viewports 1440×1000 e 390×844, API e assets reais | aprovado |

## Critérios observados

- Execução que contém falha intencional termina como `failed`.
- Perda de conexão é registrada como observação de contrato não atendido, sem derrubar o worker.
- Redirect para destino não cadastrado é interrompido antes da chamada seguinte.
- Valores acima dos limites de carga recebem resposta 422 em vez de serem ajustados silenciosamente.
- Cancelamento interrompe novos envios e encerra o grupo do subprocesso; o filho real não permanece órfão.
- Uma execução deixada ativa antes de reinício é recuperada como `interrupted`, nunca `passed`.
- Artefatos utilizam caminho gerado pelo backend; tentativas de escapar da raiz são recusadas.
- Dados sensíveis conhecidos são redigidos em evidências e relatórios.
- Correlações temporais declaram fuso, incerteza e natureza hipotética.
- A demonstração real do contrato persistiu 11 checks e 1 conjunto de
  métricas, exibiu as 2 falhas intencionais, terminou como `failed` e exportou
  um relatório HTML de 6.475 bytes.

## Inventário e remoção anterior

As oito ferramentas foram catalogadas por inspeção estática, sem executar mecanismos ofensivos. Na busca exata sob `/home/grekas/Projetos`, não foram localizados `planejador-local`, `Planejador_Local_v0.1.0.zip` ou `Planejamento_IA_Arquiteta_v0.1.md`; nada foi removido e nenhum processo atribuível ao planejador foi encerrado. Outros projetos permaneceram intocados.

## Repetição

Use um diretório descartável para a rodada:

```bash
tmpdir="$(mktemp -d)"
VERIFICALAB_DATA="$tmpdir" verificalab migrate
VERIFICALAB_DATA="$tmpdir" verificalab demo
VERIFICALAB_DATA="$tmpdir" python -m pytest -q backend/tests
```

O diretório temporário pode ser descartado depois da inspeção manual. A aplicação não o remove automaticamente.
