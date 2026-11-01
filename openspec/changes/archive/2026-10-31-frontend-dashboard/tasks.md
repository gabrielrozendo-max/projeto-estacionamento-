## 1. Align dashboard API interactions

- [x] 1.1 Verify status, entry, exit, and payment route methods and payloads against the Flask contracts.
- [x] 1.2 Handle documented response envelopes and snake_case response fields consistently.
- [x] 1.3 Preserve Xano ownership of fee calculation, state transitions, and occupancy.

## 2. Align occupancy and fee presentation

- [x] 2.1 Render occupied, available, and maximum capacity from a valid status response.
- [x] 2.2 Verify green below 80%, yellow from 80% to below 100%, and red at 100%.
- [x] 2.3 Disable entry while status is unavailable/invalid and while the park is full.
- [x] 2.4 Format integer `total_cents` as EUR with Portuguese locale and cent precision.
- [x] 2.5 Keep occupancy unchanged after exit and refresh it after payment confirmation.

## 3. Verify operator feedback and accessibility

- [x] 3.1 Show readable errors for Flask/Xano HTTP errors, malformed responses, and network failures.
- [x] 3.2 Preserve Portuguese UI, entry-plate autofocus, keyboard submission, and accessible status feedback.
- [x] 3.3 Verify the live dashboard in a browser using mocked Flask responses; the proposal records reproducible checks.
- [x] 3.4 Run automated tests and verify the full, threshold, fee, and payment flows.
