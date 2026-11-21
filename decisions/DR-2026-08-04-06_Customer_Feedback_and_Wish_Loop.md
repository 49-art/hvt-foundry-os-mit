# DR-2026-08-04-06 — Decision Record — Customer Feedback & Wish Loop (Tablet-to-Model Path)

Document ID: DR-2026-08-04-06  
Title: Decision Record — Customer Feedback & Wish Loop (Tablet-to-Model Path)  
Version: 1.0  
Status: Approved  
Owner: Architecture Office  
Reviewed By: Chief Architect  
Dependencies: HVT-0001 Art. V, Art. VIII, Art. XIV, HVT-0004, HVT-0006  

---

## Decision

The Foundry must support a lightweight, constitutional path for capturing customer feedback and wishes from a live tablet session and feeding them straight back into the Model-First process. The customer is always right. The system must never require perfection before a real high-street owner can change direction.

## Action Taken

1. Created a new object type: Customer Wish (WSH-####).
2. Created a new object type: Customer Session (SES-####).
3. Registered both in the Object Model (to be formalised in HVT-0004 v0.3).
4. Added a simple workflow: Tablet Session → Capture Wishes → Engine Search or Configurator re-run → New configuration offered for approval.
5. Explicit rule: a Customer Wish never forces new code. It forces a Model-First re-evaluation (Article XIV) and, if needed, an Engine Search (Article II).

## Rationale

High-street owners will always have wishes that the current engines do not fully cover. The correct response is not to hard-code the wish, and not to refuse it. The correct response is to log it, re-classify the business if needed, and let the existing constitutional machinery decide the next step. This keeps the system imperfect by design and customer-driven by force.

## Authority

Issued under HVT-0001 Art. V, Art. VIII (customer assets and reality first), Art. XIV (Model-First), and HVT-0002 §3.2.

## Traceability

- Related: DR-2026-08-04-01 through -05 Extends: HVT-0004, HVT-0006 Enables: tablet-based discovery and rapid iteration for any high-street business type

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-04 | Decision issued. |

## Filing Note (Architecture Office, appended on registration — not part of the original decision text above)

Citation flagged, not corrected: the Authority section cites “Art. VIII (customer assets and reality first).” HVT-0001 Article VIII is titled Customer Asset Ownership and concerns data/configuration ownership (8.1–8.3); it does not contain a “reality first” or “customer is always right” clause. The decision’s substance — capture the wish, don’t hard-code it, don’t refuse it, run it back through Model-First — is sound and doesn’t depend on this citation being exact. If a “customer is always right” / reality-first principle is intended as its own standing doctrine, it isn’t yet written anywhere in the Constitution; it currently lives only as prose in this Decision Record’s Rationale. Flagged for a future decision on whether it should become its own clause (candidate: Article XIV, alongside the Model-First doctrine it’s paired with here) rather than an uncodified citation.

Registered on filing: WKF-0001 (the Tablet Session → Capture Wishes → Engine Search/Configurator → New Configuration workflow itself, as a Workflow-class object per HVT-0004 §2). Customer Wish and Customer Session are logged as proposed object types (HVT-0006 §9, v0.3) — consistent with how Problem, Integration, and Solution Component were each proposed before HVT-0004’s pending formal adoption; no instance data (no actual wish or session) has been created, since none was supplied.
