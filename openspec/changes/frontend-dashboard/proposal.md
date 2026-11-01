# Change: Align Frontend Dashboard with Flask and Xano Contracts

## Status

Applied.

## Why

The dashboard is the operator's interface for occupancy, vehicle entry, exit,
and payment confirmation. Its JavaScript already calls the Flask proxy routes,
but the full mapping between API responses and visible UI behavior should be
specified and verified together. In particular, displayed prices must use
integer `total_cents`, capacity indicators must match the documented
thresholds, and new entries must be disabled when the park is full or status
cannot be trusted.

## Scope

- Validate and align calls in `static/js/dashboard.js` with the existing Flask
  routes: `/api/status`, `/api/entries`, `/api/exits`, and
  `/api/payments/confirm`.
- Ensure occupancy, availability, and capacity are rendered consistently,
  with green below 80%, yellow from 80% to below 100%, and red at 100%.
- Disable vehicle entry when the park is full and when status cannot be
  verified; enable it again after a successful refresh reports capacity.
- Format exit fees from integer `total_cents` as EUR without changing the
  amount or using floating-point arithmetic for business calculations.
- Present success and error feedback for all operator actions, including
  network, Flask, and upstream Xano failures.
- Refresh occupancy after successful entry, exit, and payment confirmation;
  keep the parking place occupied during `Aguardando Pagamento` and reflect
  release only after confirmation.
- Verify existing form usability requirements: Portuguese UI, entry-plate
  autofocus, and Enter-based form submission.

## Out of Scope

- Adding Flask or Xano routes, business rules, or persistence.
- Recalculating parking duration, tariffs, billing rounding, or occupancy in
  JavaScript.
- Changing the payment-confirmation semantics or freeing a place at exit.
- Adding authentication, administrative screens, or external payment services.
- Introducing a new frontend framework or build system.

## Files and Planned Modifications

| File | Planned modification |
|---|---|
| `static/js/dashboard.js` | Align request paths and payload keys with the Flask API; handle documented response fields, status thresholds, fee formatting, loading/feedback behavior, and post-operation refreshes. Do not duplicate Xano business rules. |
| `templates/index.html` | Adjust markup, labels, live regions, or disabled-state presentation only where needed for accessible and accurate dashboard behavior. Preserve Portuguese (`pt-PT`) and existing semantic structure. |
| `tests/` | Add focused frontend behavior tests using the repository's available test tooling, or document a repeatable browser verification if no JavaScript test runner exists. Do not reintroduce a Node server or local database. |
| `docs/specs/dashboard-ui.md` | No change expected; add or amend only if a requirement needs to become a lasting project-level UI specification rather than a Change delta. |
| `openspec/changes/frontend-dashboard/proposal.md` | Record this proposal and its acceptance criteria. |
| `openspec/changes/frontend-dashboard/specs/frontend-dashboard/spec.md` | Specify endpoint use and observable dashboard behavior. |
| `openspec/changes/frontend-dashboard/tasks.md` | Break implementation and verification into small tasks. |

## Acceptance Criteria

1. The dashboard calls only the existing Flask routes with the documented HTTP
   methods and JSON payloads; it does not call Xano directly.
2. The occupancy display renders occupied, available, and maximum capacity
   from the status response, accepting the documented snake_case keys.
3. Occupancy below 80% is green; occupancy from 80% to less than 100% is
   yellow; occupancy at 100% is red.
4. The entry submit control is disabled at full capacity and while status is
   unavailable or invalid; it is re-enabled only after a valid status refresh
   shows an available space.
5. Exit fees are read from integer `total_cents` and displayed as EUR in
   Portuguese locale; no client-side tariff or duration calculation occurs.
6. After exit, the interface communicates `Aguardando Pagamento` and the
   occupied count remains unchanged. After successful payment confirmation,
   the UI reflects `Concluído` and refreshes the released capacity.
7. Flask/Xano and network failures are shown as operator-readable error
   feedback; failed operations are not presented as successful.
8. Submitting forms with Enter and autofocus on the entry plate continue to
   work.
9. Focused frontend checks or documented browser verification cover full,
   threshold, error, fee, and confirmation cases without access to a live Xano
   service.

## Verification

- Test or manually verify all four route calls against their expected methods
  and payloads.
- Exercise occupancy at below 80%, exactly 80%, 99%, and 100%.
- Check the disabled entry state during initial loading, a failed status
  request, invalid status values, and a valid non-full status.
- Verify representative integer-cent amounts render correctly as EUR and
  preserve cent precision.
- Simulate Flask structured errors, malformed responses, and network
  failures for each relevant action.
- Verify exit leaves occupancy unchanged and payment confirmation refreshes
  the status with one fewer occupied space.
- Run the available automated tests and any focused browser checks.

## Dependencies and Risks

- Depends on the Flask proxy routes and response contracts already specified
  in `docs/specs/xano-backend.md`.
- Status responses may be nested or top-level depending on the Xano endpoint;
  confirm the actual documented contract before adding compatibility logic.
- Client-side occupancy can become stale when multiple operators act
  concurrently. Xano remains authoritative for entry admission; the UI
  disablement is a usability aid, not a concurrency guarantee.
- If no frontend test runner is present, browser verification must be
  repeatable and clearly recorded; adding tooling is not assumed by this
  proposal.
