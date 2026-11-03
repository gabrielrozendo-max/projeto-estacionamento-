# streamlit-client Specification

## Purpose
Provides a secure, server-side HTTPS communication layer between Streamlit and Xano, managing environment credentials, error resilience, secure error sanitization, and parking status retrieval.

## Requirements

### Requirement: Secure server-side HTTPS client configuration
The system SHALL configure the Streamlit Xano client using environment variables `XANO_BASE_URL`, `XANO_API_KEY`, and `XANO_TIMEOUT_SECONDS`, reusing existing configuration patterns.

#### Scenario: Configuration loaded successfully from environment
- **WHEN** the application starts with valid environment variables
- **THEN** the Streamlit client uses the configured base URL and authentication header for HTTPS requests

#### Scenario: Missing or invalid configuration handling
- **WHEN** `XANO_BASE_URL` is missing or invalid
- **THEN** the client raises a clear configuration error without exposing sensitive tokens or internal details

### Requirement: Resilient API request handling and error management
The system SHALL handle network timeouts, connection failures, and upstream HTTP errors gracefully, returning structured error messages in Brazilian Portuguese (`pt-BR`) while strictly preventing the exposure of tokens, credentials, or internal system details.

#### Scenario: Upstream timeout or connection failure
- **WHEN** the request to Xano times out or fails to connect
- **THEN** the client catches the exception and presents a descriptive operator-friendly error message in Brazilian Portuguese without revealing internal stack traces or credentials

#### Scenario: Upstream HTTP error response
- **WHEN** Xano returns an HTTP error status code (e.g., 4xx, 5xx)
- **THEN** the client parses the upstream error message safely and displays a sanitised message in Brazilian Portuguese (`pt-BR`)

### Requirement: Parking status retrieval and capacity display
The system SHALL query `GET /status` on Xano and display max capacity, occupied spaces, and available spaces in Streamlit.

#### Scenario: Successful status retrieval
- **WHEN** the operator opens or refreshes the Streamlit dashboard
- **THEN** the system fetches parking status from Xano and displays capacity indicators
