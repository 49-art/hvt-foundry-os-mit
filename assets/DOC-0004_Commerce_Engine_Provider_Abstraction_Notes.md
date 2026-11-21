Document ID: DOC-0004  
Title: Commerce Engine Provider Abstraction Notes  
Version: 1.2  
Previous version: 1.1  
Status: Approved  
Previous status (v1.1): Approved by Founder (Travis Lee Swift), 18 Oct 2026  
Approval record: DR-2026-11-20-12 (earlier: DR-2026-10-18-01)  
Owner: Architecture Office  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-01)  
Dependencies: HVT-0001 Art. VI.2, ENG-0003  

---

# DOC-0004 — Commerce Engine Provider Abstraction Notes

Document Class: Documentation Asset (Business Asset, per HVT-0003 asset-class scheme) Effective Date: Pending Approval Review Cycle: Continuous — promoted to Reusable Asset only after use in two real high-street projects (per HVT-0001 Art. III.3.a)

## Origin

This asset was created to resolve an open traceability gap logged in HVT-0003 §2: ENG-0003 (Commerce Engine) listed DOC-0004 as a dependency before DOC-0004 existed as a registered asset. This document is that asset.

## Purpose

Documents how the Commerce Engine stays interchangeable between payment providers, so a high-street business is never locked in to a single vendor — satisfying HVT-0001 Article VI.2 (every module must be replaceable, every AI/service provider must be interchangeable) as applied specifically to payments infrastructure.

## Abstraction Principle

The Commerce Engine talks to a single internal payment interface. Stripe, Square, and local bank/acquirer connections are implementations behind that interface, not assumptions baked into the Engine itself. Adding a new provider means writing a new adapter against the existing interface — it does not require changes to any application built on the Engine (Mystic Veil, Sales Trainer, Law Firm, Estate Agent, or any future high-street package).

## What This Guarantees the High-Street Owner

- No forced migration to a new payment account to go live.
- If a provider changes terms or the Foundry adds a better-priced option, the owner’s data, history, and configuration carry over — the Engine’s obligation, not the owner’s task.
- Consistent with HVT-0001 Art. VIII: the customer’s transaction history and account relationships are the customer’s asset, not the Foundry’s or the provider’s.

## Current Supported Providers (Draft)

- Stripe Square Direct local bank / acquirer connection (region-dependent)

This list is expected to grow. Adding a provider is a Package-level change under ENG-0003, logged in HVT-0003 on release, not a Constitutional or Registry-level change.

## Reuse Status

Status: Draft. Promotion to Reusable Asset requires documented use in at least two distinct high-street projects.

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-04 | Created to resolve HVT-0003 §2 Issue A (Architecture Office decision, Howard direction). Registered as dependency of ENG-0003. |
| 1.1 | 2026-10-18 | Approved by Founder (Travis Lee Swift), 18 Oct 2026. Approved by the founder. Text unchanged from v1.0. Founder's words: “APPROVE EVERYTHING IN THE WAY YOU FEEL IT SHOULD BE.” See DR-2026-10-18-01. |
| 1.2 | 2026-11-20 | Approved. Status normalised to the Appendix A vocabulary (was “Approved by Founder”). Text unchanged. Owner's instruction, 20 Nov 2026: “can you complete all decisions waiting and complete it.” See DR-2026-11-20-12. |
