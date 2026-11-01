## 1. Align the Flask exit route with the Xano contract

- [x] 1.1 Confirm `POST /api/exits` forwards only the normalized plate to Xano.
- [x] 1.2 Preserve the upstream successful status and JSON response.
- [x] 1.3 Keep all tariff, duration, rounding, state, and occupancy logic in Xano.

## 2. Verify the exit flow

- [x] 2.1 Test the exit endpoint URL, method, and normalized request payload.
- [x] 2.2 Test preservation of the successful response including `total_cents`.
- [x] 2.3 Test invalid input, Xano HTTP errors, and network failures.
- [x] 2.4 Assert that pending payment does not decrement occupied capacity.
- [x] 2.5 Run the focused Flask test suite.
