# DR-2026-08-04-01 — Decision Record — Resolve ENG-0003 Dependency Gap (HVT-0003 §2, Issue A)

Document ID: DR-2026-08-04-01  
Title: Decision Record — Resolve ENG-0003 Dependency Gap (HVT-0003 §2, Issue A)  
Version: 1.0  
Status: Approved  
Owner: Architecture Office  
Reviewed By: Chief Architect  
Dependencies: HVT-0001 Art. V, HVT-0002 §3.2, HVT-0003  

---

## Decision

ENG-0003 (Commerce Engine) listed dependencies DOC-0001 and DOC-0004, neither of which existed as registered Documentation assets at the time HVT-0003 was drafted. This was logged as an open traceability item, not silently resolved, per HVT-0001 Art. V.

Architecture Office determines these were never intended as Governance Document references (HVT-####) but as genuine Documentation-class Business Assets that had not yet been written.

## Action Taken

1. Created DOC-0001 — Commerce Engine High-Street Integration Guide.
2. Created DOC-0004 — Commerce Engine Provider Abstraction Notes.
3. Updated HVT-0003 Asset Ledger: ENG-0003 dependencies changed from “DOC-0001, DOC-0004 (unresolved)” to “DOC-0001, DOC-0004” (resolved), referencing the two new assets by their now-real IDs.
4. Updated foundry_graph.json: DOC-0001 and DOC-0004 objects changed from status “unresolved” to “Draft”; the prior unresolved objects are marked superseded rather than deleted, preserving history per HVT-0001 Appendix A.
5. HVT-0003 §2 Issue A marked Resolved with a pointer to this Decision Record.

## Rationale

Per HVT-0001 Art. V, every proposal must be traceable and undocumented state carries no institutional weight. Resolving the gap by creating the real assets — rather than deleting the reference or inventing a retroactive justification — keeps the chain of custody intact and satisfies the Constitution’s instruction against silently resolving ambiguity in another office’s record.

## Authority

Issued under HVT-0001 Art. V and HVT-0002 §3.2 (Architecture Office decision authority over Registry and Object Model consistency).

## Traceability

- Supersedes: unresolved DOC-0001 / DOC-0004 entries in foundry_graph.json (2026-08-04 seed)
- Related: DR-2026-08-04-02 (ENG-0001 / ENG-0002 numbering gap)

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-04 | Decision issued and executed. |
