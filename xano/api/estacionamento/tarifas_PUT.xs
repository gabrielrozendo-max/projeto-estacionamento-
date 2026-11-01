query "tarifas" verb=PUT {
  api_group = "Estacionamento"
  description = "Atualiza a tarifa atual (apenas campos enviados)"
  input {
    decimal hora_inicial? filters=min:0
    decimal hora_adicional? filters=min:0
    int tolerancia_minutos? filters=min:0
  }
  stack {
    db.query "tarifa" {
      return = { type: "single" }
    } as $tarifa

    precondition ($tarifa != null) {
      error_type = "notfound"
      error = "Tarifa não encontrada"
    }

    var $updates { value = {} }

    conditional {
      if ($input.hora_inicial != null) {
        var.update $updates { value = $updates|set:"hora_inicial":$input.hora_inicial }
      }
    }
    conditional {
      if ($input.hora_adicional != null) {
        var.update $updates { value = $updates|set:"hora_adicional":$input.hora_adicional }
      }
    }
    conditional {
      if ($input.tolerancia_minutos != null) {
        var.update $updates { value = $updates|set:"tolerancia_minutos":$input.tolerancia_minutos }
      }
    }

    precondition (($updates|is_empty) == false) {
      error = "Nenhuma atualização fornecida"
    }

    db.patch "tarifa" {
      field_name = "id"
      field_value = $tarifa.id
      data = $updates
    } as $updated_tarifa
  }
  response = $updated_tarifa
}
