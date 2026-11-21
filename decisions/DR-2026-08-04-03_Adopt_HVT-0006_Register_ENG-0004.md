# DR-2026-08-04-03 — Decision Record — Adopt Industry & Compatibility Taxonomy (HVT-0006) and Register Configurator Engine (ENG-0004)

Document ID: DR-2026-08-04-03  
Title: Decision Record — Adopt Industry & Compatibility Taxonomy (HVT-0006) and Register Configurator Engine (ENG-0004)  
Version: 1.0  
Status: Approved  
Owner: Architecture Office  
Reviewed By: Chief Architect  
Dependencies: HVT-0001 Art. V, HVT-0002 §3.2, HVT-0004, HVT-0006  

---

## Decision

Howard (Special Advisor) provided two taxonomy chains and three data-card templates describing how an Industry should resolve down to a priced, deployable configuration of Engines, Packages, Products, and Integrations. Architecture Office resolves the two chains as two layers of one model — an abstract schema layer and an applied instance layer — and formalizes both as HVT-0006, a governed extension of HVT-0004 (Object Model).

A new Engine, the Configurator Engine (ENG-0004), is registered at Prototype status to run the taxonomy traversal HVT-0006 defines.

## Action Taken

1. Created HVT-0006 — Industry & Compatibility Taxonomy, defining:
    - The ten-level taxonomy spine (Sector → Industry → Business Type → Business Model → Workflow → Problem → Solution/Engine → Package → Product → Integration).
    - The Hair Salon example as an illustrative instance only — not registered as real objects.
    - Seven proposed new object types (Sector, Industry, Business Type, Business Model, Problem, Integration, Product), flagged for formal HVT-0004 adoption rather than silently added to its canonical list.
    - Five cross-cutting attribute dimensions (Deployment, Pricing Tier, Business Size, Budget, Technical Ability), modeled as Product/instance attributes, not taxonomy levels.
    - Six proposed new relationship types (works_with, requires, optional_with, classifies_under, solves, integrates_via).
    - Three data card schemas (Integration, Engine Compatibility, Sizing Filters).
2. Registered ENG-0004 — Configurator Engine — in HVT-0003, Prototype status, composable with ENG-0001, ENG-0002, ENG-0003.
3. Updated foundry_graph.json: added HVT-0006 (Document object), ENG-0004 (Engine object), and this Decision Record as a Decision object, with supporting relationships.

## Explicitly Not Done (Scope Boundary)

Per the confirmed scope for this pass — schema only, no data:

- No Sector, Industry, Business Type, Business Model, Problem, Integration, or Product instance objects were created.
- The Hair Salon example and the Stripe integration card remain documentation-only illustrations.
- HVT-0004 itself was not edited. Its new object types and relationship types are proposed in HVT-0006 and require a separate, later Chief Architect–reviewed version bump (HVT-0004 v0.1 → v0.2) before they are canonical.
- The IND-#### prefix collision between the proposed “Industry” type and the existing “Industry Template” asset class (HVT-0003) was identified but not resolved — logged as an open item in HVT-0006 §8.

## Rationale

Per HVT-0001 Art. V, a document is not amended by another document’s side effect — HVT-0004’s type list is extended by proposal (HVT-0006), not by silent edit. Per Art. XIII, the Foundry accumulates Business Assets deliberately; registering the Configurator Engine at Prototype (not Reusable Asset) status reflects its actual maturity and avoids overstating readiness. Keeping schema and instance data separate in this pass (per confirmed scope) avoids populating the graph with example data that hasn’t cleared the Foundry’s own reuse-history bar.

## Authority

Issued under HVT-0001 Art. V and Art. XIII, HVT-0002 §3.2 (Architecture Office decision authority), extending HVT-0004 per its own §1 (a governed second layer, not a substitute).

## Traceability

- Extends: HVT-0004 (Object Model) — formal amendment pending, see HVT-0006 §8.2.
- Related: DR-2026-08-04-01, DR-2026-08-04-02 (same session, ENG-0003/ENG-0001/ENG-0002 registry gaps).
- Open follow-ons: HVT-0006 §8 (four items, none silently deferred).

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-04 | Decision issued and executed. |
