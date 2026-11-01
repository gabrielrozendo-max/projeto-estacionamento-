query status verb=GET {
  api_group = "Estacionamento"

  input {
  }

  stack {
    db.get parking_capacity {
      field_name = "id"
      field_value = 1
    } as $parking_capacity1
  
    var $available_spaces {
      value = $parking_capacity1.max_capacity
        |subtract:$parking_capacity1.occupied_spaces
    }
  }

  response = $parking_capacity1
  guid = "7uC7dbcLUCknAH5pcNnmS727B08"
}