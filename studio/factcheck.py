"""Vendor fact-check results for Solution Components SLC-0001..0008.

Transcribed from decisions/DR-2026-09-25-04 (Draft), checked 2026-09-25 against
the vendors' own public pages. Nothing here is new information: if a value is
not in DR-2026-09-25-04 it is not in this file.

result values:  verified | partly | mismatch | unverified
"""
CHECKED_ON = "2026-09-25"
SOURCE_DR = "DR-2026-09-25-04"

V, P, X, U = "verified", "partly", "mismatch", "unverified"

FACTCHECK = {
    "SLC-0001": {
        "plain_price": "No monthly fee. Standard UK cards 1.5% + 20p per payment.",
        "min_monthly_gbp": 0, "price_basis": "stripe.com/gb/pricing (verified)",
        "fields": [
            ("Countries (SLC: 46+)", V, "Available for businesses in 46 countries.", "stripe.com/use-cases/global-businesses"),
            ("Countries (old INT record: 170+)", X, "Does not match the current business figure (46).", "stripe.com/use-cases/global-businesses"),
            ("Monthly cost: none, transaction fees", V, "No setup fees, no monthly fees; 1.5% + 20p standard UK cards.", "stripe.com/gb/pricing"),
            ("Features: Subscriptions, Invoices, Tax", V, "Listed in Stripe's product menu.", "stripe.com/gb/pricing"),
            ("Deployment: ~5 minutes to enable", U, "Not checked.", ""),
            ("Support level: Standard", U, "Not checked.", ""),
        ]},
    "SLC-0002": {
        "plain_price": "Free plan: £0 a month plus card fees. Plus plan from £29 a month. Loyalty from £25 a month.",
        "min_monthly_gbp": 0, "price_basis": "squareup.com/gb/en/pricing (verified)",
        "fields": [
            ("Countries: 8 (US, UK, CA, AU, IE, FR, ES, JP)", V, "Exactly these 8.", "developer.squareup.com/docs/international-development"),
            ("Monthly cost: none + fees; paid tiers", V, "Free plan £0/month + processing; Plus from £29/month.", "squareup.com/gb/en/pricing"),
            ("Features: POS, online checkout, invoices, loyalty add-on", V, "Invoices and Online store from £0; Loyalty from £25/month.", "squareup.com/gb/en/pricing"),
            ("Low-stock alerts (stock path S1)", P, "Alerts exist; email 90 min after closing. Not confirmed on the owner's own plan.", "squareup.com/help/gb/en/article/8333-create-inventory-alerts"),
        ]},
    "SLC-0003": {
        "plain_price": "Free with a personal Google account (one booking page). Reminder emails and more need a paid Google plan.",
        "min_monthly_gbp": 0, "price_basis": "support.google.com/calendar/answer/16287038 (verified)",
        "fields": [
            ("Monthly cost: free, business tiers via Workspace", V, "Personal accounts get a single booking page; more needs paid plans.", "support.google.com/calendar/answer/16287038"),
            ("Feature: appointment sync", P, "Basic booking page is free.", "support.google.com/calendar/answer/16287038"),
            ("Feature: reminders", P, "Automatic booking reminder emails need an eligible paid plan.", "support.google.com/calendar/answer/16287038"),
            ("Feature: shared calendars", U, "Not checked.", ""),
            ("Countries: global", U, "Not checked.", ""),
        ]},
    "SLC-0004": {
        "plain_price": "Free (iCloud calendar sharing). No booking feature found.",
        "min_monthly_gbp": 0, "price_basis": "support.apple.com iCloud guide (verified)",
        "fields": [
            ("Monthly cost: free", V, "iCloud calendar sharing, no charge shown.", "support.apple.com/guide/icloud/share-a-calendar-mm6b1a9479/icloud"),
            ("Feature: appointment sync", P, "Calendar sharing only; no appointment-booking feature found.", "support.apple.com/guide/icloud/share-a-calendar-mm6b1a9479/icloud"),
            ("Feature: reminders", U, "Not checked.", ""),
            ("Countries: global (iCloud)", U, "Not checked.", ""),
        ]},
    "SLC-0005": {
        "plain_price": "The WhatsApp Business app is free. Automated messages use the paid Platform, charged per message; more message types become chargeable from 1 Oct 2026.",
        "min_monthly_gbp": 0, "price_basis": "app free (partly verified)",
        "fields": [
            ("Monthly cost: free app; paid Platform", P, "App free. Platform is per delivered message, not tiers. From 1 Oct 2026 service messages chargeable after 1,000 free/month/number.", "developers.facebook.com/documentation/business-messaging/whatsapp/pricing"),
            ("Feature: customer chat", V, "App: catalog, greeting/away messages, quick replies.", "business.whatsapp.com"),
            ("Feature: booking confirmations, reminders", P, "Automated confirmations need the paid Platform, not the free app.", "whatsappbusiness.com/products/platform-pricing"),
            ("Countries: global", U, "Not checked.", ""),
        ]},
    "SLC-0006": {
        "plain_price": "From £18 a month (Ignite) up to £70 (Ultimate), excluding VAT. Payroll included from the Grow plan (£39).",
        "min_monthly_gbp": 18, "price_basis": "xero.com/uk/pricing-plans (verified)",
        "fields": [
            ("Monthly cost: paid, tiered", V, "Ignite £18, Grow £39, Comprehensive £55, Ultimate £70 per month excl. VAT.", "xero.com/uk/pricing-plans"),
            ("Features: invoicing, bank reconciliation, tax", V, "Listed; Making Tax Digital supported.", "xero.com/uk/pricing-plans"),
            ("Feature: payroll add-on", X, "In the UK payroll is included from Grow (1 person), not an add-on.", "xero.com/uk/pricing-plans"),
            ("Countries: UK, AU, NZ, US…", P, "UK, NZ, US sites seen; others only from a secondary summary.", ""),
        ]},
    "SLC-0007": {
        "plain_price": "Price not verified — Intuit's site could not be reached on 25 Sept 2026.",
        "min_monthly_gbp": None, "price_basis": "unverified",
        "fields": [
            ("All fields", U, "Intuit pages did not load; search summaries not confirmed, so not recorded.", ""),
        ]},
    "SLC-0008": {
        "plain_price": "Apple charges no fee. You pay your normal card fees to your payment provider.",
        "min_monthly_gbp": 0, "price_basis": "apple.com/uk/apple-pay (verified)",
        "fields": [
            ("Countries: 70+", X, "Apple's list (published 9 Sep 2026) shows 101 countries and regions.", "support.apple.com/en-us/102775"),
            ("Pricing: Apple does not charge merchants", V, "\u201cApple does not charge any fees\u2026 contact your payment provider.\u201d", "apple.com/uk/apple-pay"),
            ("Deployment: SDK / StoreKit integration", U, "Questionable: Apple's merchant page points to your payment provider and does not mention StoreKit.", "apple.com/uk/apple-pay"),
            ("Supported industries, support level", U, "Not checked.", ""),
        ]},
}


def summary(slc_id):
    """Counts of each result type for one component, plus a single overall flag."""
    fc = FACTCHECK.get(slc_id)
    if not fc:
        return {"overall": "unverified", "counts": {}}
    counts = {}
    for _, r, _, _ in fc["fields"]:
        counts[r] = counts.get(r, 0) + 1
    if counts.get(U) == len(fc["fields"]):
        overall = "unverified"
    elif counts.get(X) or counts.get(U) or counts.get(P):
        overall = "partly"
    else:
        overall = "verified"
    return {"overall": overall, "counts": counts}


def as_dict(slc_id):
    fc = FACTCHECK.get(slc_id)
    if not fc:
        return None
    return {
        "checked_on": CHECKED_ON, "source_dr": SOURCE_DR,
        "plain_price": fc["plain_price"], "min_monthly_gbp": fc["min_monthly_gbp"],
        "price_basis": fc["price_basis"],
        "fields": [{"field": f, "result": r, "note": n, "source": s} for f, r, n, s in fc["fields"]],
        **summary(slc_id),
    }
