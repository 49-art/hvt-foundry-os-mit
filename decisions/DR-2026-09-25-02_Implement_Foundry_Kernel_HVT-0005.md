# DR-2026-09-25-02 — Decision Record — Implement the Foundry Kernel (HVT-0005) code

Document ID: DR-2026-09-25-02  
Title: Decision Record — Implement the Foundry Kernel (HVT-0005) code  
Version: 0.1  
Status: Draft  
Owner: Architecture Office  
Reviewed By: pending — not reviewed  
Drafted By: AI executor (Grok Bot) on instruction from Travis Lee Swift, 2026-09-25  
Dependencies: README ("The Foundry Kernel", "Run it"), HVT-0001 Art. IV, Appendix A; HVT-0002 §4; HVT-0004 §3–§5  

---

## Decision

The kernel described in the README, which the record says does not exist yet, is written to that description: kernel/foundry_kernel.py, kernel/demo_boot.py, kernel/test_kernel.py, plus requirements.txt and LICENSE (MIT). Standard library only. The code was run and all tests pass.

## Action Taken

1. **foundry_kernel.py** enforces the README's four hard-gated boot steps:
    - Gate 1 — load the Constitution; refuse unless its header says Document ID HVT-0001 and Status Approved.
    - Gate 2 — load the object graph; refuse if the Constitution is not loaded; check the HVT-0004 universal fields, unique IDs, status words per class, relationship words, no dangling IDs, and that reuse_count is never stored (HVT-0004 §5 says it is derived).
    - Gate 3 — register Agents; refuse anything that is not Agent class, or not in the graph, or not in exactly one Office, or not a row in HVT-0002 §4.2.
    - Gate 4 — run a workflow; allow only actions the HVT-0002 §4.2 table gives the Agent's Office; refuse closed otherwise. Even allowed actions return "pending_human_review", never a final answer (HVT-0001 Art. IV).
    - Every success and refusal is written to an audit log.
2. **demo_boot.py** runs all four gates on the real files and shows the two refusals the README asks for (Chief Architect trying to approve a Constitution amendment; trying to register ENG-0003 as an Agent), plus a boot-order refusal.
3. **test_kernel.py** — 23 tests. Result on 2026-09-25: **23 passed** (Python 3.13.5, pytest 9.1.1). demo_boot.py exit code 0, 3 of 3 expected refusals.
4. requirements.txt lists pytest only (for tests). LICENSE: MIT, Copyright (c) 2026 Travis Lee Swift / HVT Foundation.

## Rationale

The README promises a kernel that "hasn't actually demonstrated it enforces anything" unless it shows refusals. The tests prove each gate refuses when it should. The authority table is taken only from the two Agent rows that exist in HVT-0002 §4.2 (CEO Agent, Chief Architect); no other Agent or Office power was invented.

## Authority

Prepared on the direct instruction of Travis Lee Swift (project owner). It is a Draft: under HVT-0001 Art. IV (AI output must be reviewable and is not authoritative until a qualified human accepts it) and Art. V.3, it carries no institutional weight until reviewed. Nothing in this record approves, stamps or signs anything on behalf of Raj, Stan Lee, Howard, Leonard or any Office.

## Traceability

- Implements: README "The Foundry Kernel"; HVT-0005 (code, not a Markdown document).
- Reads: governance/HVT-0001_Constitution.md; graph/foundry_graph.json (DR-2026-09-25-03).
- HVT-0002 is still Draft v0.2, so the kernel's authority table is labelled as coming from a Draft.
- The Agent ID prefix AGT- is a kernel working label; HVT-0004 defines none (flagged in HVT-0004 v0.2 Draft §2.2).

## Explicitly Not Done

- **ENG-0005 Local Stock Ledger was not coded.** Its spec (DR-2026-09-04-11 §3) is concrete, but DR-2026-09-04-12 (Approved) puts it on HOLD: "Not refused. Not registered. Not coded." Coding it would break that decision.
- ENG-0004 Configurator was not built (DR-2026-09-04-10a rejected running it).
- No new Agents were created. Job A (HVT-0002 bump with more Agent rows) was not done.

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-09-25 | Draft. Kernel, demo, 23 tests written and run: 23 passed. |
