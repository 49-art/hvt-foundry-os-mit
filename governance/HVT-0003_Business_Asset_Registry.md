Document ID: HVT-0003  
Title: HVT Foundry Business Asset Registry  
Version: 0.4  
Status: Draft  
Owner: Architecture Office  
Reviewed By: Chief Architect  
Dependencies: HVT-0001, HVT-0002, HVT-0006  


> **Kept for the record.** The current version is `HVT-0003_Business_Asset_Registry_v0.6.md` (DR-2026-10-18-01).

> **Kept for the record.** The current version is `HVT-0003_Business_Asset_Registry_v1.0.md` (DR-2026-11-20-02).
---

# HVT Foundry Business Asset Registry

Document Class: Governance Document — Living Register Effective Date: Pending Approval Review Cycle: Continuous (updated on every asset creation, promotion, or reuse event)

## 1. Purpose

This is the register required by HVT-0001, Article VII (Engine Registry) and Article XIII.5 (Business Asset logging). Every Business Asset — Engine, Package, Theme, Plugin, Documentation, Prompt Library, Design System, Industry Template, Test Suite, or Brand Asset — is recorded here for the lifetime of its existence, per Appendix A of HVT-0001: entries are never deleted, only superseded.

Asset IDs use a class-prefixed scheme distinct from Document IDs (HVT-####): ENG-#### for Engines, PKG-#### for Packages, THM-#### for Themes, PLG-#### for Plugins, DOC-#### for Documentation assets, PRL-#### for Prompt Libraries, DSY-#### for Design Systems, IND-#### for Industry Templates, TST-#### for Test Suites, BRD-#### for Brand Assets.

## 2. Open Item — Resolved 2026-08-04

Two traceability gaps were flagged here per Article V (every proposal must be traceable). Both are now resolved by Architecture Office decision. Nothing below has been silently altered — each resolution is logged as a Decision Record, per the Constitution’s instruction not to silently resolve ambiguity in another office’s record.

- Issue A — ENG-0003’s dependencies (DOC-0001, DOC-0004) were unresolved Documentation-class Business Assets. Resolved: both created and registered — see §3 and DR-2026-08-04-01.
- Issue B — ENG-0003 implied ENG-0001 and ENG-0002 existed; neither was logged. Resolved: confirmed as an accidental numbering gap, not prior undisclosed work. ENG-0001 (Local Customer Engine) and ENG-0002 (Local Content & Booking Engine) reserved and defined at Prototype status — see §3 and DR-2026-08-04-02.

Both resolutions were made under the Foundry’s restated high-street objective: every asset must solve a concrete daily problem for a high-street owner, be approvable and go live in minutes, and leave a reusable Business Asset behind.

## 3. Asset Ledger

| Asset ID | Name | Class | Status | Owner | Dependencies | Used By |
|---|---|---|---|---|---|---|
| ENG-0001 | Local Customer Engine | Engine | Prototype | Architecture Office | HVT-0001 | — |
| ENG-0002 | Local Content & Booking Engine | Engine | Prototype | Architecture Office | HVT-0001 | — |
| ENG-0003 | Commerce Engine | Engine | Reusable Asset | Architecture Office | DOC-0001, DOC-0004 | Mystic Veil, Sales Trainer, Law Firm, Estate Agent |
| ENG-0004 | Configurator Engine | Engine | Prototype | Architecture Office | HVT-0006, HVT-0004 | — |
| DOC-0001 | Commerce Engine High-Street Integration Guide | Documentation | Draft | Architecture Office | HVT-0001, ENG-0003 | ENG-0003 |
| DOC-0004 | Commerce Engine Provider Abstraction Notes | Documentation | Draft | Architecture Office | HVT-0001 Art. VI.2, ENG-0003 | ENG-0003 |
| DOC-0005 | High-Street Tablet Design Loop | Documentation | Draft | Architecture Office | HVT-0001 Art. VIII, Art. XIV; HVT-0006; DR-2026-08-04-06; ENG-0004; WKF-0001 | WKF-0001 |

## 4. Ledger Entry Detail

### ENG-0003

Name: Commerce Engine Class: Engine Status: Reusable Asset — per HVT-0001 Art. III.4, this status certifies the asset has cleared Prototype and Engine states, has been used in at least two distinct contexts, and is documented to third-party-adoptable standard. Reuse across four named applications (Mystic Veil, Sales Trainer, Law Firm, Estate Agent) satisfies the reuse-history bar (Art. III.3.a) well beyond the minimum. Owner: Architecture Office, per HVT-0002 §2.2 (Registry ownership). Dependencies: DOC-0001, DOC-0004 — resolved 2026-08-04, see DR-2026-08-04-01. Used By: Mystic Veil · Sales Trainer · Law Firm · Estate Agent Version: 2.3

### ENG-0001

Name: Local Customer Engine Class: Engine Status: Prototype — promotion to Reusable Asset requires use in at least two distinct high-street projects (Art. III.3.a). Owner: Architecture Office. Purpose: Simple CRM + appointment book + basic loyalty for a single-location high-street business. Dependencies: HVT-0001. Used By: None yet. Version: 0.1 Decision Record: DR-2026-08-04-02.

### ENG-0002

Name: Local Content & Booking Engine Class: Engine Status: Prototype — promotion to Reusable Asset requires use in at least two distinct high-street projects (Art. III.3.a). Owner: Architecture Office. Purpose: Simple website + online booking + local map integration, editable by a non-technical owner from a phone. Dependencies: HVT-0001. Used By: None yet. Version: 0.1 Decision Record: DR-2026-08-04-02.

### DOC-0001

Name: Commerce Engine High-Street Integration Guide Class: Documentation Status: Draft — promotion to Reusable Asset requires use in two real high-street projects. Owner: Architecture Office. Dependencies: HVT-0001, ENG-0003. Used By: ENG-0003 (dependency). Version: 1.0 Decision Record: DR-2026-08-04-01.

### DOC-0004

Name: Commerce Engine Provider Abstraction Notes Class: Documentation Status: Draft — promotion to Reusable Asset requires use in two real high-street projects. Owner: Architecture Office. Dependencies: HVT-0001 Art. VI.2, ENG-0003. Used By: ENG-0003 (dependency). Version: 1.0 Decision Record: DR-2026-08-04-01.

### ENG-0004

Name: Configurator Engine Class: Engine Status: Prototype — no instance data yet; runs the HVT-0006 taxonomy traversal once Industry/Business Type/Integration objects exist. Owner: Architecture Office. Purpose: Given a Business Type and its Sizing Filters (Business Size, Budget, Technical Ability), traces Problems → Solutions (Engines) → Packages → Products → Integrations, filtered by Deployment and Pricing Tier, per HVT-0006. Dependencies: HVT-0006, HVT-0004. Composable With: ENG-0001, ENG-0002, ENG-0003 — orchestrates across them, does not replace any. Used By: None yet. Version: 0.1 Decision Record: DR-2026-08-04-03.

### DOC-0005

Name: High-Street Tablet Design Loop Class: Documentation Status: Draft — pilot not yet run. Owner: Architecture Office. Purpose: Step-by-step procedure for running a live tablet session with a high-street owner: classify/re-classify, run the Configurator (ENG-0004), capture wishes, and route them back through Model-First (Art. XIV) and Engine Search (Art. II) between sessions. Dependencies (fuller than the document’s own stated list — see DR-2026-08-04-08): HVT-0001 Art. VIII, Art. XIV; HVT-0006; DR-2026-08-04-06; ENG-0004; WKF-0001. Implements: WKF-0001 (Tablet Feedback & Wish Loop workflow) as a runnable procedure. Pilot: BUT-0001 (Hair Salon). Used By: None yet — no session has been run. Version: 1.0 Decision Record: DR-2026-08-04-08. Open item: the document’s “customer is always right” / “customer’s stated reality overrides” instructions are not yet backed by a Constitutional clause — see DR-2026-08-04-08 for the recommendation.

## 5. Changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-08-04 | Registry initialized. First entry logged: ENG-0003, Commerce Engine, v2.3, Reusable Asset. Dependency IDs flagged for confirmation. |
| 0.2 | 2026-08-04 | §2 Issue A resolved: DOC-0001 and DOC-0004 created and registered as Documentation assets (DR-2026-08-04-01). §2 Issue B resolved: ENG-0001 (Local Customer Engine) and ENG-0002 (Local Content & Booking Engine) reserved and defined as high-street priority Engines at Prototype status; numbering gap closed deliberately (DR-2026-08-04-02). Architecture Office decision, per Howard direction. |
| 0.3 | 2026-08-04 | ENG-0004 (Configurator Engine) registered at Prototype status, per HVT-0006 (Industry & Compatibility Taxonomy) and DR-2026-08-04-03. Schema only — no Industry/Business Type/Integration instance data registered this pass. |
| 0.4 | 2026-08-04 | DOC-0005 (High-Street Tablet Design Loop) registered as Documentation asset, per DR-2026-08-04-08. Implements WKF-0001; pilot BUT-0001. Dependency list in the registry expanded beyond the document’s own stated front matter — flagged, not silently reconciled into the source file. |
