query "tarifas" verb=GET {
  api_group = "Estacionamento"
  description = "Retorna o primeiro registro da tabela tarifa"
  input {
  }
  stack {
    db.query "tarifa" {
      return = { type: "single" }
    } as $tarifa
  }
  response = $tarifa
  guid = "SJtbuzXERa-tYqfc8UxzFZ2VMjw"
}
