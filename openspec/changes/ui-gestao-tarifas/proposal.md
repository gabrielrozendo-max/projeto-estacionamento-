# Proposal: Interface Web para Gestão de Tarifas

## Contexto
A Change 5 disponibilizou os endpoints proxy `/api/tarifas` no Flask. É necessário integrar estes endpoints ao frontend web para permitir a consulta e alteração das tarifas pela interface do operador.

## Alterações Propostas
- Adicionar painel/modal de Tarifas no `templates/index.html`.
- Criar script JS para consumo assíncrono de `GET` e `PUT /api/tarifas`.
- Adicionar testes de renderização no `tests/test_app.py`.
