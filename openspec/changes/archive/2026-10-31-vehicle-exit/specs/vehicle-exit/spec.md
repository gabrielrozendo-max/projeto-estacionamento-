## ADDED Requirements

### Requirement: Vehicle exit is calculated by Xano

The Flask application MUST proxy a vehicle exit to Xano and MUST NOT calculate
parking duration, choose the tariff, round billing time, or mutate parking
records locally.

#### Scenario: Operator requests a vehicle exit

- **WHEN** a client sends a valid plate to `POST /api/exits`
- **THEN** Flask MUST trim and uppercase the plate
- **AND** Flask MUST send `{"plate": "<NORMALIZED_PLATE>"}` as JSON to Xano
  `POST /exits`
- **AND** Flask MUST preserve the upstream successful HTTP status and JSON body

#### Scenario: Xano returns a fee

- **WHEN** Xano returns a successful exit response containing `total_cents`
- **THEN** Flask MUST return that amount unchanged to the client
- **AND** Flask MUST NOT recalculate or transform the amount

### Requirement: Exit keeps the parking space occupied until payment

An exit MUST NOT decrement `occupied_spaces`. A record in
`Aguardando Pagamento` continues to occupy a space until payment confirmation
transitions it to `Concluído`.

#### Scenario: Exit has produced a pending payment

- **WHEN** Xano processes an exit and the record becomes
  `Aguardando Pagamento`
- **THEN** the occupancy count MUST remain unchanged
- **AND** Flask MUST NOT issue a separate occupancy update

### Requirement: Exit errors remain explicit

Flask MUST reject invalid exit requests before making an upstream request and
MUST return structured errors when Xano responds with an error or cannot be
reached.

#### Scenario: Plate is missing or invalid

- **WHEN** the request body is not a valid JSON object or contains no non-empty
  plate
- **THEN** Flask MUST return a structured client error
- **AND** MUST NOT contact Xano

#### Scenario: Xano rejects the exit

- **WHEN** Xano returns an HTTP error or a network failure occurs
- **THEN** Flask MUST return the existing structured error response
- **AND** MUST NOT present the operation as successful
