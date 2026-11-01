## 1. Align the Flask confirmation route

- [x] 1.1 Validate positive integer `record_id` values and reject booleans or invalid values.
- [x] 1.2 Forward the confirmation request to Xano with the documented JSON payload.
- [x] 1.3 Preserve successful status, completed record, amount, and occupancy response fields.
- [x] 1.4 Keep all record and capacity mutations in Xano.

## 2. Verify payment confirmation

- [x] 2.1 Test the Xano endpoint, method, request payload, and successful response.
- [x] 2.2 Verify the response reports `Concluído` and one fewer occupied space.
- [x] 2.3 Test invalid identifiers and ensure they do not call Xano.
- [x] 2.4 Test Xano HTTP conflicts/errors and network failures.
- [ ] 2.5 Verify Xano-side idempotency, atomicity, and inconsistency handling (requires deployed Xano access).
- [x] 2.6 Run the focused Flask test suite.
