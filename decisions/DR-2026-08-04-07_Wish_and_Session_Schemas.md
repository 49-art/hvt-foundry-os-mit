# DR-2026-08-04-07 — Decision Record — Field-Level Schemas for Customer Wish and Customer Session (HVT-0006 v0.4)

Document ID: DR-2026-08-04-07  
Title: Decision Record — Field-Level Schemas for Customer Wish and Customer Session (HVT-0006 v0.4)  
Version: 1.0  
Status: Approved  
Owner: Architecture Office  
Reviewed By: Chief Architect  
Dependencies: HVT-0001 Art. V, Art. VIII, Art. XIV, HVT-0004, HVT-0006, DR-2026-08-04-06  

---

## Decision

DR-2026-08-04-06 registered Customer Wish (WSH-####) and Customer Session (SES-####) as proposed object types without field-level detail. This decision adopts the full schemas as supplied, verbatim, and folds them into HVT-0006 as §9’s expansion (v0.3 → v0.4).

## Action Taken

1. Added CustomerSession field schema to HVT-0006 §9.1: id, class, project_id_or_business_type_id, date, location, owner, status, notes, linked_wishes.
2. Added CustomerWish field schema to HVT-0006 §9.2: id, class, session_id, description, priority, status, linked_problems, linked_capabilities, resolution, customer_asset_flag.
3. Registered both status vocabularies as proposed extensions to HVT-0004 §4:
    - Customer Session: Open → Closed → Actioned Customer Wish: Logged → Under Review → Engine Search Required → Configured → Accepted → Rejected by Customer → Superseded
4. Restated the binding rule in its precise supplied form: “A Customer Wish never authorises new Engine code by itself. It only authorises a re-run of the Configurator or a formal Engine Search.” — replacing DR-2026-08-04-06’s looser paraphrase in HVT-0006 §9 with this exact wording.
5. No instance data created. No real Customer Wish or Customer Session exists yet; this decision completes the schema only.

## Rationale

customer_asset_flag is the field of particular constitutional weight here: it ties a Customer Wish directly to Article VIII 8.2, which requires the customer-asset-vs-Foundry-engine distinction to be explicit before work begins. Without this field, a wish that happens to touch customer-owned data or branding could be actioned through the Engine Search / Configurator path with no record of which side of the Article VIII line it falls on. With it, that determination is captured at the moment the wish is logged, not reconstructed later.

The rest of the schema is adopted as supplied without material change — both object types were already proposed in DR-2026-08-04-06, so this decision is a completion, not a new architectural question.

## Authority

Issued under HVT-0001 Art. V (traceability), Art. VIII (customer asset distinction, via customer_asset_flag), Art. XIV (Model-First — the schema exists to route wishes back through this doctrine), and HVT-0002 §3.2.

## Traceability

- Completes: DR-2026-08-04-06 (Customer Wish / Customer Session type registration).
- Extends: HVT-0006 v0.3 → v0.4.
- Related: DR-2026-08-04-01 through -06.
- Open follow-ons, unchanged: HVT-0004 formal adoption of all proposed types and status vocabularies from HVT-0006 (§3, §9)
- remains pending a single consolidated version bump — not one bump per proposal, to avoid HVT-0004 churning with every HVT-0006 revision. No real Customer Wish or Customer Session instance exists yet.

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-04 | Decision issued and executed. |
