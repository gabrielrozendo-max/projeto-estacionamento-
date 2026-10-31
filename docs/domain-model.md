# Modelo de Domínio: Sistema de Estacionamento

## 1. Entidades Principais

**Veículo**
* `Matrícula`: Identificador único (String/Texto).
* `Tipo`: Categoria, ex: Carro, Mota (Enum/Opção).

**Registo de Estacionamento**
* `HoraEntrada`: Data e hora exata da chegada (DateTime).
* `HoraSaida`: Data e hora da partida (DateTime, nulo enquanto estacionado).
* `Estado`: "Estacionado", "Aguardando Pagamento", "Concluído" (Enum/Opção).
* `ValorTotal`: Montante calculado na saída (Decimal/Moeda).

**Tarifa**
* `TipoVeiculo`: Relaciona o valor com a categoria do veículo.
* `PrecoHora`: Custo por hora de permanência (Decimal/Moeda).

**Parque/Lotação**
* `CapacidadeMaxima`: Número total de lugares (Inteiro).
* `LugaresOcupados`: Contagem em tempo real (Inteiro).

## 2. Regras de Negócio
* **Cálculo de Pagamento:** O valor é calculado no momento da saída, multiplicando as horas (ou frações) de permanência pelo `PrecoHora` correspondente ao tipo de veículo.
* **Controlo de Lotação:** O sistema deve alertar ou impedir o registo de novas entradas caso os `LugaresOcupados` atinjam a `CapacidadeMaxima`.
* **Fluxo de Saída:** O estado do registo só passa a "Concluído" após a confirmação do pagamento.