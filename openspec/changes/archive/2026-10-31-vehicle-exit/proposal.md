# Change: Vehicle Exit and Fee Calculation

## Status

Archived.

## Why

The Flask application already exposes `POST /api/exits` and proxies the
normalized plate to Xano's `POST /exits`. The contract test currently checks
part of this flow alongside payment confirmation, but does not fully verify
the exit endpoint, response, and failure cases as an independent vertical
capability.

This Change will make the exit flow and its Flask-to-Xano contract explicit
and verifiable without moving parking business rules into Flask.

## Scope

- Verify and, only where needed, align the existing Flask exit route with the
  Xano contract.
- Forward the normalized plate to Xano and preserve its successful JSON
  response and status, including `total_cents`, `exit_at`, and status when
  returned by Xano.
- Expand `tests/test_app.py` to cover valid exits, invalid requests, upstream
  errors, and the occupancy invariant.
- Keep calculation of elapsed time, tariff selection, rounding, record-state
  transition, and occupancy updates in Xano.

### Occupancy decision requiring Review

The requested decrement of one occupied space at exit conflicts with
`docs/specs/xano-backend.md`: an exit changes the record to
`Aguardando Pagamento` and MUST leave `occupied_spaces` unchanged. The place is
released only after `POST /payments/confirm` transitions the record to
`Concluído`.

This proposal follows the existing domain contract and MUST NOT decrement
occupancy on `POST /exits`. If the product requires freeing the place before
payment, that is a domain and operational policy change requiring explicit
approval and updated specifications before Apply; it is not assumed here.

## Out of Scope

- Implementing tariff calculation, time rounding, or persistence in Flask.
- Adding a new endpoint or changing the existing Xano endpoint contract.
- Decrementing occupancy during exit.
- Implementing or changing payment confirmation behavior.
- Changing Xano tables or introducing local persistence.

## Files and Planned Modifications

| File | Planned modification |
|---|---|
| `app.py` | Inspect the existing `/api/exits` route. Preserve its route and Xano proxy approach; make only contract alignment changes if tests demonstrate a mismatch. No local fee calculation or occupancy mutation. |
| `tests/test_app.py` | Add focused exit contract tests: URL/method, normalized plate payload, returned status/body including `total_cents`, Xano HTTP errors, network errors, and no upstream request for invalid input. Assert that Flask does not calculate the fee or report an occupancy decrement. |
| `docs/specs/xano-backend.md` | No change expected if the existing exit contract remains authoritative. Modify only if Review approves a different occupancy policy before Apply. |
| `openspec/changes/vehicle-exit/specs/vehicle-exit/spec.md` | Define observable exit behavior and explicitly preserve the pending-payment occupancy invariant. |
| `openspec/changes/vehicle-exit/tasks.md` | Track implementation and focused verification tasks. |

## Acceptance Criteria

1. `POST /api/exits` accepts a JSON object with a non-empty `plate`, trims it,
   uppercases it, and forwards `{"plate": "<NORMALIZED>"}` to Xano `POST /exits`.
2. Flask does not calculate duration, choose a tariff, round billing time,
   write parking records, or mutate occupancy.
3. A successful Xano response is returned with its status and JSON content
   preserved, including `data.total_cents` when supplied.
4. A Xano HTTP error is surfaced as the existing structured Flask JSON error
   and does not become a success response.
5. Network failures use the existing structured error behavior.
6. Missing, invalid, or non-JSON input is rejected without contacting Xano.
7. Exit does not reduce `occupied_spaces`; the space remains occupied while
   the record is `Aguardando Pagamento`.
8. The focused Flask tests pass without network access or Xano credentials.

## Verification

- Run `python -m pytest -q tests/test_app.py`.
- Confirm tests assert the outbound request method, URL, payload, and preserved
  successful response.
- Confirm tests cover an upstream error and a network failure.
- Confirm the proposal/spec do not contradict the payment-before-release rule
  in `docs/specs/xano-backend.md`.

## Dependencies and Risks

- Depends on the existing Xano `POST /exits` endpoint implementing the
  documented fee and state transition contract.
- The Xano endpoint contract currently uses `total_cents` in its response,
  while the domain table calls the persisted field `total_amount_cents`.
- Product confirmation is needed if the requested early occupancy decrement
  was intentional; applying it would invalidate the current payment flow and
  can allow new entries before payment completes.
