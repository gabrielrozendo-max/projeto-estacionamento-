# Proposal: Streamlit Core Client Integration with Xano

## Why

The parking management system requires Streamlit as its exclusive frontend technology communicating securely with Xano as the sole backend. To begin migrating away from legacy Flask while preserving it until complete verification, we need a robust, secure, server-side HTTPS client in Python. This client will handle communication with Xano APIs, manage credentials (`XANO_BASE_URL`, `XANO_API_KEY`) safely via environment variables, provide resilient error and timeout handling without exposing sensitive tokens or internal details, and integrate initial status checking (`GET /status`) into `streamlit_app.py`.

## What Changes

- Introduce a secure Python client module for server-side HTTPS communication with Xano, reusing existing configuration patterns.
- Read `XANO_BASE_URL`, `XANO_API_KEY`, and `XANO_TIMEOUT_SECONDS` exclusively from environment variables.
- Implement robust handling of network exceptions, timeouts, and upstream HTTP/JSON errors, surfacing operator-friendly messages in Brazilian Portuguese (`pt-BR`) while ensuring tokens, credentials, and internal details are never exposed.
- Integrate initial status query (`GET /status`) into `streamlit_app.py` to display parking capacity and occupancy.
- Add automated unit tests with mocks for the Streamlit Xano client and status integration.
- Preserve legacy Flask application (`app.py`, templates, static) untouched until full migration is verified.

## Capabilities

### New Capabilities
- `streamlit-client`: Core server-side HTTPS communication layer between Streamlit and Xano, secure environment credential management, error/timeout resilience, secure error sanitization, and initial parking status integration.

### Modified Capabilities
- None.

## Impact

- New service code for Streamlit-Xano communication.
- Updates to `streamlit_app.py`.
- Automated tests for the Streamlit client.
- No changes to legacy Flask code, Xano schema, or Xano backend logic.
