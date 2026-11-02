# Tasks

## 1. Streamlit Client Implementation & Configuration

- [ ] 1.1 Implement Streamlit Xano client module (`src/services/streamlit_client.py`) reading `XANO_BASE_URL`, `XANO_API_KEY`, and `XANO_TIMEOUT_SECONDS` from environment variables, reusing existing configuration patterns, and verify configuration handling via unit tests.
- [ ] 1.2 Implement robust error and timeout handling with operator-friendly Brazilian Portuguese (`pt-BR`) error messages, ensuring tokens, credentials, and internal details are never exposed, and verify exception tests pass.

## 2. Status Integration & Testing

- [ ] 2.1 Integrate `GET /status` in `streamlit_app.py` to display parking capacity and occupancy, and verify correct rendering.
- [ ] 2.2 Create automated unit tests for the Streamlit client and status integration, and verify all tests pass successfully using `pytest`.

## Workflow follow-up

- Review and verify the implementation before archiving the change.
