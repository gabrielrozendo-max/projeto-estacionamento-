## ADDED Requirements

### Requirement: Flask proxy preserves the Xano API contracts

The Flask application MUST proxy the existing status, entry, exit, and payment
confirmation routes to their corresponding Xano endpoints using JSON, without
reimplementing Xano business rules or adding routes in this change.

#### Scenario: Status is requested

- **WHEN** a client requests `GET /api/status`
- **THEN** Flask MUST request `GET /status` from Xano
- **AND** it MUST return the upstream JSON body and successful status code

#### Scenario: Entry, exit, or payment is submitted

- **WHEN** a client submits an existing entry, exit, or payment request
- **THEN** Flask MUST forward the corresponding Xano contract payload to
  `/entries`, `/exits`, or `/payments/confirm`
- **AND** it MUST preserve the upstream successful status and JSON body

#### Scenario: Xano returns an HTTP or network error

- **WHEN** an upstream request fails
- **THEN** Flask MUST return a structured JSON error
- **AND** it MUST NOT report a failed upstream request as a success
