table parking_capacity {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int max_capacity?
    int occupied_spaces?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  guid = "PaRzAGajfE17CaXgitYVPkJS0bM"
}