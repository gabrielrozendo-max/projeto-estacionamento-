table "usuario" {
  auth = true
  schema {
    int id
    timestamp created_at?=now
    text nome filters=trim
    email email filters=trim|lower { sensitive = true }
    password password { sensitive = true }
    enum tipo?="OPERADOR" { values = ["ADMIN", "OPERADOR"] }
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "email"}]}
  ]
}
