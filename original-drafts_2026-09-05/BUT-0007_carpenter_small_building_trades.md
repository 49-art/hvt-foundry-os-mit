Document ID: BUT-0007
Title: BusinessType card — Carpenter / small building trades
Version: 0.1
Status: Draft
Owner: Architecture Office
Reviewed By: pending Raj + Stan Lee
Live instance: none
Depends on: DR-10, DR-12, Art. VIII
ENG-0005: held

Filed: artifacts/governance/BUT-0007_carpenter_small_building_trades.md
Not an Approved BusinessType. No site.

Howard flags (not closed):
- Sector “Trades” is not SEC-0001 Services and not Retail.
  New Sector in prose. No SEC-0003 / MKT ID minted.
- “procedure: quote → accept → deposit → schedule” is a
  Workflow candidate (WKF-), not a new Engine on this card.
- Tier 3 names (ServiceTitan, Jobber, Buildertrend, Houzz Pro,
  Checkatrade, MyBuilder) unverified. Lead doors stay options.
- CIS / multi-crew ERP named as gap, correctly out of session 1.
- Photos on the phone are Customer Assets (Art. VIII). Drive
  folder per job is a procedure, not Foundry owning the photos.
- Small retail of offcuts may dual-type toward BUT-0004/0005.
  Not decided.

============================================================
WHAT THIS TRADE IS
============================================================
A carpenter, joiner, small builder, kitchen fitter,
or similar: van, phone, tape measure, one or two mates.
Jobs live in WhatsApp. Quotes live in a notebook.
The website they were sold does not get them work.

Typical picture
- Job is a place, not a till
- Deposit then balance
- Materials from a merchant account
- Rain and “the other trade didn’t show” destroy the diary
- Photos of the job ARE the brand

Classification
  Sector:          Trades
  Market Industry: Building & joinery
  Business Type:   Carpenter / small building trade
  Business Model:  Quoted job + deposit + schedule.
                   Some day-rate. Some small retail of
                   offcuts / furniture if they have a shop.

============================================================
PROBLEMS
============================================================
  PRB-0029  Quotes take a night and then go cold
  PRB-0030  Diary vs materials vs who is on site
  PRB-0031  Deposit taken, extras argued later
  PRB-0032  Photos trapped on the phone
  PRB-0033  No idea which jobs made money

============================================================
SHELF (show all)
============================================================
  Tier 4: WhatsApp, merchant account, van insurer,
          existing bank / SumUp / Stripe
  Tier 1: Google Calendar; Google Drive for job photos;
          spreadsheet job list; open-source job-ticket
          tools if they will actually open them
  Tier 2: ENG-0001 customers / sites
          ENG-0002 slots for survey / fit days
          ENG-0003 deposits and balances
          procedure: quote → accept → deposit → schedule
  Tier 3: ServiceTitan, Jobber, Buildertrend, Houzz Pro,
          Checkatrade / MyBuilder as lead doors —
          on the shelf as options, not as “join this or
          you don’t exist”
  Stock of timber / ironmongery: DR-10 path (merchant
          account + sheet). ENG-0005 held.

============================================================
GAPS
============================================================
  Full site-costing / CIS / multi-crew ERP = not session 1
  Lead-marketplace lock-in = warn, don’t hide

============================================================
MINIMUM PATH
============================================================
  One job record: who, where, quote, deposit, dates.
  Calendar they already have.
  Payments they already have.
  Drive folder per job for photos.
  GBP with real photos of THEIR work.

STAN LEE TEST
  No stock decking at sunset. Their last job, their
  hands, their van signwriting. Else reject.

USED BY: none
MATURITY: Draft schema
