# Especificação do Backend Xano

## 1. Objetivo e convenções

Este documento define o modelo de dados, as regras de negócio e os contratos REST
para configurar o backend na plataforma Xano. O Xano é a única camada de
persistência e backend; a aplicação cliente comunica com esta API por HTTPS e
troca exclusivamente JSON (`application/json`).

Os nomes de tabelas, campos, estados e propriedades JSON são escritos em inglês.
Os termos em Português entre parênteses identificam o conceito correspondente
no modelo de domínio.

- Todas as datas são instantes ISO 8601 em UTC, por exemplo
  `2026-10-30T20:00:00.000Z`.
- Os valores monetários são inteiros em cêntimos. `hourly_price_cents` representa
  o preço de uma hora; `total_amount_cents` representa o total a cobrar.
- Os identificadores `id` são gerados pelo Xano como chaves técnicas. Não
  representam novos conceitos do domínio.
- Os caminhos abaixo são relativos ao grupo/base URL da API Xano configurada
  para este sistema.

## 2. Schema das tabelas

### `tariffs` (Tarifa)

| Campo | Tipo Xano | Restrições | Descrição |
|---|---|---|---|
| `id` | Integer, gerado | Chave primária | Identificador técnico Xano. |
| `vehicle_type` | Text | Obrigatório, único | Categoria do veículo, por exemplo `Carro` ou `Mota`. |
| `hourly_price_cents` | Integer | Obrigatório, >= 0 | Preço por hora em cêntimos. |

Cada tipo de veículo usado em entradas tem exatamente uma tarifa configurada.

### `vehicles` (Veículo)

| Campo | Tipo Xano | Restrições | Descrição |
|---|---|---|---|
| `id` | Integer, gerado | Chave primária | Identificador técnico Xano. |
| `plate` | Text | Obrigatório, único, não vazio | Matrícula normalizada. |
| `vehicle_type` | Text ou relação | Obrigatório; corresponde a `tariffs.vehicle_type` | Categoria do veículo. |

Normalizar a matrícula removendo espaços nas extremidades e convertendo letras
para maiúsculas antes de a guardar ou pesquisar.

### `parking_records` (Registo de Estacionamento)

| Campo | Tipo Xano | Restrições | Descrição |
|---|---|---|---|
| `id` | Integer, gerado | Chave primária | Identificador do registo, usado na confirmação do pagamento. |
| `vehicle_id` | Relation para `vehicles` | Obrigatório | Veículo associado ao registo. |
| `entry_at` | DateTime | Obrigatório | Instante de entrada. |
| `exit_at` | DateTime | Nulo enquanto estacionado | Instante de saída calculado pelo backend. |
| `status` | Enum/Text | Obrigatório; valores permitidos abaixo | Estado do registo. |
| `total_amount_cents` | Integer | Nulo enquanto estacionado; >= 0 quando calculado | Total calculado na saída. |

Valores permitidos para `status`:

- `Estacionado`
- `Aguardando Pagamento`
- `Concluído`

Uma matrícula só pode ter um registo no estado `Estacionado` de cada vez. Um
registo em `Aguardando Pagamento` continua a ocupar um lugar até à confirmação
do pagamento. Depois de concluído, o registo mantém-se para histórico.

### `parking_capacity` (Parque/Lotação)

| Campo | Tipo Xano | Restrições | Descrição |
|---|---|---|---|
| `id` | Integer, gerado | Chave primária | Identificador técnico Xano. |
| `max_capacity` | Integer | Obrigatório, > 0 | Capacidade máxima do parque. |
| `occupied_spaces` | Integer | Obrigatório, >= 0 e <= `max_capacity` | Lugares atualmente ocupados. |

Esta tabela contém uma única configuração ativa para o parque. Inicializar essa
linha antes de aceitar entradas. `occupied_spaces` conta registos
`Estacionado` **e** `Aguardando Pagamento`.

## 3. Regras de negócio e consistência

### Entradas

1. Validar `plate` e `vehicle_type`; normalizar a matrícula.
2. Confirmar que existe uma tarifa para o tipo de veículo.
3. Confirmar que a matrícula não tem já um registo `Estacionado`.
4. Confirmar que existe configuração de lotação e que
   `occupied_spaces < max_capacity`.
5. Criar ou reutilizar o veículo e criar um registo com `entry_at` no instante
   UTC atual, estado `Estacionado`, `exit_at = null` e
   `total_amount_cents = null`.
6. Incrementar `occupied_spaces`.
7. As verificações e escritas têm de ser atómicas ou serializadas no Xano para
   que pedidos concorrentes não ultrapassem a capacidade nem criem entradas
   duplicadas para a mesma matrícula.

### Saídas e arredondamento

1. Localizar o registo `Estacionado` pela matrícula normalizada. Se não existir,
   devolver `404`.
2. O instante de saída é determinado pelo backend em UTC.
3. Calcular a duração em milissegundos:

   `duration_ms = exit_at - entry_at`

4. Rejeitar uma duração negativa com `400`. A duração zero é válida e resulta
   numa cobrança de zero horas.
5. Arredondar **cada fração de hora para cima**:

   `billable_hours = ceil(duration_ms / 3_600_000)`

   Exemplos: 1 hora exata = 1 hora faturada; 1 hora e 5 minutos = 2 horas
   faturadas; 1 minuto = 1 hora faturada.
6. Calcular o total usando inteiros:

   `total_amount_cents = billable_hours * hourly_price_cents`

   Rejeitar resultados fora do intervalo de inteiros seguros suportado pelo
   Xano. Não calcular nem transportar o montante como ponto flutuante decimal.
7. Guardar `exit_at`, `total_amount_cents` e estado `Aguardando Pagamento`.
   **Não** reduzir `occupied_spaces` nesta operação: a vaga só é libertada
   quando o pagamento for confirmado.
8. A atualização do registo e a leitura da tarifa devem ser consistentes; não
   aceitar um registo sem tarifa válida para o tipo de veículo.

### Confirmação de pagamento

1. Localizar o registo pelo `record_id`.
2. Só permitir a transição de `Aguardando Pagamento` para `Concluído`.
3. Reduzir `occupied_spaces` exatamente uma vez, na mesma operação lógica da
   transição. Confirmar que a lotação é maior que zero; caso contrário, devolver
   erro de inconsistência sem concluir o registo.
4. Não alterar `total_amount_cents`: o valor devido foi calculado e guardado na
   saída. O endpoint confirma a liquidação desse valor; não recebe nem define
   um método, referência ou montante de pagamento, pois esses dados não fazem
   parte do modelo de domínio atual.
5. Pedidos repetidos para um registo já `Concluído` não podem libertar lugares
   novamente; devolver `409`.

## 4. Endpoints REST

Todos os pedidos e respostas com corpo usam `application/json`. Os erros têm o
formato comum:

```json
{
  "error": {
    "code": "PARKING_FULL",
    "message": "O parque está lotado."
  }
}
```

### `POST /entries` — registar entrada

Pedido:

```json
{
  "plate": "AA-00-AA",
  "vehicle_type": "Carro"
}
```

Resposta `201 Created`:

```json
{
  "data": {
    "id": 101,
    "plate": "AA-00-AA",
    "vehicle_type": "Carro",
    "entry_at": "2026-10-30T20:00:00.000Z",
    "status": "Estacionado"
  },
  "occupancy": {
    "occupied_spaces": 12,
    "max_capacity": 50
  }
}
```

Erros previstos: `400` (`INVALID_REQUEST`, `UNKNOWN_VEHICLE_TYPE`), `409`
(`PARKING_FULL`, `VEHICLE_ALREADY_PARKED`) e `503`
(`PARKING_NOT_CONFIGURED`).

### `POST /exits` — calcular saída e valor a pagar

Pedido:

```json
{
  "plate": "AA-00-AA"
}
```

Resposta `200 OK`:

```json
{
  "data": {
    "id": 101,
    "plate": "AA-00-AA",
    "vehicle_type": "Carro",
    "entry_at": "2026-10-30T18:55:00.000Z",
    "exit_at": "2026-10-30T20:00:00.000Z",
    "status": "Aguardando Pagamento",
    "total_cents": 200
  },
  "occupancy": {
    "occupied_spaces": 12
  }
}
```

O exemplo pressupõe uma tarifa de 100 cêntimos por hora; 1 hora e 5 minutos
correspondem a 2 horas faturadas. A ocupação permanece inalterada enquanto o
pagamento estiver pendente.

Erros previstos: `400` (`INVALID_REQUEST`, `EXIT_BEFORE_ENTRY`), `404`
(`ACTIVE_PARKING_RECORD_NOT_FOUND`) e `409` (`PARKING_RECORD_CHANGED`).

### `POST /payments/confirm` — confirmar pagamento

Pedido:

```json
{
  "record_id": 101
}
```

Resposta `200 OK`:

```json
{
  "data": {
    "record_id": 101,
    "plate": "AA-00-AA",
    "status": "Concluído",
    "total_cents": 200
  },
  "occupancy": {
    "occupied_spaces": 11,
    "max_capacity": 50
  }
}
```

Erros previstos: `400` (`INVALID_REQUEST`), `404`
(`PARKING_RECORD_NOT_FOUND`), `409` (`PAYMENT_NOT_PENDING`,
`OCCUPANCY_INCONSISTENT`).

### `GET /status` — consultar lotação

Não requer corpo. A resposta é calculada a partir da configuração única de
`parking_capacity`.

Resposta `200 OK`:

```json
{
  "max_capacity": 50,
  "occupied_spaces": 11,
  "available_spaces": 39
}
```

Devolver `503` (`PARKING_NOT_CONFIGURED`) se a configuração da lotação estiver
ausente.

## 5. Códigos e validações comuns

- `400 Bad Request`: JSON inválido, campos obrigatórios ausentes ou inválidos,
  duração negativa ou identificador inválido.
- `404 Not Found`: veículo/registo ativo ou registo para pagamento inexistente.
- `409 Conflict`: parque cheio, matrícula já estacionada, transição de estado
  inválida ou conflito de concorrência.
- `500 Internal Server Error`: falha inesperada ou inconsistência interna; não
  expor detalhes internos da plataforma ao cliente.
- `503 Service Unavailable`: configuração inicial do parque em falta.

Validar todos os dados novamente nas Function Stacks do Xano; a validação do
cliente serve apenas para melhorar a experiência e não substitui a validação do
backend.

## 6. Critérios de aceitação

- Não é criada uma entrada quando o parque está cheio, mesmo com pedidos
  simultâneos.
- A mesma matrícula não pode ter dois registos `Estacionado`.
- Uma saída calcula frações de hora com arredondamento para cima e guarda o
  montante em cêntimos inteiros.
- A saída muda o estado para `Aguardando Pagamento`, sem libertar a vaga.
- Só a confirmação de pagamento muda o estado para `Concluído` e liberta a vaga,
  uma única vez.
- `GET /status` devolve valores coerentes com a configuração da lotação.
- Todos os endpoints devolvem JSON, incluindo erros de validação e de negócio.
