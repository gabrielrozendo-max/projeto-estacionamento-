# Proposal: Histórico de Movimentações no Dashboard

## Contexto
O operador necessita de uma visualização clara das entradas, saídas e valores arrecadados para acompanhamento operacional do estacionamento.

## Alterações Propostas
- Criar rota proxy `GET /api/history` no `app.py`.
- Adicionar painel com tabela de histórico no `templates/index.html`.
- Adicionar testes de integração no `tests/test_app.py`.
