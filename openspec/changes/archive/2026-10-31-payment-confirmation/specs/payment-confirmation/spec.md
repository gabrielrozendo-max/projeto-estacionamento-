## ADDED Requirements

### Requirement: Flask proxies payment confirmation to Xano

Flask MUST validate the record identifier and proxy payment confirmation to
Xano. Flask MUST NOT mutate parking records or occupancy locally.

#### Scenario: Confirm a pending payment

- **WHEN** a client sends a positive integer `record_id` to
  `POST /api/payments/confirm`
- **THEN** Flask MUST send `{"record_id": <id>}` as JSON to Xano
  `POST /payments/confirm`
- **AND** Flask MUST preserve the upstream successful status and JSON body
- **AND** the response MUST report the resulting record status and occupancy
  supplied by Xano

#### Scenario: Invalid record identifier

- **WHEN** the request body is invalid or `record_id` is not a positive
  integer, including a boolean
- **THEN** Flask MUST return a structured client error
- **AND** MUST NOT contact Xano

### Requirement: Xano completes pending payment and releases occupancy once

Xano MUST change a record only from `Aguardando Pagamento` to `Concluído` and
decrement `occupied_spaces` exactly once in the same logical atomic operation.

#### Scenario: First confirmation of a pending payment

- **WHEN** Xano receives confirmation for a record in
  `Aguardando Pagamento`
- **THEN** it MUST set the record status to `Concluído`
- **AND** it MUST decrement `occupied_spaces` by exactly one
- **AND** it MUST preserve the amount calculated at exit

#### Scenario: Duplicate or invalid-state confirmation

- **WHEN** Xano receives confirmation for a completed record or a record not
  awaiting payment
- **THEN** it MUST return a conflict
- **AND** it MUST NOT decrement occupancy again

#### Scenario: Occupancy is inconsistent

- **WHEN** the record is pending but `occupied_spaces` is less than one
- **THEN** Xano MUST return an inconsistency error
- **AND** MUST NOT complete the record

### Requirement: Confirmation failures remain explicit

Flask MUST return structured errors when Xano rejects the confirmation or
cannot be reached.

#### Scenario: Xano returns an HTTP error or network failure

- **WHEN** the upstream confirmation fails
- **THEN** Flask MUST return the existing structured error response
- **AND** MUST NOT report payment as confirmed
