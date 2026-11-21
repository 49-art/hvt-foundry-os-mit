"""
Local business engines used by card app templates (standard library only).

Each engine keeps its own JSON file in the shop app's data/private/ folder, so
nothing leaves the shop's computer unless the owner switches on a connector.
They are small on purpose: a shop owner (or whoever looks after the app) should
be able to read them.

    booking    – services, stylists, opening hours, slots, no double booking
    walkin     – walk-in queue with a live "you're next" board
    loyalty    – stamp cards
    vouchers   – gift vouchers with balances
    packages   – memberships / prepaid packages
    retail     – product stock and sales
    clients    – client notes, allergies and patch tests (consent required)
    rota       – staff shifts, takings and commission
    referrals  – referral codes
    analytics  – local counts only (no cookies, no personal data)
    messages   – reminder / review-request text and WhatsApp links
    calendar   – .ics files and the Google Calendar event body
    suppliers  – trade-aware supplier search on top of live search
"""
