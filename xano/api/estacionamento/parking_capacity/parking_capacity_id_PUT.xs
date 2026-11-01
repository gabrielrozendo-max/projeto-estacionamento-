// Update parking_capacity record
query "parking_capacity/{parking_capacity_id}" verb=PUT {
  api_group = "Estacionamento"

  input {
    int parking_capacity_id? filters=min:1
    dblink {
      table = "parking_capacity"
    }
  }

  stack {
    db.edit parking_capacity {
      field_name = "id"
      field_value = $input.parking_capacity_id
      enforce_hidden_fields = false
      data = {
        max_capacity   : $input.max_capacity
        occupied_spaces: $input.occupied_spaces
      }
    } as $model
  }

  response = $model
  guid = "deFbgrVj_3Zw7U8jGS1gJiin0D8"
}