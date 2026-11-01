# Proposal: Gestão de Tarifas

## Contexto
O sistema de estacionamento requer um módulo dedicado para configuração e consulta dinâmica das regras de tarifação (valor da hora inicial, hora adicional, tempo de tolerância em minutos e valor máximo diário), eliminando valores fixos no código.

## Escopo
1. Mapeamento e estruturação da tabela/regras de tarifas no Xano.
2. Endpoints proxy no Flask (`GET /api/tarifas` e `PUT /api/tarifas`).
3. Integração do cálculo tarifário do fluxo de saída com os parâmetros do Xano.
4. Cobertura de testes automatizados via `pytest`.
