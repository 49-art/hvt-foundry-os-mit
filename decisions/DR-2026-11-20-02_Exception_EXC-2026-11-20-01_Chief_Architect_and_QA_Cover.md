# DR-2026-11-20-02 — Art. XII Exception EXC-2026-11-20-01: CEO Office covers the vacant Chief Architect review and the QA release sign-off

Document ID: DR-2026-11-20-02  
Title: Art. XII Exception EXC-2026-11-20-01 — CEO Office covers Chief Architect review and QA release sign-off while those roles are vacant  
Version: 1.0  
Status: Approved  
Owner: CEO Office  
Reviewed By: Tony Adams (Raj), CEO Office — 20 Nov 2026 (DR-2026-11-20-01)  
Dependencies: HVT-0001 Art. IV, XII; HVT-0002 §3.1, §3.2, §3.11, §4.2, §5.2, §5.3; DR-2026-10-18-01 §4; DOC-0010  

---

## 1. Problem

HVT-0002 §4.2 names a Chief Architect, but nobody holds that role. Quality Assurance (§3.11) is unstaffed too. DR-2026-10-18-01 §4 left six items "Approved by Founder — interim", waiting on a review that nobody could do. Nobody has signed a QA release either.

## 2. Exception (HVT-0001 Art. XII.1 fields)

| Field | Value |
|---|---|
| Exception ID | EXC-2026-11-20-01 |
| Articles deviated from | HVT-0002 §3.2 and §4.2: Chief Architect reviews and approvals (HVT-0003 ownership, asset maturity promotion). HVT-0002 §3.11 and §5.2: QA release sign-off |
| Reason | Both roles are vacant. Leaving them vacant blocks approved work indefinitely, and no reviewer can be invented (Art. IV) |
| Scope | (a) The CEO Office (Tony Adams) does the Chief Architect review on HVT-0003, HVT-0004, DOC-0006, DOC-0007, and the Studio action maps DR-2026-09-25-07, DR-2026-09-26-08 and DR-2026-09-26-09. (b) The CEO Office signs each QA release using the DOC-0010 checklist, **one release at a time, for a named shop**. The automated test suite is evidence for QA. It is not the sign-off |
| Duration | From 20 Nov 2026. **Expires 20 May 2027**, unless renewed by the same process or ended earlier when either role is filled (Art. XII.2) |
| Accountable approver | Tony Adams, CEO Office |

## 3. What this closes

- HVT-0003 → **v1.0 Approved**. HVT-0004 → **v1.0 Approved**. DOC-0006 → **v1.0 Approved**. DOC-0007 → **v1.0 Approved**.
- DR-2026-09-25-01 … -06 and DR-2026-09-25-07 / DR-2026-09-26-08: the "interim" qualifier is removed. Each is **Approved**, and that approval is carried by this record. Their own text is unchanged (Art. V.4).
- Kernel and Studio labels now cite HVT-0002 v1.0 and this Exception instead of "interim, pending Chief Architect review".

## 4. What this does NOT do

- It does not promote any asset's maturity. ENG-0001, ENG-0002 and ENG-0004 stay **Prototype**. ENG-0003 stays **Reusable Asset**. The kernel stays **Prototype**. Promotion needs real reuse (Art. III), and a stamp cannot supply that.
- It does not sign a QA release for any shop, because no shop is live. The first real release needs a DOC-0010 sign-off on that day.
- It does not touch Stan Lee's Design veto.

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-20 | Exception logged and in effect until 2027-05-20. |
