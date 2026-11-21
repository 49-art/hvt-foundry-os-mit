# DR-2026-09-25-07 — Decision Record — Build HVT Foundry Studio (DOC-0005 loop app) on the Foundry Kernel

Document ID: DR-2026-09-25-07  
Title: Decision Record — Build HVT Foundry Studio on the Foundry Kernel  
Version: 0.1  
Status: Draft  
Owner: Architecture Office  
Reviewed By: pending — not reviewed  
Drafted By: AI executor (Grok Bot) on instruction from Travis Lee Swift, 2026-09-25  
Dependencies: DOC-0005; HVT-0001 Art. II, IV, V, VIII, XIV; HVT-0002 §3.2, §4.2; HVT-0006 §4, §7, §9; HVT-0006-OVL-0001; HVT-0007 §7; DR-2026-08-04-06; DR-2026-08-04-09; DR-2026-09-04-10; DR-2026-09-25-02; DR-2026-09-25-04  

---

## Decision

Build a working, tablet-friendly web app, **HVT Foundry Studio** (studio/), that runs the DOC-0005 High-Street Tablet Design Loop end to end on top of the Foundry Kernel and graph/foundry_graph.json. It uses the Python standard library only and starts with `python3 studio/app.py` on http://localhost:8000.

## Action Taken

1. **Kernel change (small, backward-compatible).** `FoundryKernel` accepts an optional, labelled `extra_authority` map. It can only **add** actions to an Office that already exists in the HVT-0002 §4.2 table. It cannot create an Office or redefine a core action, and it requires a source label. Results authorized this way name that label, not HVT-0002. Three kernel tests were added (26 in total).
2. **Studio action map (Draft).** The following eight actions were added to the **Architecture Office only**:
    - open_customer_session
    - classify_business
    - run_configurator
    - record_owner_response
    - capture_customer_wish
    - close_customer_session
    - resolve_wish
    - offer_new_configuration

    The basis is DOC-0005 (an Architecture Office procedure) and the DR-2026-08-04-09 precedent: SES/WSH instances registered by the Architecture Office under HVT-0002 §3.2. Resolving a wish as an Engine Search uses the core `run_engine_search` action. The CEO Agent gets no Studio actions.
3. **Loop implemented:**
    - The boot screen runs all four gates plus three refusal checks.
    - Sessions get IDs from SES-0004 onward, and wishes from WSH-0002 onward (SES-0001–0003 and WSH-0001 already exist in the record).
    - Owner correction of the classification is saved with the owner's own words.
    - The configurator follows the HVT-0006 §7 traversal and uses graph data only. Vendor facts are shown with the DR-2026-09-25-04 fact-check.
    - A plain-language package view lets the owner accept or reject.
    - Wishes are saved verbatim.
    - Closing a session makes it permanent.
    - The review queue offers three outcomes: reconfigure, Engine Search logged, or out of scope.
    - A follow-up session offers a new configuration. The owner's answer on it moves the re-configured wishes to Accepted or Rejected by Customer.
    - There is an audit screen with authority-test buttons.
4. **Persistence:** studio/data/studio_state.json. It is append-only: every change adds a new revision with a `supersedes` pointer, and nothing is deleted.
5. **Tests:** studio/test_studio.py (21 tests) plus kernel tests (26). Result 2026-09-25: **47 passed**. A curl walkthrough of the full loop (studio/curl_walkthrough.sh) was run, and screenshots were taken.

## Rationale

Travis asked for a finished product on the kernel. DOC-0005 is the procedure the record already defines for exactly this use, and BUT-0001 is its named pilot. Routing every action through Gate 4 keeps the Art. IV / V discipline: nothing is authoritative, and everything is traceable.

## Authority

Prepared on the direct instruction of Travis Lee Swift (project owner). It is a Draft: under HVT-0001 Art. IV and V.3, it carries no institutional weight until reviewed. **The Studio action map extends what the Architecture Office's agent may do in software. That extension is itself pending Chief Architect review.** Nothing here approves or stamps anything on behalf of Raj, Stan Lee, Howard, Leonard or any Office.

## Traceability

- Sessions and wishes created in the Studio are **local draft records**. They are not written into foundry_graph.json or any governance document. DOC-0008 is still unapproved, so SES-0003 (the first official live build session) remains blocked. The Studio does not claim to be that session.
- **Size and technical-ability filters are recorded but do not narrow results.** No sizing or skill data exists in the record for any engine or tool, and the Studio says so on screen. Only the budget filter is applied, using prices verified on 2026-09-25.
- **"Out of scope" has no value in the HVT-0006 §9.2 wish vocabulary.** Such wishes keep status "Under Review", and the outcome goes in `resolution`. Flagged.
- A logged Engine Search is a record that one is required. It does not perform the search, and it never authorizes an Engine (DR-2026-08-04-06 binding rule).
- The visual design avoids the DR-2026-09-04-12 refusal-list look ("Inter + teal on white"). Stan Lee's design review is still deferred, so no owner-facing design is approved.

## Explicitly Not Done

- No new Agents, Offices, personas or people. No outside services are called.
- ENG-0004 is not "built" in the HVT-0003 sense. The Studio applies its documented logic to graph data; ENG-0004 stays Prototype.
- No authentication. It is intended for a single trusted machine or network.

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-09-25 | Draft. Studio built and tested (47 passed); kernel extension added. |
