# DR-2026-08-04-09 — Decision Record — First Template Instances: SES-0001, WSH-0001

Document ID: DR-2026-08-04-09  
Title: Decision Record — First Template Instances: SES-0001, WSH-0001  
Version: 1.0  
Status: Approved  
Owner: Architecture Office  
Reviewed By: Chief Architect  
Dependencies: HVT-0006 §9, DR-2026-08-04-06, DR-2026-08-04-07, DOC-0005, BUT-0001  

---

## Decision

The first instances of Customer Session and Customer Wish are registered — SES-0001 and WSH-0001 — as supplied, explicitly marked as templates rather than real customer data. This validates the HVT-0006 §9 schema and the WKF-0001 loop end to end against the BUT-0001 (Hair Salon) pilot, without waiting for an actual tablet session.

## Action Taken

1. Registered SES-0001 and WSH-0001 with the base fields exactly as supplied (id, class, name, owner, status, version, authority, source_document, note).
2. Completed the type-specific fields defined in HVT-0006 §9.1/ §9.2, which the supplied objects did not include, using values consistent with the objects’ own names and notes:
    - SES-0001.project_id_or_business_type_id: BUT-0001 SES-0001.linked_wishes: [WSH-0001] SES-0001.notes: marks it explicitly as a schema-validation template, not a real interaction WSH-0001.session_id: SES-0001 WSH-0001.description: “Owner wants stock alerts on phone” — templated from the object’s own name, not an actual customer quote WSH-0001.linked_problems: [PRB-0004] (Manual stock — already registered against BUT-0001)
    - WSH-0001.linked_capabilities: “Stock / inventory tracking (mobile notifications)” — matches the capability gap already flagged on the BUT-0001 canonical card (HVT-0006 §2.3)
    - WSH-0001.customer_asset_flag: true — stock-level and notification configuration is customer-specific configuration under Art. VIII 8.1 WSH-0001.priority: left unset. Not fabricated, since no Must/Should/Could signal was supplied and inventing one would misrepresent a template as having real customer input.
    - WSH-0001.resolution: states the wish is open, matches the pre-existing Stock Engine gap, and per the binding rule (DR-2026-08-04-06/-07) authorizes a formal Engine Search, not new code — Engine Search not yet run.

## Rationale

This is the first end-to-end demonstration of the loop DOC-0005 describes: a wish lands on a known capability gap (Stock/inventory tracking) that was already flagged, not newly discovered, which is exactly what the loop is supposed to surface cleanly rather than let quietly disappear. customer_asset_flag: true is a deliberate choice, not a default — it shows the flag doing the job Article VIII 8.2 requires, distinguishing “this wish touches customer-owned configuration” from wishes that wouldn’t.

priority was left unset rather than guessed, consistent with not inventing customer input that wasn’t given.

## Authority

Issued under HVT-0001 Art. V, Art. VIII, HVT-0002 §3.2.

## Traceability

- Registers: SES-0001, WSH-0001.
- Validates: HVT-0006 §9 schema, WKF-0001, DOC-0005.
- Links: BUT-0001 (pilot), PRB-0004 (Manual stock — pre-existing gap this wish surfaces).
- Open follow-on: the Engine Search this wish authorizes (Stock/inventory tracking capability) has not been run. WSH-0001.status remains Logged, not yet advanced to Engine Search Required.

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-04 | Decision issued and executed. |
