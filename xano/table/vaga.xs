table "vaga" {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    int numero
    enum tipo?="Carro" { values = ["Carro", "Moto"] }
    enum status?="LIVRE" { values = ["LIVRE", "OCUPADA"] }
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "numero"}]}
  ]
}
