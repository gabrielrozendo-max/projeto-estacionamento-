table "tarifa" {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    decimal hora_inicial filters=min:0
    decimal hora_adicional filters=min:0
    int tolerancia_minutos?=0 filters=min:0
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
  ]
  guid = "nrxzZSc1p_dfi5cXKN2aY6Pz35o"
}
