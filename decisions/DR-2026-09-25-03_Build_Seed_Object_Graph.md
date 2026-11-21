# DR-2026-09-25-03 — Decision Record — Build graph/foundry_graph.json from the record

Document ID: DR-2026-09-25-03  
Title: Decision Record — Build graph/foundry_graph.json from the record  
Version: 0.1  
Status: Draft  
Owner: Architecture Office  
Reviewed By: pending — not reviewed  
Drafted By: AI executor (Grok Bot) on instruction from Travis Lee Swift, 2026-09-25  
Dependencies: HVT-0004 §3–§7; HVT-0006 §2–§6, §9; HVT-0006-OVL-0001; HVT-0007 §3–§5; DR-2026-08-04-01…09; DR-2026-09-04-10…14  

---

## Decision

graph/foundry_graph.json, referred to throughout the record but not present, is built only from objects and data stated in the documents: 72 objects. Where the documents are unclear, the graph records the uncertainty instead of choosing.

## Action Taken

1. Documents HVT-0001/2/3/4/6/7 and overlay HVT-0006-OVL-0001; Agents CEO Agent and Chief Architect (the two HVT-0002 §4.2 rows); Engines ENG-0001…0004; Documentation DOC-0001, 0004, 0005, 0008, 0009 and the new Drafts DOC-0006, 0007; WKF-0001; SEC-0001, MKT-0001; PRB-0001…0005; BUT-0001 (full card plus overlay data) and BUT-0002…0007 (card status only); INT-0001…0007 (unedited); SLC-0001…0008; SES-0001, WSH-0001; all Decision Records.
2. ENG-0003 has four used_by edges (Mystic Veil, Sales Trainer, Law Firm, Estate Agent), so its derived reuse_count is 4, matching HVT-0003.
3. solves edges follow the record. PRB-0004 (Manual stock) has **no** solving Engine — it is the capability gap.
4. WSH-0001 stays "Configured" with the overlay prose kept separately (DR-2026-09-04-10a said prose is not a status value).
5. ENG-0005 and ENG-0006 are **not** in the graph. They are listed under "held_not_registered".

## Rationale

The kernel needs a real graph to load, and the README says the graph carries the Hair Salon pilot end to end. Building it only from the record keeps the Markdown authoritative (HVT-0004 §1).

## Authority

Prepared on the direct instruction of Travis Lee Swift (project owner). It is a Draft: under HVT-0001 Art. IV (AI output must be reviewable and is not authoritative until a qualified human accepts it) and Art. V.3, it carries no institutional weight until reviewed. Nothing in this record approves, stamps or signs anything on behalf of Raj, Stan Lee, Howard, Leonard or any Office.

## Traceability

- **SLC numbering is partly inferred.** Explicit in the record: SLC-0001 Stripe, SLC-0002 Square (DR-2026-09-04-10), SLC-0008 Apple Pay. SLC-0003…0006 follow the order of HVT-0007 §5.2. QuickBooks was given **SLC-0007 provisionally**, because HVT-0007 §5.2 fits six vendors into five IDs. Each SLC object carries an id_provenance note. Needs confirming.
- The unresolved DOC-0001/DOC-0004 placeholder objects that DR-2026-08-04-01 says were "marked superseded" are not recreated, because the original JSON file never existed to copy from.
- Status "Registered" is used as a descriptive word for Sector, Market Industry, Business Type, Problem and Solution Component, because no source defines a vocabulary for those classes. Flagged in HVT-0004 v0.2 Draft §4.1.
- Each SLC object points to DR-2026-09-25-04 for its fact-check.

## Explicitly Not Done

- No price, country count or feature was added that is not in the record.
- The Tier-3 names on BusinessType cards (Fresha, Booksy, etc.) were not registered as SLC objects; they remain unverified candidates.
- Pronto (SLC-0009 candidate) was not registered.

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-09-25 | Draft. Seed graph built: 72 objects; loads cleanly in the kernel. |
