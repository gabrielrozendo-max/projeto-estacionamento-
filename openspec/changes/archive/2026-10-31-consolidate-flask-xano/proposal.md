---
status: archived
completed: 2026-10-31
---

# Change: Consolidate Flask and Xano

## Why

The repository contains both a Flask application that proxies requests to Xano
and a separate Node/Express API backed by SQLite. The browser dashboard uses the
Flask routes, while the Node implementation introduces a conflicting runtime
and local persistence model. Xano URL and credential configuration must also
come only from environment variables.

## What Changes

- Establish Flask + Xano as the only active application architecture.
- Remove the legacy Node/SQLite API, schema, package manifests, and its tests.
- Add the OpenSpec project configuration and this tracked Change.
- Read the Xano base URL and optional API key from environment variables.
- Keep the existing Flask routes and align their tests with the Xano JSON
  contracts; add no business routes or rules.

## Capabilities

### New Capabilities

- `project-architecture`: Defines the active Flask/Xano runtime and environment
  configuration requirements.
- `xano-api-proxy`: Defines the contract-preserving Flask proxy and its tests.

### Modified Capabilities

None.

## Impact

- Application configuration and proxy: `config.py`, `app.py`, `.env.example`.
- Verification: `tests/test_app.py`; removal of the Node integration test.
- Legacy runtime: remove `src/`, `database/schema.sql`, `package.json`, and
  `package-lock.json`.
- OpenSpec: add `openspec/config.yaml` and the Change artifacts.
- No routes, Xano tables, business rules, or frontend behavior are added.
