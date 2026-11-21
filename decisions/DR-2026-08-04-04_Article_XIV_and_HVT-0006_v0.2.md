# DR-2026-08-04-04 — Decision Record — Constitutional Amendment (Article XIV) and HVT-0006 v0.2: BusinessType Canonical Schema and First Registered Instance

Document ID: DR-2026-08-04-04  
Title: Decision Record — Constitutional Amendment (Article XIV) and HVT-0006 v0.2: BusinessType Canonical Schema and First Registered Instance  
Version: 1.0  
Status: Approved  
Owner: Architecture Office  
Reviewed By: Chief Architect  
Dependencies: HVT-0001 Art. XI, Art. V, HVT-0002 §3.2, HVT-0004, HVT-0006  

---

## Part 1 — Constitutional Amendment (Article XI Procedure)

### 1.1 Article Affected

New Article. Inserted as Article XIV — The Model-First Doctrine, between Article XIII (Business Asset Doctrine) and Appendix A.

### 1.2 Proposed Change

Howard (Special Advisor) proposed the following as “the one Architecture Office decision” for this session: the Foundry should never ask “What software should I build?” — it should ask “What business is this, how does it operate, what problems does it face, and which combination of reusable Foundry assets solves those problems?” Software becomes an output of that model, not its starting point.

Architecture Office elevates this from guidance to a binding Constitutional Article rather than logging it only as a Decision Record, per the confirmed decision that this principle should carry Constitution-level force.

### 1.3 Rationale

Article II already mandates an Engine Search before new capability is built. Article XIV makes explicit what Article II presumes: that a business has been classified — its problems, capabilities, and candidate engines identified — before the Engine Search itself even runs. Without this Article, “search for an existing engine” has no defined input; Article XIV supplies it. This is also the natural home for the Business Ontology work now underway in HVT-0006: the ontology is not a side project, it is the mechanism by which Article XIV is satisfied.

### 1.4 Review

Reviewed under HVT-0002 §3.2 (Architecture Office decision authority) and HVT-0001 Art. V (decision documentation). No alternatives were rejected; the principle was accepted as proposed, worded to fit the Constitution’s existing Article style (see HVT-0001 Art. XIV.1–.5).

### 1.5 Version Increment

HVT-0001: v1.0 → v1.1. Changelog entry appended in the Constitution itself, per Art. XI.1.c.

### 1.6 Effect

Per Art. XI.2, this amendment governs future work only. It does not retroactively fault prior engagements (Mystic Veil, Sales Trainer, Law Firm, Estate Agent) for having been built before a formal Business Ontology existed.

## Part 2 — HVT-0006 v0.2: BusinessType Canonical Schema

### 2.1 Decision

Howard proposed a flat, 12-field BusinessType schema (Name, Sector, Common Problems, Required Capabilities, Optional Capabilities, Recommended Engines, Recommended Packages, Integrations, Deployment Targets, Pricing Bands, Time to Deploy, Complexity Score) as the practical unit of the Business Ontology — one record per business type, not a join across many object types.

Per confirmed scope: this layers on top of the HVT-0006 v0.1 seven-type graph model rather than replacing it. The graph stays normalized (Sector, Industry, Business Type, Problem, Integration, etc. as distinct objects with relationships) for traceability and machine querying (HVT-0004 §6). BusinessType is added as the canonical read/query shape — a denormalized card that answers “what does this business need” in one lookup, generated from the underlying graph rather than competing with it.

### 2.2 Prefix Collision Resolved

HVT-0006 §8 (v0.1) flagged a collision: the proposed “Industry” taxonomy type wanted prefix IND-####, already used by “Industry Template” assets in HVT-0003. Resolved per the resolution HVT-0006 §8 itself proposed: the taxonomy type is renamed Market Industry, prefix MKT-####. IND-#### remains reserved for Industry Template assets, unchanged. This is a mechanical resolution of an already-identified, already-proposed fix — not a new design decision — and is executed now because the first real instance (§2.3) requires an unambiguous prefix.

### 2.3 First Registered Instance: Hair Salon

Per confirmed scope, the Hair Salon example is promoted from illustrative documentation (HVT-0006 v0.1 §2.2) to a real registered BusinessType instance in the object graph, using the new canonical schema. Supporting objects created:

- SEC-0001 — Sector: Services MKT-0001 — Market Industry: Personal Care BUT-0001 — Business Type: Hair Salon (the canonical card)
- PRB-0001–PRB-0005 — five Problem objects (Missed appointments, Empty time slots, No repeat customers, Manual stock, Slow checkout)
- INT-0001–INT-0007 — seven Integration objects (Stripe, Square, Google Calendar, Apple Calendar, WhatsApp Business, Xero, QuickBooks)

Engine gap, not silently filled: the Hair Salon card’s “Recommended Engines” honestly maps to what is actually registered — ENG-0001 (Local Customer Engine), ENG-0002 (Local Content & Booking Engine), ENG-0003 (Commerce Engine) — and explicitly flags two capabilities (Stock management, Review/reply management) for which no Engine is yet registered. Per Article II, these require an Engine Search before any new Engine is built for them; none is authorized by this Decision Record.

Integration data provenance: Stripe’s card fields (category, cost, countries, features, compatible engines, alternatives) reproduce the data Howard supplied directly. The remaining six Integration cards are populated from general market knowledge and marked as best-effort in HVT-0006 §6.4, not verified against current vendor documentation — flagged for confirmation before being treated as authoritative for a real customer-facing configurator.

### 2.4 Version Increment

HVT-0006: v0.1 → v0.2.

## Authority

Part 1 issued under HVT-0001 Art. XI (Amendment Procedure). Part 2 issued under HVT-0001 Art. V and Art. XIII, HVT-0002 §3.2 (Architecture Office decision authority).

## Traceability

- Amends: HVT-0001 (Constitution), adding Article XIV.
- Extends: HVT-0006 v0.1 → v0.2.
- Resolves: HVT-0006 §8 item 1 (IND-#### prefix collision).
- Related: DR-2026-08-04-01, -02, -03 (same working session).
- Open follow-ons: Engine Search for Stock and Review capabilities (Art. II); verification of the six non-Stripe Integration cards; HVT-0004 v0.2 formal adoption of HVT-0006’s proposed object/relationship types (still pending, unchanged from DR-2026-08-04-03).

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-04 | Decision issued and executed. |
