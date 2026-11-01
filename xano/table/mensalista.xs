table "mensalista" {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    int veiculo_id { table = "veiculo" }
    text nome filters=trim
    text telefone?
    decimal valor_mensalidade filters=min:0
    date data_inicio
    date data_fim
    enum status?="ATIVO" { values = ["ATIVO", "INATIVO", "VENCIDO"] }
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "veiculo_id"}]}
    {type: "btree", field: [{name: "status"}]}
  ]
}
