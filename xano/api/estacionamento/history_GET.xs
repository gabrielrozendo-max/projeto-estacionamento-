query "history" verb=GET {
  api_group = "Estacionamento"
  description = "Lista o histórico de movimentações do estacionamento"
  input {
  }
  stack {
    db.query "movimentacao" {
      join = {
        veiculo: {
          table: "veiculo",
          type: "inner",
          where: $db.movimentacao.veiculo_id == $db.veiculo.id
        },
        vaga: {
          table: "vaga",
          type: "inner",
          where: $db.movimentacao.vaga_id == $db.vaga.id
        }
      }
      eval = {
        id: $db.movimentacao.id,
        placa: $db.veiculo.placa,
        vaga_numero: $db.vaga.numero,
        entrada: $db.movimentacao.entrada,
        saida: $db.movimentacao.saida,
        valor: $db.movimentacao.valor,
        status_pagamento: $db.movimentacao.status_pagamento
      }
      sort = { entrada: "desc" }
      return = {
        type: "list",
        paging: { page: 1, per_page: 50 }
      }
    } as $history
  }
  response = $history.items
  guid = "_HdW3gk1b9lnm4Fx0K-pESbY0M4"
}
