# DR-2026-11-20-12 — Completion record: version table, Draft records carried, tests, and what still needs a live human

Document ID: DR-2026-11-20-12  
Title: Completion record for the 20 Nov 2026 completion pass (DR-2026-11-20-01 … -12)  
Version: 1.0  
Status: Approved  
Owner: CEO Office  
Reviewed By: Tony Adams (Raj), CEO Office — 20 Nov 2026  
Dependencies: DR-2026-11-20-01 … DR-2026-11-20-11; HVT-0001 Art. V.4, Art. XI, Art. XII  

---

Owner's instruction, 20 Nov 2026: "can you complete all decisions waiting and complete it." Authority and identity: DR-2026-11-20-01.

## 1. Version table (no ID reused; every older version kept as its own file or in its changelog)

| ID | Before | After | Record |
|---|---|---|---|
| HVT-0001 Constitution | 1.2 Approved | 1.3 Approved (Art. XIV.6 added under Art. XI) | DR-2026-11-20-06 |
| HVT-0002 Organisation & Authority | 0.3 founder-approved | 1.0 Approved | DR-2026-11-20-06 |
| HVT-0003 Business Asset Registry | 0.6 founder-approved interim | 1.0 Approved (new file; 0.4/0.5/0.6 kept) | DR-2026-11-20-02 |
| HVT-0004 Object Model | 0.3 founder-approved interim | 1.0 Approved (new file; 0.1/0.2/0.3 kept) | DR-2026-11-20-07 |
| HVT-0006 Taxonomy | 0.6 founder-approved | 1.0 Approved | DR-2026-11-20-08 |
| HVT-0006-OVL-0001 (BUT-0001 overlay) | 0.2 | 1.0 Approved | DR-2026-11-20-04 |
| HVT-0006-OVL-0002 … 0007 | did not exist | 1.0 Approved (new IDs) | DR-2026-11-20-10 |
| HVT-0006-Q-0001 queue index | 0.3 | 1.0 Approved | DR-2026-11-20-10 |
| HVT-0007 Marketplace & Catalog | 0.2 founder-approved | 1.0 Approved | DR-2026-11-20-09 |
| BUT-0002 … BUT-0007 cards | 0.1/0.2 approved cards, pending Raj + Stan Lee | 1.0 Approved (classification only) | DR-2026-11-20-10 |
| DOC-0001 / DOC-0004 / DOC-0005 | 1.1 | 1.2 Approved (cross-references) | DR-2026-11-20-02 |
| DOC-0006 / DOC-0007 | 0.2 Draft | 1.0 Approved | DR-2026-11-20-02 |
| DOC-0008 Progressive Build Session | 0.3 Draft | 1.0 Approved ("APPROVED DOC-0008") | DR-2026-11-20-03 |
| DOC-0009 Stan Lee hibernation brief | 0.2 | 1.0 Approved (§9 added) | DR-2026-11-20-10 |
| DOC-0010 QA Release Gate & Privacy Checklist | did not exist | 1.0 Approved (next free DOC ID; DOC-0002/0003 never reused) | DR-2026-11-20-02 |
| SES-0002 ladder script | 0.2 Draft | 1.0 Approved | DR-2026-11-20-03 |
| SES-0002-F-0001 Mina theatre | 0.1 Draft | 1.0 Approved — filed theatre, not a customer record | DR-2026-11-20-03 |
| SES-0003 live session form | blocked | 1.0 Approved blank (not run) | DR-2026-11-20-03 |
| WL-2026-09-04-01 working list | 0.1 | 0.2 Superseded (by HVT-0002 v1.0 / HVT-0006 v1.0) | DR-2026-11-20-06 |
| Studio (studio_core) | 0.3.0, interim labels | 0.3.0, all 17 actions Approved | DR-2026-11-20-11 |
| ENG-0004 Configurator | Registered, not built | Built as `foundry_os` 1.0.0; maturity Prototype | DR-2026-11-20-11 |

## 2. Draft decision records carried (text unchanged, Art. V.4)

| Draft record | Carried by |
|---|---|
| DR-2026-09-04-10a | DR-2026-11-20-04 (signed off) |
| DR-2026-09-04-11 | DR-2026-11-20-04 (closed as Superseded; §3 Search accepted) |
| DR-2026-09-25-01 | DR-2026-11-20-02 (Approved) |
| DR-2026-09-25-02 | DR-2026-11-20-02 (Approved) |
| DR-2026-09-25-03 | DR-2026-11-20-02 (Approved) |
| DR-2026-09-25-04 | DR-2026-11-20-02 / -09 (Approved; fact-check applied) |
| DR-2026-09-25-05 | DR-2026-11-20-02 (Approved; DOC-0006/0007 at 1.0) |
| DR-2026-09-25-06 | DR-2026-11-20-02 / -07 (Approved; HVT-0003/0004 at 1.0) |
| DR-2026-09-25-07 | DR-2026-11-20-02 / -11 (Approved) |
| DR-2026-09-26-08 | DR-2026-11-20-02 / -11 (Approved) |
| DR-2026-09-26-09 | DR-2026-11-20-11 (Approved) |

DR-2026-09-04-13 was reserved and never issued; it is retired unused (DR-2026-11-20-04).

## 3. Code changes

- `kernel/foundry_kernel.py`: AUTHORITY_SOURCE cites HVT-0002 v1.0 (table unchanged); `family_of` relationship added; status words for Sector, Market Industry, Business Model, Problem, Integration, Solution Component and Business Type added (HVT-0004 v1.0). The Agent table is unchanged: only CEO Agent and Chief Architect.
- `studio/studio_core.py`: labels now say "Approved — DR-2026-11-20-11"; sector / industry read from graph edges for every type; gaps generated from each card; Solution Component industry tags per card. The CEO Agent is still refused every Studio action.
- `foundry_os/`: new ENG-0004 ladder, governance verifier, and CLI, with 21 tests.
- `graph/foundry_graph.json`: 72 → 136 objects (tools/apply_completion_2026_11_20.py, idempotent).

## 4. Tests

- Before: **189 passed** (kernel + studio).
- After: **210 passed, 0 failed** (189 existing + 21 new `foundry_os` tests). `python3 -m foundry_os verify` → ok.
- Three existing assertions pinned the old *pending* state and were amended. Each keeps the old assertion as a comment:
  1. `kernel/test_kernel.py::test_01` — Constitution version 1.2 → 1.3 (Art. XIV.6).
  2. `studio/test_studio.py::test_card_summary_type_shows_gaps_honestly` — BUT-0006 is now a full Approved card; the test now checks the gaps stay honest (out-of-scope listed, Stan Lee veto listed, nothing "pending").
  3. `studio/test_studio_v2.py::test_new_actions_are_in_the_studio_map_and_draft` — labels now cite DR-2026-11-20-11 and EXC-2026-11-20-01, not "founder-approved interim / pending Chief Architect review".

No other test changed. ENG-0005/0006 are still unregistered, and the Agent set is still exactly the two HVT-0002 rows.

## 5. Still needs a live human (cannot be done by a document)

1. The first real owner session on SES-0003. This includes the Square vs sheet choice, made by that owner.
2. Brand Intake and the Stan Lee Design veto before any public surface. These are deferred, not waived.
3. A DOC-0010 QA release for each shop before anything goes live (CEO Office under EXC-2026-11-20-01 until 2027-05-20).
4. Native-speaker checks of any non-English copy (BUT-0002/0003).
5. Running connectors with real owner keys (Square, Google Business Profile, WhatsApp Business).
6. Vendor facts still marked unverified (QuickBooks and others in HVT-0007).
7. Legal review: supplier price-list ingest (BUT-0002) and the clinic records boundary (BUT-0006).
8. The ENG-0005 trigger: registration only on the first live owner evidence of the two-source stock gap (DR-2026-11-20-05).
9. Filling the Chief Architect and QA offices before EXC-2026-11-20-01 expires on 2027-05-20.
