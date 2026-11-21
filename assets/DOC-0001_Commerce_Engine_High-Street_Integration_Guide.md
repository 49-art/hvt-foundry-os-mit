Document ID: DOC-0001  
Title: Commerce Engine High-Street Integration Guide  
Version: 1.2  
Previous version: 1.1  
Status: Approved  
Previous status (v1.1): Approved by Founder (Travis Lee Swift), 18 Oct 2026  
Approval record: DR-2026-11-20-12 (earlier: DR-2026-10-18-01)  
Owner: Architecture Office  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-01)  
Dependencies: HVT-0001, ENG-0003  

---

# DOC-0001 — Commerce Engine High-Street Integration Guide

Document Class: Documentation Asset (Business Asset, per HVT-0003 asset-class scheme) Effective Date: Pending Approval Review Cycle: Continuous — promoted to Reusable Asset only after use in two real high-street projects (per HVT-0001 Art. III.3.a)

## Origin

This asset was created to resolve an open traceability gap logged in HVT-0003 §2: ENG-0003 (Commerce Engine) listed DOC-0001 as a dependency before DOC-0001 existed as a registered asset. This document is that asset. The gap is closed by this document’s creation, not by silent removal of the reference — per HVT-0001 Art. V.

## Purpose

Practical instructions for a high-street business (café, salon, independent retailer, local service, clinic, etc.) to take payments, manage simple subscriptions, and issue receipts without technical staff. Written for the business owner, not a developer.

## Objective Filter

This document, and the integration path it describes, is held to the high-street filter set by Architecture Office decision on 2026-08-04:

1. Does it solve a concrete daily problem a high-street owner actually has?
2. Can a non-technical owner approve it and have it live in minutes, not weeks?
3. Does it leave a reusable Business Asset behind so the next high-street client is cheaper and faster?

## What the Owner Can Do After Approval

- Accept card, contactless, Apple Pay, and Google Pay in under 5 minutes Create a simple membership or loyalty scheme Send automatic receipts and basic invoices See daily takings from a phone

## Instant Integration Path

1. Customer approves the Commerce package in the Foundry portal.
2. System generates a one-click install link.
3. Owner connects their existing Stripe / Square / local bank account — no new account forced (per HVT-0001 Art. VIII, customer assets belong to the customer, and Art. VI.2, provider interchangeability).
4. Live within the same session.

## Explicitly Out of Scope

Per the high-street objective filter, this integration path does not include: enterprise-grade checkout customization, multi-location inventory sync, or any step requiring a technical intermediary between owner approval and go-live.

## Reuse Status

Status: Draft. Promotion to Reusable Asset requires documented use in at least two distinct high-street projects, consistent with the reuse-history bar already met by ENG-0003 itself.

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-04 | Created to resolve HVT-0003 §2 Issue A (Architecture Office decision, Howard direction). Registered as dependency of ENG-0003. |
| 1.1 | 2026-10-18 | Approved by Founder (Travis Lee Swift), 18 Oct 2026. Approved by the founder. Text unchanged from v1.0. Founder's words: “APPROVE EVERYTHING IN THE WAY YOU FEEL IT SHOULD BE.” See DR-2026-10-18-01. |
| 1.2 | 2026-11-20 | Approved. Status normalised to the Appendix A vocabulary (was “Approved by Founder”). Text unchanged. Owner's instruction, 20 Nov 2026: “can you complete all decisions waiting and complete it.” See DR-2026-11-20-12. |
