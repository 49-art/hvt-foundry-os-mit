# DR-2026-08-04-05 — Decision Record — Marketplace Layer (HVT-0007), Solution Component Migration, and Constitutional Amendment (Article VI.4)

Document ID: DR-2026-08-04-05  
Title: Decision Record — Marketplace Layer (HVT-0007), Solution Component Migration, and Constitutional Amendment (Article VI.4)  
Version: 1.0  
Status: Approved  
Owner: Architecture Office  
Reviewed By: Chief Architect  
Dependencies: HVT-0001 Art. VI, Art. XI, Art. V, HVT-0002 §3.2, HVT-0004, HVT-0006, HVT-0007  

---

## Decision

Howard (Special Advisor) proposed a new constitutional concept — the HVT Marketplace Layer — reframing the Foundry as a marketplace of solutions across four ownership tiers (Open Source, Foundry Assets, Partner Products, Customer Assets), with a new interchangeable object type (Solution Component) replacing ad hoc product references, a Partner Status ladder, and a Constitution-level neutrality clause.

Per confirmed scope, this is formalized as a new document, HVT-0007 — Marketplace Layer & Solution Catalog, with the existing seven Integration objects migrated into the new schema and Apple Pay registered as the first new Tier 3 Partner Product.

## Explicit Open Item Carried Forward, Not Resolved

The relationship between the new Solution Component type and the existing Integration type (HVT-0006 v0.2, INT-####) was asked as a direct question; the answer given was “I’ll clarify — hold off.” Because the same message confirmed migrating the seven existing records and adding Apple Pay, Architecture Office proceeded with the most reversible interpretation available rather than blocking the whole pass on one unresolved sub-question:

- All seven INT-#### objects are retained exactly as they were — no edits, no deletions.
- Seven new SLC-#### objects are created with the fuller Solution Component schema, each carrying a supersedes edge back to its INT-#### predecessor.
- HVT-0007 §3.1 states plainly that this is a provisional resolution, and that either final answer (full replacement, or Integration as a permanent Solution Component subtype) requires no data migration to correct — only a wording change in §3.1 itself.

This is logged so the “hold off” is visible in the record, not quietly overridden by the scope confirmation that followed it.

## Action Taken

1. Created HVT-0007, defining the Four Tiers, the Solution Component schema (SLC-####), the Partner Status controlled vocabulary, and the downstream resolution chain (Business Blueprint → Required Capability → Foundry Engine → Partner Products/Open Source Alternatives → Customer Choice → Deployment).
2. Migrated INT-0001–INT-0007 into SLC-0001–SLC-0006 (Stripe, Square, Google Calendar, Apple Calendar, WhatsApp Business, Xero, QuickBooks) with supersedes edges; originals untouched.
3. Registered SLC-0008 — Apple Pay — as the first new Tier 3 Partner Product, with partner_status: Public Integration (no partnership agreement exists; not marked Certified or higher).
4. Logged, not registered, the remaining five named Apple products (Wallet, Maps, Business Connect, Sign in with Apple, Push Notifications, and StoreKit as a distinct capability) as future Solution Catalog candidates.
5. Proposed and adopted HVT-0001 Article VI.4 (see Part 2 below)
    - under the Art. XI amendment procedure.
6. Flagged, not resolved: a countries-supported discrepancy for Stripe (170+ in the original ENG-0003 dependency work vs. 46+ in this pass) — both figures retained on their respective records (INT-0001 vs SLC-0001).
7. Flagged, not resolved: Stripe’s supplied partner status “Official”
    - does not match any rung of the six-level Partner Status ladder — mapped to “Verified” as the closest fit, pending confirmation.
8. Explicitly deferred: referral income modeling, logged as a commercial (not architectural) concern in HVT-0007 §9.

## Part 2 — Constitutional Amendment (Article XI Procedure)

Article affected: Article VI (Modularity, Interchangeability, and Documentation Standards) — new clause 6.4, not a new standalone Article.

Proposed change: “Foundry recommends solutions, not vendors. Vendor recommendations shall be derived from the customer’s requirements, deployment constraints, geography, budget, and existing technology estate, ensuring that interchangeable alternatives remain available wherever practical.” — as supplied, unedited.

Rationale: Article VI already establishes module replaceability (6.1) and AI provider interchangeability (6.2) as binding doctrine. This clause is the same principle applied to the full universe of vendor recommendations the Marketplace Layer now formalizes — a natural extension of an existing Article rather than new constitutional ground, unlike Article XIV, which addressed a genuinely new question (how engagements begin) with no existing Article to extend.

Placement decision, not directly confirmed: no question was put to the person on Article-vs-clause placement; Architecture Office made the call and states it plainly here so it can be corrected on review without any registered data needing to change.

Review: Under HVT-0002 §3.2 and HVT-0001 Art. V.

Version increment: HVT-0001 v1.1 → v1.2. Changelog entry appended in the Constitution.

Effect: Per Art. XI.2, governs future work only; does not retroactively fault the four existing named engagements.

## Authority

Part 1 (HVT-0007, Solution Component migration) issued under HVT-0001 Art. V, Art. XIII, HVT-0002 §3.2, as a governed extension of HVT-0006. Part 2 (Article VI.4) issued under HVT-0001 Art. XI.

## Traceability

- Creates: HVT-0007.
- Amends: HVT-0001 (Constitution), adding Article VI.4.
- Extends: HVT-0006 (Solution Component supersedes Integration, pending final confirmation — see Open Item above).
- Related: DR-2026-08-04-01 through -04 (same working session).
- Open follow-ons: final Solution-Component-vs-Integration relationship confirmation; Stripe countries-supported discrepancy; “Official” vs. Partner Status ladder terminology; five unregistered Apple products; referral income record type; HVT-0004 formal adoption (still pending from HVT-0006, unchanged).

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-04 | Decision issued and executed. |
