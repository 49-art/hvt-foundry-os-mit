"""Companies House Public Data API — free key. Check a supplier is a real registered UK company."""
import urllib.parse
from . import Connector, ConnectorError, basic


class CompaniesHouse(Connector):
    id = "companies_house"
    name = "Companies House"
    category = "Checks"
    cost_type = "free key"
    what_it_does = "Look up any UK company by name or number: status (active/dissolved), address, date set up. Good for checking a new supplier."
    credentials = [{"key": "api_key", "label": "Companies House REST API key", "secret": True, "required": True,
                    "help": "Free: developer.company-information.service.gov.uk → register → create an application → REST key."}]
    docs_url = "https://developer-specs.company-information.service.gov.uk/companies-house-public-data-api/reference/search/search-companies"
    pricing = {"text": "Free (a free account and key are needed).", "url": "https://developer.company-information.service.gov.uk/", "checked": "2026-09-26"}
    status = "code-ready-needs-key"
    status_note = "search/companies endpoint confirmed in the official spec on 2026-09-26. Without a key the live API answered 401, as expected."
    actions = {"search": {"label": "Search companies", "params": [{"key": "q", "label": "Company name", "example": "Polish food wholesale"}]},
               "company": {"label": "Company by number", "params": [{"key": "number", "label": "Company number", "example": "00000006"}]}}
    BASE = "https://api.company-information.service.gov.uk"

    def _h(self):
        self.need("api_key")
        return {"Authorization": basic(self.creds["api_key"], "")}

    def test_connection(self):
        d = self.get_json(self.BASE + "/search/companies?q=tesco&items_per_page=1", headers=self._h())
        return {"ok": True, "message": f"Working: {d.get('total_results', 0)} companies match 'tesco'."}

    def act_search(self, p):
        if not p.get("q"):
            raise ConnectorError("Type a company name.")
        d = self.get_json(self.BASE + "/search/companies?" + urllib.parse.urlencode({"q": p["q"], "items_per_page": 10}), headers=self._h())
        return {"items": [{"title": i.get("title"), "number": i.get("company_number"), "status": i.get("company_status"),
                           "address": i.get("address_snippet"), "created": i.get("date_of_creation"),
                           "url": f"https://find-and-update.company-information.service.gov.uk/company/{i.get('company_number')}"}
                          for i in d.get("items", [])]}

    def act_company(self, p):
        n = str(p.get("number") or "").strip().upper()
        if not n:
            raise ConnectorError("Type a company number.")
        d = self.get_json(self.BASE + "/company/" + urllib.parse.quote(n), headers=self._h())
        return {"name": d.get("company_name"), "status": d.get("company_status"), "created": d.get("date_of_creation"),
                "address": d.get("registered_office_address"), "sic_codes": d.get("sic_codes")}
