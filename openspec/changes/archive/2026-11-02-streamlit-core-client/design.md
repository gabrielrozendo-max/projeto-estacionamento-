# Design: Streamlit Core Client Integration with Xano

## Context

See proposal.md - Why. The project is migrating its frontend from legacy Flask/HTML/JS to Streamlit while keeping Xano as the sole backend and database. We need a modular Python client in Streamlit to perform HTTPS requests to Xano with proper security, timeout handling, reuse of existing configuration patterns, and testability.

## Goals / Non-Goals

**Goals:**
- Implement a dedicated Streamlit Xano client module (e.g., `src/services/streamlit_client.py`) using `requests`.
- Load configuration (`XANO_BASE_URL`, `XANO_API_KEY`, `XANO_TIMEOUT_SECONDS`) securely via environment variables, reusing existing configuration approaches.
- Handle connection errors, timeouts, and upstream error payloads robustly while sanitizing error outputs to prevent any exposure of tokens, credentials, or internal system details.
- Integrate `GET /status` into `streamlit_app.py`.
- Add automated unit tests with mocks to verify client behavior.

**Non-Goals:**
- Modifying Xano database schemas or server code.
- Removing or altering the legacy Flask application (`app.py`) during this change.
- Implementing entry/exit/payment mutations (deferred to subsequent Streamlit changes).

## Decisions

- **Decision 1: Dedicated Service Module (`src/services/streamlit_client.py`)**: 
  - *Rationale*: Separation of concerns keeps UI logic in `streamlit_app.py` clean and separates API communication and error handling into testable functions.
  - *Alternatives considered*: Placing all HTTP calls directly inside `streamlit_app.py` (rejected due to maintainability and testability concerns).
- **Decision 2: Use Python `requests` library**:
  - *Rationale*: Already used and tested successfully in the project (`app.py`, `tests/test_app.py`).
  - *Alternatives considered*: `httpx` or `urllib` (rejected to maintain ecosystem consistency).

## Risks / Trade-offs

- **Risk**: Network instability or Xano service unavailability.
  - *Mitigation*: Comprehensive exception catching (`Timeout`, `ConnectionError`, `HTTPError`) with user-friendly warnings/errors in Brazilian Portuguese (`pt-BR`).
- **Risk**: Secret leakage in logs or UI.
  - *Mitigation*: Ensure API keys, tokens, credentials, and raw internal stack traces are never printed, logged, or exposed in Streamlit UI components or error responses.
