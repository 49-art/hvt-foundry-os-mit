Document ID: SES-0002
Title: Ladder script — dry run on BUT-0001 Hair Salon
Version: 0.1
Status: Draft  (run this; do not code this)
Type: template session  (not a live owner until you say so)
Owner: Architecture Office
Reviewed By: pending Raj
BusinessType: BUT-0001
Duration: 20 minutes
People: Raj (stamp) + salesman (can be you) + owner
        Stan Lee only if a surface is proposed
Clock: stop at 20:00 even if incomplete
Depends on: DOC-0008 v0.2 Draft, DR-10 Approved, BUT-0001

Filed: artifacts/governance/SES-0002_BUT-0001_ladder_dry_run.md
Not a live owner session. Not software.

Howard flags:
- DOC-0008 still Draft until APPROVED DOC-0008.
- Running this script as theatre is allowed; it does not
  stamp DOC-0008 by itself.
- Tier 3 names (Fresha, Booksy, Treatwell, Phorest, Salon
  Iris) remain unverified SLC candidates.
- SES-0001 / WSH-0001 stay templates in the pack.

============================================================
BEFORE THE ROOM
============================================================
Print or open:
- this script
- BUT-0001 card (from the pack)
- blank quote sheet (table below)
- Brand Intake questions (rung 7) — ask only if they want
  anything public

Do not open Grok Build.
Do not promise ENG-0005.
Do not start from “what app shall we make.”

============================================================
RUNG 1 — CLASSIFY   (2 min)
============================================================
Say:
  “Tell me what this place is, in your words.”

Tick:
  [ ] Hair salon / barber / mixed
  [ ] One site
  [ ] Country: UK / other
  [ ] How many chairs
  [ ] Who already does the diary
  [ ] Who already takes the money
  [ ] Phone skill: WhatsApp only / apps are fine

Write one line:
  This is a _____ with _____ chairs in _____.
  They already own: _______________________

If they are not a salon, STOP. Get the right card.
Do not stretch BUT-0001 over a clinic or a shop.

============================================================
RUNG 2 — PROBLEMS   (3 min)
============================================================
Say:
  “What hurts this week. Not the dream. This week.”

Map their sentence to a box. Do not correct their English.

  [ ] Missed appointments / no-shows     (booking)
  [ ] Empty slots they cannot fill       (booking + customers)
  [ ] No idea who the regulars are       (customers)
  [ ] Colour / foil / product runs out   (stock — DR-10 path)
  [ ] Slow checkout                      (commerce)
  [ ] Reviews sitting there              (GBP + WhatsApp)
  [ ] Other: _________________________   (Wish, not a feature)

Owner words, copied exactly:
  “______________________________________________”

============================================================
RUNG 3 — SHELF   (5 min)
============================================================
Show ALL of this. Recommend with a star. Do not hide
premium tools. Do not pretend free tools are always enough.

TIER 4  they already own  (always first)
  [ ] Paper diary / phone calendar
  [ ] WhatsApp
  [ ] Card machine / Stripe / Square
  [ ] Instagram
  [ ] Google listing
  [ ] Spreadsheet
  [ ] Something else: ________

TIER 1  free / open
  [ ] Google Calendar *
  [ ] Google Business Profile *
  [ ] WhatsApp Business app *
  [ ] Sheet of product lines (colour, foil, shampoo) *
  [ ] Apple Calendar if that is their phone

TIER 2  Foundry
  [ ] ENG-0001 Customer records
  [ ] ENG-0002 Booking + reminders
  [ ] ENG-0003 Payments on THEIR account
  [ ] DR-10 stock alert path (Square or sheet+phone) *
  [ ] DR-10 review path (GBP reply + WhatsApp) *
  [ ] This ladder (DOC-0008)

TIER 3  partner / premium  (on the shelf, not the identity)
  [ ] Square Appointments / Payments
  [ ] Fresha / Booksy / Treatwell-class booking
  [ ] Stripe
  [ ] Phorest / Salon Iris-class
  [ ] Mailchimp-class mail
  Say: “These exist. We only pick one if the free path
        cannot do the job you named.”

Search allowed:
  Salesman may add one extra tool they thought of.
  Write it on the shelf. Mark tier. Do not install it yet.

Added mid-session:
  name: __________  tier: _  why: __________

============================================================
RUNG 4 — MATCH   (3 min)
============================================================
For each ticked problem:

  Problem          Path this session           Status
  ---------------- --------------------------- ---------
  no-shows         ENG-0002 or their diary
                   + WhatsApp reminder         covered / quote
  regulars         ENG-0001 or phone list      covered / quote
  checkout         ENG-0003 keep their card    covered / quote
  stock            Square alerts OR sheet
                   + phone  (DR-10)            covered / quote
  reviews          GBP + WhatsApp  (DR-10)     covered / quote
  other            Wish / Search / out         GAP

Forbidden this session:
  “We’ll build you a stock app.”
  “We’ll build you a review product.”
  “We’ll move your card takings onto our account.”

============================================================
RUNG 5 — QUOTE   (4 min)
============================================================
One line per thing that is not already theirs and free.

id     name                  tier  owned  take        reversible
-----  --------------------  ----  -----  ----------  ----------
Q1     __________________     _     y/n    zero/mark/
                                           outright    y/n
Q2     __________________     _     y/n    ____        y/n
Q3     __________________     _     y/n    ____        y/n

Rates: Raj fills later. Today only pick the TYPE of take.
Zero on Tier 4 and on GBP / WhatsApp app.
Do not invent a percentage in the room.

Read back:
  “You keep ____. You add ____. You pay ____ to them,
   and ____ to us if anything. If you walk away you still
   have ____.”

============================================================
RUNG 6 — GAPS   (2 min)
============================================================
Write every empty box. Do not tidy them.

  GAP: ________________________________
  Action: Engine Search / out of scope / later session
  Wish in their words: ________________

If the gap is “stock from two places in one list”
that is ENG-0005 HELD. Say:
  “Logged. Not built today.”
Do not apologise by promising code.

============================================================
RUNG 7 — BRAND   (only if they want anything public)
============================================================
  Photo of the real shop
  Languages at the desk
  Three words they would never put in Comic Sans
  What a Canva salon page would get wrong

If no public surface this session: tick SKIP.
Stan Lee is not required for a diary + WhatsApp path.

============================================================
RUNG 8 — DEPLOY THIS WEEK   (minimum path)
============================================================
Default salon week, unless they already have better:

  Mon  Hours honest on Google
  Mon  WhatsApp Business app on the owner’s phone
  Tue  Reminder text the day before (from their diary)
  Tue  Sheet of colour / foil / shampoo + a number
       that means “reorder”
  Wed  Card machine unchanged
  Fri  Reply to any waiting Google review in their voice

No new website in week one.
No Foundry-owned customer list.

============================================================
SESSION RECORD  (fill before you stand up)
============================================================
Date:
Owner name / shop:
This is a: BUT-0001 salon / STOP wrong type
Already own:
Chose:
Quoted:
Gaps:
Wishes:
Public surface this week: yes / no
Stan Lee needed: yes / no
Twenty minutes kept: yes / no

Status of this SES: Draft dry-run until a real owner sits.

============================================================
AFTER THE ROOM
============================================================
File this page. Do not open a builder.
If the dry run felt stupid, fix the SCRIPT, not the stack.
If a tool was missing from the shelf, add it to the shelf
and run again. That is how the ladder becomes routine.
