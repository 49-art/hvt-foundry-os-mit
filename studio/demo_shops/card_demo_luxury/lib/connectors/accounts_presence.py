"""Accounting (Xero) and local presence (Google Business Profile)."""
from . import Connector, ConnectorError, basic


class Xero(Connector):
    id = "xero"
    name = "Xero (accounting)"
    category = "Accounting"
    cost_type = "paid"
    what_it_does = "Connects to the owner's Xero books, e.g. to check the organisation and list unpaid bills to suppliers."
    credentials = [{"key": "client_id", "label": "Custom connection client ID", "secret": False, "required": True},
                   {"key": "client_secret", "label": "Client secret", "secret": True, "required": True,
                    "help": "developer.xero.com → My Apps → New app → Custom connection (a paid Xero add-on for the organisation)."}]
    docs_url = "https://developer.xero.com/documentation/guides/oauth2/custom-connections/"
    pricing = {"text": "Xero plans from £18 a month excl. VAT (from the 25 Sept 2026 fact-check). Custom connections cost extra — not checked today.",
               "url": "https://www.xero.com/uk/pricing-plans/", "checked": "2026-09-25"}
    status = "unverified"
    status_note = ("Xero's developer pages load their text with JavaScript, so we could not read them from our box on 2026-09-26. "
                   "The token address and api.xro/2.0 endpoints are from our knowledge. Treat as a starting point.")
    actions = {"organisation": {"label": "Show organisation", "params": []},
               "unpaid_bills": {"label": "Unpaid supplier bills", "params": []}}

    def _token(self):
        self.need("client_id", "client_secret")
        d = self.send_json("https://identity.xero.com/connect/token",
                           headers={"Authorization": basic(self.creds["client_id"], self.creds["client_secret"])},
                           form={"grant_type": "client_credentials",
                                 "scope": "accounting.settings.read accounting.transactions.read"})
        return {"Authorization": "Bearer " + d["access_token"]}

    def test_connection(self):
        o = self.act_organisation({})
        return {"ok": True, "message": f"Working: Xero organisation '{o.get('name')}'."}

    def act_organisation(self, p):
        d = self.get_json("https://api.xero.com/api.xro/2.0/Organisation", headers=self._token())
        o = (d.get("Organisations") or [{}])[0]
        return {"name": o.get("Name"), "country": o.get("CountryCode"), "currency": o.get("BaseCurrency")}

    def act_unpaid_bills(self, p):
        d = self.get_json('https://api.xero.com/api.xro/2.0/Invoices?where=Type%3D%3D%22ACCPAY%22%26%26Status%3D%3D%22AUTHORISED%22',
                          headers=self._token())
        return {"items": [{"supplier": (i.get("Contact") or {}).get("Name"), "due": i.get("DueDateString"),
                           "amount_due": i.get("AmountDue"), "currency": i.get("CurrencyCode")} for i in d.get("Invoices", [])]}


class GoogleBusinessProfile(Connector):
    id = "google_business_profile"
    name = "Google Business Profile"
    category = "Local presence"
    cost_type = "free key"
    what_it_does = "Reads the shop's Google Maps listing (name, hours) so the shop app and Google say the same thing."
    credentials = [{"key": "access_token", "label": "OAuth access token", "secret": True, "required": True,
                    "help": "Needs a Google Cloud project with Business Profile API access approved by Google, then an OAuth sign-in by the owner."}]
    docs_url = "https://developers.google.com/my-business/reference/businessinformation/rest"
    pricing = {"text": "The API has no charge listed, but Google must approve access first.", "url": "https://developers.google.com/my-business/content/prereqs", "checked": None}
    status = "unverified"
    status_note = ("Business Information API host confirmed in Google's reference on 2026-09-26, but access needs Google's approval "
                   "and an OAuth sign-in we can't do here. Still open from the 25 Sept fact-check.")
    actions = {"accounts": {"label": "List accounts", "params": []}}

    def _h(self):
        self.need("access_token")
        return {"Authorization": "Bearer " + self.creds["access_token"]}

    def test_connection(self):
        d = self.act_accounts({})
        return {"ok": True, "message": f"Working: {len(d['items'])} account(s)."}

    def act_accounts(self, p):
        d = self.get_json("https://mybusinessaccountmanagement.googleapis.com/v1/accounts", headers=self._h())
        return {"items": [{"name": a.get("accountName"), "id": a.get("name")} for a in d.get("accounts", [])]}
