## ADDED Requirements

### Requirement: Flask and Xano are the only active application architecture

The system MUST use Flask for its local web application and gateway, and Xano
as its sole backend, database, and business-rules platform. The active runtime
MUST NOT use a Node.js server or local database.

#### Scenario: Application starts without a local database

- **WHEN** the Flask application is started
- **THEN** it MUST NOT initialize or access SQLite or another local database
- **AND** Xano requests MUST be made through the existing Flask proxy routes

### Requirement: Xano connection configuration comes from the environment

The system MUST read `XANO_BASE_URL` and any optional Xano API key from
environment variables, including variables loaded from `.env`. Source code
MUST NOT contain a fixed Xano URL or credential.

#### Scenario: Xano base URL is not configured

- **WHEN** `XANO_BASE_URL` is unset or empty
- **THEN** the application MUST NOT fall back to a hardcoded Xano endpoint
- **AND** a proxy request MUST return the existing structured configuration
  error without making an upstream request

#### Scenario: Xano API key is configured

- **WHEN** `XANO_API_KEY` is set
- **THEN** the Flask proxy MUST send it to Xano as a Bearer authorization token
- **AND** it MUST NOT expose the token in the browser response
