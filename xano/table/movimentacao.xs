table "movimentacao" {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    int veiculo_id { table = "veiculo" }
    int vaga_id { table = "vaga" }
    int usuario_id? { table = "usuario" }
    timestamp entrada?=now
    timestamp saida?
    decimal valor? filters=min:0
    enum status_pagamento?="PENDENTE" { values = ["PENDENTE", "PAGO"] }
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "veiculo_id"}]}
    {type: "btree", field: [{name: "vaga_id"}]}
    {type: "btree", field: [{name: "usuario_id"}]}
    {type: "btree", field: [{name: "status_pagamento"}]}
  ]
  guid = "0e81py3y3lFtCq0qOXB_320WSK0"
}
