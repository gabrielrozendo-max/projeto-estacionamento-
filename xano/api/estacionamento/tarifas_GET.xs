# API Endpoint: GET /tarifas
# Description: Retorna a tabela de tarifas atual do estacionamento

query GetTarifas {
  db.find_first("tarifas") {
    output = "tarifa"
  }
  return $tarifa
}
