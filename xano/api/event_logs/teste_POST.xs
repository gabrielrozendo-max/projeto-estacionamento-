// Add teste record
query teste verb=POST {
  api_group = "Event Logs"

  input {
    dblink {
      table = ""
    }
  }

  stack {
    db.add "" {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $teste
  }

  response = $teste
  guid = "Bxx5nNH7_a6ACBOKwe27I5CCd_g"
}