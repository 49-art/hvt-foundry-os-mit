# DR-2026-09-26-09 — Decision Record — The Hair Salon / Barber card as a ready-made app (Studio v0.3)

Document ID: DR-2026-09-26-09  
Title: Decision Record — Hair Salon / Barber card: a 4-star app template with switchable modules (Studio v0.3)  
Version: 0.1  
Status: Draft — written 18 Oct 2026, awaiting the founder's look and Chief Architect review (role vacant)  
Owner: Architecture Office  
Reviewed By: pending — not reviewed  
Drafted By: AI executor (Grok Bot) on instruction from Travis Lee Swift, 18 Oct 2026  
Dependencies: DR-2026-09-26-08; DR-2026-10-18-01; DOC-0005; HVT-0001 Art. IV, V, VIII; HVT-0002 §4.2; the Hair Salon & Barber theory test of 26 Sept 2026  

Note on the number: the ID follows on from DR-2026-09-26-08 because the card was planned on 26 Sept 2026 (the theory test). The record itself was written on 18 Oct 2026. It is **not** covered by the founder approval of 18 Oct 2026 (DR-2026-10-18-01 §6), because Travis had not seen this work yet.

---

## 1. Decision (plain English)

A BusinessType card (starting with BUT-0001 Hair Salon, with barbers as a variant of it) is now a **complete app template**:

1. **A strong 4-star base.** Out of the box the shop gets a good-looking phone app: services and prices, stylists, opening hours, booking, call / WhatsApp / directions buttons, several languages (including right-to-left), and an owner admin page with a password.
2. **Switchable modules.** The owner (or Travis, sitting with them) switches extra parts on or off: walk-in queue and TV board, deposits, reminders, reviews, patch tests, loyalty, packages, retail stock, Google Calendar and so on.
3. **Every module shows an honest status:** *working-tested* (runs here, tests pass), *code-ready-needs-key* (written from the vendor's own docs but never run with a real key), or *needs-server* (needs the shop's app running on a computer that stays on).
4. **The shop owns the result** (Art. VIII). It exports as a zip with no keys, passwords or private client data in it.

## 2. What was built

- **Booking engine v3** (`studio/engines/booking.py`). A booking can be: held, requested, confirmed, done, cancelled, no-show, declined, expired or refund due.
  - **Held** means the time is kept for the customer while they pay a deposit (10 minutes by default). If the hold runs out, the time is freed.
  - A stylist can never be double-booked; if two people try for the same time, the second gets "Sorry, that time has just gone" plus the next free times.
- **The six fixes the theory test asked for** (all now have tests):
  1. Clean-up time after the last appointment may run past closing time (the appointment itself may not).
  2. A "flexible" lunch break doesn't block long services (3 hours or more), so a balayage can still be booked.
  3. Services with waiting time in the middle (for example colour developing) only block the stylist while they are actually working, so another client can fit in the gap.
  4. A deposit that arrives late is checked again. If the time is still free, the booking is confirmed. If not, it's marked **refund due** and the owner gets an alert. The same payment message arriving twice is only counted once.
  5. The walk-in queue calls the first person who can actually be served by that barber, not just whoever is at the top.
  6. Queue waiting times are worked out chair by chair, and include the booked appointments, based on how long each person's service takes.
- **Other rules from the theory test:** a patch test at least 48 hours before colour; a late-cancel flag; a no-show after 15 minutes' grace; a deposit asked for after one no-show; reminder timing; shop times always in UK time (summer and winter time handled).
- **Payments:** deposit links and payment checks for Stripe, Square and SumUp, written from each company's own docs (checked 18 Oct 2026). The payment message is checked for a valid signature, and for SumUp the status is always re-checked with SumUp rather than trusted. **None of these has been run with real keys.** With no payment company connected, bookings that need a deposit come in as requests, and the owner takes the deposit themselves.
- **No-signal handling:** if the customer's phone loses signal, the app says clearly "Not sent yet — you are NOT booked", keeps the request on the phone, and sends it when the signal comes back. The queue page shows "No signal — this is the last answer we had" and the time it last checked.
- **WhatsApp fallback (no server):** a static copy of the app that can sit on free hosting. Booking becomes "Send your request by WhatsApp", clearly labelled a request, not a booking. Modules that need the server (queue, packages, retail stock, admin) are left out.
- **Two demo shops,** both labelled "(demo)" everywhere, with invented content: a luxury salon and an urban barber with a walk-in queue.

## 3. Action taken in the Studio

Three new actions were added to the Studio action map, for the **Architecture Office only**, through the same labelled `extra_authority` route as DR-2026-09-25-07 and DR-2026-09-26-08:

- `preview_card_template`
- `build_card_app`
- `export_card_app`

Each is tagged "(DR-2026-09-26-09, Draft)". **The CEO Agent (AGT-0001) is refused all three; this is tested.** `kernel/foundry_kernel.py` only had its authority wording updated by DR-2026-10-18-01; nothing here changed it.

## 4. Tests

- 32 tests port every case of the 26 Sept theory test (B1–B21, Q1–Q8, plus extra checks). The theory paper said "28 cases"; its own results file lists 29, and all 29 are covered. A check confirms that against the original results file when it is on the computer.
- 15 more tests cover the card v3 parts (payments, refund alert, slot-taken answer, queue, export zip, demo clock, checks on the owner's settings, barcode lookup).
- Whole project: **189 tests, all pass** (18 Oct 2026 / early 19 Oct 2026 UK time). Before this work there were 142.

## 5. What is honestly not done

- Payments, text messages (Twilio) and Google Calendar have **never run with real keys**.
- The new wording in the app is in English only; the other languages fall back to English for those lines.
- Chairs are not counted separately from staff (one barber = one chair).
- Hosting: see `studio/HOSTING_OPTIONS.md`. No shop has a server yet; who hosts and who pays is Travis's decision.
- Owner-facing design still needs Stan Lee's design review (DR-2026-09-04-12), and QA is unstaffed.

## 6. Authority

Drafted under HVT-0001 Art. IV (AI work stays pending human review). Nothing in this record is approved. One line from Travis approves it as founder; the Chief Architect review stays owed while that role is vacant.
