# Spec: Interface Web para Gestão de Tarifas

## Requisitos de Interface e Comportamento
1. O formulário `#tarifa-form` deve conter inputs numéricos com os atributos `min="0"` e `step="0.01"`.
2. O evento `DOMContentLoaded` deve disparar a leitura inicial dos valores vigentes via `GET /api/tarifas`.
3. A submissão do formulário deve desabilitar o botão de envio durante o processamento.
