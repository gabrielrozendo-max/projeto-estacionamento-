# API Endpoint: PUT /tarifas
# Description: Atualiza a tabela de tarifas do estacionamento

input {
  hora_inicial: decimal?
  hora_adicional: decimal?
  tolerancia_minutos: integer?
}

query UpdateTarifas {
  db.find_first("tarifas") {
    output = "tarifa_atual"
  }
  
  db.patch("tarifas", $tarifa_atual.id) {
    data = {
      hora_inicial: $input.hora_inicial,
      hora_adicional: $input.hora_adicional,
      tolerancia_minutos: $input.tolerancia_minutos
    }
    output = "tarifa_atualizada"
  }

  return $tarifa_atualizada
}
