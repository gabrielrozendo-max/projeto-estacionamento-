table "veiculo" {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    text placa filters=trim|upper
    text modelo?
    text cor?
    enum tipo?="Carro" { values = ["Carro", "Moto"] }
    bool mensalista?=false
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "placa"}]}
  ]
  guid = "w_7jmK2T6KIsnrBo0ICc9YL290E"
}
