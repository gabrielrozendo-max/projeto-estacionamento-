# Spec: Histórico de Movimentações

## Requisitos
1. A rota `GET /api/history` deve retransmitir a requisição ao Xano e retornar a lista de registros.
2. A interface web deve exibir a tabela `#historico-table` com as colunas: Placa, Entrada, Saída, Valor e Status.
3. O carregamento do histórico deve ocorrer no evento `DOMContentLoaded` e ao registrar entrada/saída.
