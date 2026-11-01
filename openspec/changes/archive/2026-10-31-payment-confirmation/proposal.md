# Change: Confirm Payment and Release Parking Space

## Status

Archived; Xano-side verification pending.

## Why

After an exit, the parking record enters `Aguardando Pagamento` and continues
to count as occupied. The system needs a reliable confirmation flow that
transitions a pending record to `Concluído` and releases exactly one place.
The existing Flask route already proxies `POST /api/payments/confirm` to
Xano's `POST /payments/confirm`; this Change will verify and align that
contract, with the state and capacity mutation remaining exclusively in Xano.

## Scope

- Validate or minimally align the existing Flask payment-confirmation route.
- Forward a valid integer `record_id` to Xano as JSON.
- Preserve the successful Xano response, including the completed status and
  updated occupancy.
- Expand `tests/test_app.py` to cover the pending-to-completed response,
  release of one occupied place, invalid identifiers, and upstream errors.
- Keep state transition, occupancy decrement, and atomicity in Xano.

## Out of Scope

- Performing payment collection or connecting an external payment provider.
- Updating a parking record or capacity directly in Flask.
- Changing tariffs, exit calculation, or the Xano database schema.
- Adding routes or accepting a client-supplied payment amount/method.

## Files and Planned Modifications

| File | Planned modification |
|---|---|
| `app.py` | Verify `POST /api/payments/confirm` validates `record_id` and proxies `{"record_id": id}` to Xano `POST /payments/confirm`. Do not add local state or capacity changes. Make a minimal correction only if contract tests identify a mismatch. |
| `tests/test_app.py` | Add or refine tests for request URL/method/payload, preservation of `status: "Concluído"` and `occupancy.occupied_spaces` decreased by one in the Xano response, invalid IDs rejected without upstream calls, and Xano/network errors surfaced as structured errors. |
| `docs/specs/xano-backend.md` | No change expected; the existing contract already requires an atomic, one-time decrement during payment confirmation. |
| `openspec/changes/payment-confirmation/proposal.md` | Record scope, rationale, dependencies, and acceptance criteria. |
| `openspec/changes/payment-confirmation/specs/payment-confirmation/spec.md` | Specify the observable proxy contract and Xano-owned atomic state/capacity behavior. |
| `openspec/changes/payment-confirmation/tasks.md` | Track implementation and focused verification. |

## Acceptance Criteria

1. `POST /api/payments/confirm` accepts a JSON object with a positive integer
   `record_id`; booleans, non-integers, and non-positive values are rejected.
2. Flask sends `POST /payments/confirm` to Xano with
   `{"record_id": <id>}` and JSON acceptance headers.
3. Flask preserves the successful upstream JSON response, including
   `data.status = "Concluído"` and the updated occupancy returned by Xano.
4. Flask does not mutate the record or decrement `occupied_spaces` locally.
5. Xano permits only a transition from `Aguardando Pagamento` to `Concluído`
   and decrements occupancy exactly once as part of the same logical operation.
6. A repeated confirmation or a record not pending payment is returned as the
   documented conflict; occupancy is not decremented again.
7. An inconsistent zero occupancy does not result in a completed record.
8. Invalid requests do not contact Xano; upstream HTTP and network errors are
   returned as structured errors and are not represented as success.
9. The focused Flask tests pass without network access or Xano credentials.

## Verification

- Run `python -m pytest -q tests/test_app.py`.
- Assert exact Xano URL, method, JSON body, and preserved response fields.
- Cover invalid `record_id`, upstream conflict/error, and network failure.
- Verify the Xano Function Stack provides an atomic/idempotent transition and
  capacity decrement; mocked Flask tests alone cannot prove deployed Xano
  behavior.
- Confirm occupancy remains unchanged on exit and decreases only when the
  pending payment is confirmed.

## Dependencies and Risks

- Depends on the Xano `POST /payments/confirm` endpoint and its atomic update
  logic being deployed according to `docs/specs/xano-backend.md`.
- The Flask test suite validates proxy behavior and response handling; it
  cannot independently verify Xano database atomicity without Xano-side
  integration or operational verification.
- Payment confirmation represents confirmation of settlement, not actual
  payment processing; external payment integration remains undefined and out
  of scope.
