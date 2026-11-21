# DR-2026-09-25-04 — Decision Record — Fact-check of Solution Component records against public vendor pages

Document ID: DR-2026-09-25-04  
Title: Decision Record — Fact-check of Solution Component records (SLC-0001…0008) against public vendor pages  
Version: 0.1  
Status: Draft  
Owner: Architecture Office  
Reviewed By: pending — not reviewed  
Drafted By: AI executor (Grok Bot) on instruction from Travis Lee Swift, 2026-09-25  
Dependencies: HVT-0006 §6.4 (INT-0001…0007); HVT-0007 §3–§5 (SLC-0001…0008); DR-2026-09-04-10  

---

## Decision

Each field on the eight Solution Component records (and the INT records they supersede) was checked against the vendor's own public web pages on **2026-09-25**. Each field is marked **Verified**, **Partly verified**, **Inaccurate / out of date**, or **Unverified**, with the page used. The records themselves are **not edited**; this DR is the evidence a reviewer can use to update them.

## Action Taken

Legend: ✅ Verified · ◐ Partly verified · ✗ Record does not match the vendor page · ? Unverified (not checked or could not be reached). All pages were read on 2026-09-25.

### SLC-0001 Stripe (INT-0001)

| Field (record value) | Result | Evidence |
|---|---|---|
| Countries "46+" (SLC) / "170+" (INT) | ✅ 46 / ✗ 170+ | stripe.com/use-cases/global-businesses — "Available for businesses in 46 countries"; customers can pay from 195+ countries. 46 is the business-location figure. 170+ does not match the current business figure. Answers the discrepancy flagged in HVT-0007 §5.1. |
| Monthly cost "None (transaction fees apply)" | ✅ | stripe.com/gb/pricing — "No setup fees, monthly fees"; standard UK cards 1.5% + 20p. |
| Features [Subscriptions, Invoices, Tax] | ✅ | stripe.com/gb/pricing — product menu lists Billing/Subscriptions, Invoicing, Tax. |
| Deployment "~5 minutes to enable" | ? | Not checked. |
| Support level "Standard" | ? | Not checked. |

### SLC-0002 Square (INT-0002)

| Field (record value) | Result | Evidence |
|---|---|---|
| Countries "~8 (US, UK, Canada, Australia, Ireland, France, Spain, Japan)" | ✅ exactly 8, same list | developer.squareup.com/docs/international-development; square.site/help/gb/en/article/4956-international-availability |
| Monthly cost "None (transaction fees); paid tiers for advanced POS" | ✅ | squareup.com/gb/en/pricing — Free plan £0/month + processing fees; Plus from £29/month. |
| Features [In-person POS, Online checkout, Invoices, Loyalty add-on] | ✅ | squareup.com/gb/en/pricing — Invoices and Online store from £0; Loyalty "Starting from £25/mo". |
| Low-stock alerts (DR-10 path S1) | ◐ | squareup.com/help/gb/en/article/8333-create-inventory-alerts — alerts can be set per item; email sent 90 minutes after each location's closing time; no plan restriction stated. Whether it works on the **owner's actual plan** is still to confirm (DR-10). |

### SLC-0003 Google Calendar (INT-0003)

| Field | Result | Evidence |
|---|---|---|
| Monthly cost "Free (business tiers via Google Workspace)" | ✅ | support.google.com/calendar/answer/16287038 — personal accounts get a single booking page; more features need eligible Workspace / Google One plans. |
| Features: Appointment sync | ◐ | Same page — basic appointment booking page is free. |
| Features: Reminders | ◐ | Same page — automatic email reminders for booked appointments need an eligible paid plan. |
| Features: Shared calendars | ? | Not checked. |
| Countries "Global" | ? | Not checked. |

### SLC-0004 Apple Calendar (INT-0004)

| Field | Result | Evidence |
|---|---|---|
| Monthly cost "Free" | ✅ | support.apple.com/guide/icloud/share-a-calendar-mm6b1a9479/icloud — iCloud calendar sharing, no charge shown. |
| Features: Appointment sync | ◐ | Calendar sharing only; no appointment-booking feature found. |
| Features: Reminders | ? | Not checked. |
| Countries "Global (iCloud accounts)" | ? | Not checked. |

### SLC-0005 WhatsApp Business (INT-0005)

| Field | Result | Evidence |
|---|---|---|
| Monthly cost "Free (app); paid tiers via Platform for automation" | ◐ | The app is free (business.whatsapp.com, read via search index; page is script-built). The Platform is charged **per delivered message by category and country**, not by "tiers" (developers.facebook.com/documentation/business-messaging/whatsapp/pricing; whatsappbusiness.com/products/platform-pricing). **From 1 October 2026** service messages and in-window utility messages become chargeable, with 1,000 free service messages per month per number. |
| Features: Customer chat | ✅ | App: catalog, greeting/away messages, quick replies. |
| Features: Booking confirmations, Reminders | ◐ | Automated confirmations/reminders need the paid Platform (utility messages), not the free app. |
| Countries "Global" | ? | Not checked. |

### SLC-0006 Xero (INT-0006)

| Field | Result | Evidence |
|---|---|---|
| Monthly cost "Paid subscription (tiered)" | ✅ | xero.com/uk/pricing-plans — Ignite £18, Grow £39, Comprehensive £55, Ultimate £70 per month excl. VAT (a temporary discount offer was also shown). |
| Features: Invoicing, Bank reconciliation, Tax reporting | ✅ | Same page; Making Tax Digital supported. |
| Features: "Payroll add-on" | ✗ (UK) | Same page — payroll is included from the Grow plan (1 person), with extra people charged; it is not a separate add-on in the UK. |
| Countries "Primarily UK, AU, NZ, US…" | ◐ | UK, NZ and US vendor sites seen; other editions only from a secondary summary. |

### SLC-0007 QuickBooks (INT-0007) — **UNVERIFIED**

All fields remain unverified. The Intuit pages did not load from the box or the fetch tool on 2026-09-25. Search-engine summaries gave plan prices and country lists, but those were not confirmed on Intuit's own site, so they are **not recorded here**.

### SLC-0008 Apple Pay

| Field | Result | Evidence |
|---|---|---|
| Countries "70+ markets" | ✗ out of date | support.apple.com/en-us/102775 (published 9 Sep 2026) lists **101** countries and regions. |
| Pricing "Apple does not charge merchants directly" | ✅ | apple.com/uk/apple-pay — "Apple does not charge any fees when you use Apple Pay… If your business already accepts credit and debit cards, simply contact your payment provider." |
| Deployment "SDK / StoreKit integration" | ? / questionable | The Apple merchant page sends businesses to their payment provider; it does not mention StoreKit. Not confirmed. |
| Supported industries, Support level | ? | Not checked. |

### Related path evidence (DR-2026-09-04-10 R1)

Google Business Profile API: reviews.list and reviews.updateReply exist (developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews/list and /updateReply). They need a verified location and the business.manage permission. HVT's own API access approval was not checked.

## Rationale

The README and HVT-0006 §6.4 say these records must be confirmed "before any of them power a real customer-facing configurator". Recording the evidence per field, with its source and date, lets a reviewer update the records without redoing the work, and keeps anything not confirmed clearly marked.

## Authority

Prepared on the direct instruction of Travis Lee Swift (project owner). It is a Draft: under HVT-0001 Art. IV (AI output must be reviewable and is not authoritative until a qualified human accepts it) and Art. V.3, it carries no institutional weight until reviewed. Nothing in this record approves, stamps or signs anything on behalf of Raj, Stan Lee, Howard, Leonard or any Office.

## Traceability

- Informs (does not edit): INT-0001…0007, SLC-0001…0008, HVT-0006 §6.4, HVT-0007 §5.
- **Fact-checking does not change partner_status.** "Verified" on the Partner Status ladder (HVT-0007 §4) means a business relationship, not a fact check. All partner_status values stay as recorded.
- Vendor pages change. Anything here should be re-checked before use in customer material.

## Explicitly Not Done

- No record field was overwritten.
- QuickBooks, the Tier-3 card candidates (Fresha, Booksy, Treatwell, Phorest, Salon Iris, Cliniko, Jane, Mindbody, Dentally, Shopify POS, Lightspeed, Toast, ServiceTitan, Jobber, Buildertrend, Houzz Pro, Checkatrade, MyBuilder) and Pronto were not verified.
- No vendor was contacted.

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-09-25 | Draft. Field-level fact-check of SLC-0001…0008 against public vendor pages. |
