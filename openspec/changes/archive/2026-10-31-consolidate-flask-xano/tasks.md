## 1. Establish OpenSpec and architecture requirements

- [x] 1.1 Add the project OpenSpec configuration and Change proposal.
- [x] 1.2 Specify Flask/Xano runtime and proxy contract requirements.

## 2. Consolidate the runtime and configuration

- [x] 2.1 Remove the legacy Node/SQLite application, schema, manifests, and tests.
- [x] 2.2 Load Xano URL and optional API key only from environment variables.
- [x] 2.3 Preserve the existing Flask routes and Xano JSON proxy behavior.

## 3. Verify

- [x] 3.1 Cover the Flask-to-Xano route and payload contracts in Python tests.
- [x] 3.2 Run the focused test suite and inspect for remaining active Node/SQLite references.
