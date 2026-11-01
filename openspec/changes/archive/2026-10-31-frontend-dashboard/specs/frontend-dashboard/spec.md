## ADDED Requirements

### Requirement: Dashboard uses the Flask API contracts

The browser dashboard MUST communicate with the existing Flask API and MUST
NOT call Xano directly or implement backend business rules.

#### Scenario: Operator performs a parking action

- **WHEN** the dashboard loads status or submits entry, exit, or payment
  confirmation
- **THEN** it MUST use `/api/status`, `/api/entries`, `/api/exits`, or
  `/api/payments/confirm` respectively
- **AND** it MUST use the documented HTTP method and JSON payload for that
  route

### Requirement: Dashboard reflects parking occupancy accurately

The dashboard MUST render valid occupied, available, and maximum-capacity
values and MUST communicate occupancy level using the documented thresholds.

#### Scenario: Occupancy is below 80 percent

- **WHEN** occupied capacity is below 80 percent
- **THEN** the indicator MUST use the available/green state

#### Scenario: Occupancy is from 80 percent to below full

- **WHEN** occupied capacity is at least 80 percent and less than 100 percent
- **THEN** the indicator MUST use the elevated/yellow state

#### Scenario: Occupancy reaches capacity

- **WHEN** occupied capacity is 100 percent
- **THEN** the indicator MUST use the full/red state
- **AND** the entry submission control MUST be disabled

#### Scenario: Status is unavailable or invalid

- **WHEN** the status request fails or returns invalid capacity values
- **THEN** the dashboard MUST show an unavailable/error state
- **AND** it MUST keep entry submission disabled until a valid refresh succeeds

### Requirement: Dashboard presents Xano-calculated exit fees

The dashboard MUST display the integer-cent fee returned by Xano without
recalculating duration, tariff, or rounding.

#### Scenario: Exit response contains a total in cents

- **WHEN** the exit response contains integer `total_cents`
- **THEN** the dashboard MUST format that amount as EUR using the Portuguese
  locale
- **AND** it MUST preserve cent precision

### Requirement: Dashboard reflects exit and payment state transitions

The dashboard MUST reflect that an exit leaves a record awaiting payment and
does not release occupancy until payment confirmation succeeds.

#### Scenario: Exit is awaiting payment

- **WHEN** the exit request succeeds
- **THEN** the dashboard MUST communicate that payment is pending
- **AND** it MUST refresh status without assuming a space was released

#### Scenario: Payment confirmation succeeds

- **WHEN** Xano confirms payment and returns the completed state
- **THEN** the dashboard MUST show a success message
- **AND** it MUST refresh status to reflect the occupancy returned after release

### Requirement: Dashboard reports operation failures accessibly

The dashboard MUST distinguish successful actions from failed requests and
show operator-readable messages for Flask/Xano errors, invalid responses, and
network failures.

#### Scenario: An API request fails

- **WHEN** a request returns an error or cannot be completed
- **THEN** the dashboard MUST show an error feedback message
- **AND** it MUST NOT present the operation as successful

### Requirement: Operator forms remain keyboard and screen-reader usable

The dashboard MUST retain Portuguese (`pt-PT`) operator-facing text, autofocus
the entry plate on initial load, support Enter-based form submission, and
expose status/feedback updates accessibly.
