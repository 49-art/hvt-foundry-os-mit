Document ID: BUT-0005
Title: BusinessType card — Independent high-street retail
Version: 0.1
Status: Draft
Owner: Architecture Office
Reviewed By: pending Raj + Stan Lee
Live instance: none
Related: BUT-0002 deli, BUT-0003 trust-grocery, BUT-0004 specialist
Depends on: DR-10, DR-12, DOC-0008 Draft
ENG-0005: held

Filed: artifacts/governance/BUT-0005_independent_high_street_retail.md
Not an Approved BusinessType. No site.

Howard flags (not closed):
- Overlap with BUT-0004 (specialist) and generic “retail.”
  Card says do not double-card; routing rule is still prose.
- Sector/Market Industry IDs still unminted. “Independent
  goods retail” is a fourth Retail MKT name in prose.
- PRB-0020 family-overlaps PRB-0019 (empty midweek).
  PRB-0021 family-overlaps PRB-0010. Shared vs new IDs
  not reconciled.
- Tier 3 names (Shopify POS, Lightspeed, Toast) are
  unverified SLC candidates. Toast-class “only if food”
  is a filter, not a registration. “Cali” still a nickname.
- DOC-0008 is Draft; listing it on the shelf is a pointer,
  not an Approved session product.

============================================================
WHAT THIS SHOP IS
============================================================
A UK (or similar) independent shop that sells goods from
a room with a till: fashion, household, gifts, convenience,
mixed counter. Broader than the specialist. Broader than
the community grocer. If they are really a deli or a craft
counter, use 0002 / 0004 instead. Do not double-card.

Typical picture
- One till, one back room
- Staff who also unpack boxes
- Instagram they already have
- Quiet Tuesday, mad Saturday
- They have been shown three website builders and hated all
  of them

Classification
  Sector:          Retail
  Market Industry: Independent goods retail
  Business Type:   Independent high-street retail
  Business Model:  Walk-in basket. Optional click-and-collect.

============================================================
PROBLEMS
============================================================
  PRB-0020  Empty midweek / no idea who came in last month
  PRB-0021  Till, sheet, and supplier book disagree
  PRB-0022  Online looks like every other shop
  PRB-0023  Card fees and cashing up eat the evening
  PRB-0007  Run-out of the thing that actually sells

============================================================
SHELF (examples — show all, recommend in order)
============================================================
  Tier 4 already-owned: their till, Instagram, Google listing
  Tier 1: spreadsheet stock list; open-source POS if they
          will self-host; GBP (free)
  Tier 2: ENG-0001 regulars; ENG-0003 payments they have;
          DR-10 alert path; DOC-0008 session
  Tier 3 “Cali” / premium: Square, Shopify POS, Lightspeed,
          Toast-class only if food — list as alternatives,
          never as “the product”
  Booking ENG-0002: OFF unless they do appointments
                    (personal shopping, repairs)

============================================================
GAPS
============================================================
  Unified product list across till + supplier = ENG-0005 held
  Pretty site = Brand Intake + Stan Lee, not a builder pack

============================================================
MINIMUM PATH (session 1)
============================================================
  Keep their till. GBP hours honest. WhatsApp for regulars.
  Sheet of the twenty lines that actually run out.
  Quote optional: Square inventory if they already take
  Square; Shopify only if they already sell online.

STAN LEE TEST
  Logo-swap / Inter-teal / fake lifestyle stock. Reject.

USED BY: none
MATURITY: Draft schema
