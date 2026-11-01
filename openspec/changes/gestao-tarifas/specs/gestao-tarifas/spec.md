# Specification: Gestão de Tarifas

## Requirements
- **REQ-01**: O endpoint `GET /api/tarifas` deve retornar a estrutura de preços vigente (hora_inicial, hora_adicional, tolerancia_minutos).
- **REQ-02**: O cálculo da cobrança na saída do veículo deve consultar os parâmetros atualizados de tarifa.
- **REQ-03**: O endpoint `PUT /api/tarifas` deve permitir atualizar os parâmetros no Xano com validação de tipos numéricos positivos.

## Scenarios
- **Cenário 1**: Consulta de Tarifa Vigente retorna HTTP 200 com a estrutura de preços.
- **Cenário 2**: Atualização de Tarifa com valores válidos persiste no Xano e altera o valor cobrado na saída.
