query entries verb=POST {
  api_group = "Estacionamento"

  input {
    text plate? filters=trim
    text vehicle_type? filters=trim
  }

  stack {
    db.get parking_capacity {
      field_name = "id"
      field_value = 1
    } as $parking_capacity1
  
    db.edit parking_capacity {
      field_name = "id"
      field_value = 1
      data = {occupied_spaces: $parking_capacity1.occupied_spaces|add:1}
    } as $parking_capacity2
  }

  response = $parking_capacity1
  guid = "m6ocAJAzjIPTrmPokajp4SxTSBA"
}