# DOC-0007 — Review Reply Procedure (capability specification + Engine Search record)

Document ID: DOC-0007  
Title: Review Reply Procedure — capability specification for "Review / reply management"  
Version: 1.0  
Previous version: 0.2  
Status: Approved  
Previous status (v0.2): Approved by Founder (Travis Lee Swift), 18 Oct 2026 — interim: the rules also ask for a Chief Architect review, and nobody holds that role yet  
Approval record: DR-2026-11-20-02 (earlier: DR-2026-10-18-01)  
Owner: Architecture Office  
Reviewed By: CEO Office for the vacant Chief Architect role — Tony Adams, 20 Nov 2026 (EXC-2026-11-20-01, DR-2026-11-20-02)  
Dependencies: HVT-0001 Art. II, III.1, VIII, X; DR-2026-09-04-10; DR-2026-09-04-10a; HVT-0006-OVL-0001; ENG-0002; SLC-0005; BUT-0001  
Drafted by: AI executor (Grok Bot) on instruction from Travis Lee Swift, 2026-09-25. Carries no institutional weight until reviewed (HVT-0001 Art. IV.3, V.3).

---

## 1. Why this document exists

DR-2026-09-04-10a lists "DOC-0007 Review Reply Procedure" as an optional Draft, and DOC-0008 treats DOC-0007 as a reserved procedure ID. This Draft fills that slot. It is the written specification for the BUT-0001 capability gap "Review / reply management".

## 2. What this document is NOT

- It is **not an Engine** and does not register ENG-0006. DR-2026-09-04-10 (Approved) found **no new Engine** is justified for reviews.
- It does **not** mint PRB-0006 (still unminted; optional in DR-10a).
- It does **not** change the approved Engine Search result. It restates DR-10 Search 2 with fresh evidence dated 2026-09-25.

## 3. Capability specification (HVT-0001 Art. III.1 terms)

| Item | Specification |
|---|---|
| Capability | Help the owner see new customer reviews and reply to them in their own words. |
| Inputs | Reviews on the owner's Google Business Profile; messages from customers on WhatsApp; a list of completed appointments (for asking for a review). |
| Outputs | A reply written or approved by the owner; optionally, one polite request for a review after a completed appointment. |
| Decision logic | Every public reply is approved by the owner before it is posted. At most one review request per completed appointment. |
| Failure modes | A reply posted without the owner seeing it; an unhappy customer pushed to post publicly; review requests sent too often. All are forbidden (section 7). |
| Ownership | Reviews and customer contact details belong to the owner (Customer Asset, Art. VIII). |
| Human authority | The owner (Art. X). No automatic public replies. |

## 4. Engine Search record (HVT-0001 Art. II.2, in the four-step a → b → c → d form used by DR-2026-09-04-10)

Art. II.2 asks: (a) does an existing engine solve this, in whole or in part? (b) can one be extended, parameterized or composed? (c) only if both are "no", with evidence, may new functionality be authorized. DR-10 added a connectors / owner-owned / free step before the build question. Art. II.3 requires the result to be logged in the registry — see HVT-0003 v0.5 Draft §4A.

| Step | Question | Finding |
|---|---|---|
| a. Existing Engine? | Does a registered Engine reply to reviews? | **No.** |
| b. Extend an Engine? | Within its stated purpose? | **Partial.** DR-10 path R3: "After ENG-0002 completes a slot, send the GBP review link via WhatsApp or SMS. One ask. No nag loop." ENG-0002 (Local Content & Booking Engine) knows when a booking is done, so the one-time ask fits there. Replying to public reviews does not fit any Engine. |
| c. Existing vendor / Solution Component? | Is there a component that already does it? | **Yes — path R1.** Google Business Profile lets the owner reply to reviews. For software access, the Business Profile API has `reviews.list` and `reviews.updateReply` methods (developers.google.com/my-business/reference/rest/v4/accounts.locations.reviews/list and …/updateReply, checked 2026-09-25). They need a verified business location and the `business.manage` permission. Whether HVT could get API access approval was **not** checked. **Path R2:** SLC-0005 WhatsApp Business app — free, with quick replies and greeting/away messages, for private replies. From **1 October 2026**, WhatsApp *Platform* (API) service messages become chargeable after 1,000 free per month per number (developers.facebook.com/documentation/business-messaging/whatsapp/pricing, checked 2026-09-25). This matters only if replies are automated through the Platform. |
| d. New Engine? | Only if a–c fail. | **Not justified.** Result: **PARTIAL MATCH** (same as DR-10). No ENG-0006. |

**Search result: PARTIAL MATCH — unchanged.** Paths as in DR-10: **R1** Google Business Profile replies (owner, by hand), **R2** WhatsApp Business app for private conversations, **R3** one-time review request after ENG-0002 (Local Content & Booking Engine) completes a slot.

## 5. Procedure — replying to public reviews (R1)

1. The owner turns on notifications for their Business Profile in the Google Maps app (or checks the profile on a set day each week).
2. For each new review, the owner reads it and writes a short reply in their own voice. Thank people. For a complaint, apologise, and invite them to talk privately (phone or WhatsApp) — do not argue in public.
3. The owner posts the reply themselves. HVT tooling may suggest wording, but the owner approves every word.

## 6. Procedure — asking for reviews (R3) and private replies (R2)

1. After an appointment is marked complete, send **one** friendly message that thanks the customer and includes the review link. No repeat reminders.
2. Only send to customers who have agreed to receive messages from the salon.
3. If a customer replies unhappy, the owner handles it privately on WhatsApp or by phone. Never steer only happy customers to Google.
4. If this is ever automated through the WhatsApp Platform, check the current message pricing first (it changes on 1 October 2026).

## 7. Things this procedure must never do

- Post a public reply without the owner's approval.
- Offer rewards for reviews, write fake reviews, or filter who gets asked based on how happy they are.
- Store customer contact data inside an HVT asset (Art. VIII).

## 8. Open items (carried, not closed)

- Google Business Profile API access approval for HVT — **not checked**.
- PRB-0006 (review problem) — **unminted**, optional per DR-10a.
- ENG-0002 is a Prototype and is not built; R3 can be done by hand until it is.
- DR-10 recorded the Reviews API "operational detail: unverified". The API methods are now confirmed to exist (section 4); access approval and day-to-day operation remain unverified, so the pilot may be app-only, as DR-10 said.
- This document needs Chief Architect review before it is more than a Draft.

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-09-25 | Draft created by AI executor on instruction from Travis Lee Swift. Restates DR-2026-09-04-10 Search 2 with 2026-09-25 vendor evidence. Not reviewed. |
| 0.2 | 2026-10-18 | Approved by Founder (Travis Lee Swift), 18 Oct 2026 — interim: the rules also ask for a Chief Architect review, and nobody holds that role yet. Approved by the founder as interim. Chief Architect review still to do (role vacant). Text unchanged from v0.1. Founder's words: “APPROVE EVERYTHING IN THE WAY YOU FEEL IT SHOULD BE.” See DR-2026-10-18-01. |
| 1.0 | 2026-11-20 | Approved. Chief Architect review done by the CEO Office under EXC-2026-11-20-01. Text unchanged. Owner's instruction, 20 Nov 2026: “can you complete all decisions waiting and complete it.” See DR-2026-11-20-02. |
