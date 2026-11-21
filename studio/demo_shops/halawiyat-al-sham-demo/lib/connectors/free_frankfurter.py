"""Frankfurter — currency exchange rates (European Central Bank data). Free, open source, no key."""
import re
from . import Connector, ConnectorError


class Frankfurter(Connector):
    id = "frankfurter"
    name = "Frankfurter exchange rates"
    category = "Money"
    cost_type = "open source"
    what_it_does = ("Today's exchange rates from the European Central Bank, e.g. how many lei (RON) or złoty (PLN) "
                    "for £100 — useful when paying suppliers abroad. Rates are reference rates, not what a bank charges.")
    docs_url = "https://frankfurter.dev/"
    pricing = {"text": "Free, no key.", "url": "https://frankfurter.dev/", "checked": "2026-09-26"}
    status = "working-tested"
    live_tested_on = "2026-09-26"
    actions = {"convert": {"label": "Convert money", "params": [
        {"key": "amount", "label": "Amount", "example": "100"}, {"key": "from", "label": "From", "example": "GBP"},
        {"key": "to", "label": "To (comma list)", "example": "RON,PLN,EUR,TRY"}]}}

    def test_connection(self):
        r = self.act_convert({"amount": 1, "from": "GBP", "to": "EUR"})
        return {"ok": True, "message": f"Working: £1 = €{r['rates'].get('EUR')} (ECB rate for {r['date']})."}

    def act_convert(self, p):
        try:
            amount = float(p.get("amount") or 1)
        except ValueError:
            raise ConnectorError("Amount must be a number.")
        fr = str(p.get("from") or "GBP").upper()
        to = str(p.get("to") or "EUR").upper().replace(" ", "")
        if not re.fullmatch(r"[A-Z]{3}", fr) or not re.fullmatch(r"[A-Z]{3}(,[A-Z]{3})*", to):
            raise ConnectorError("Use 3-letter currency codes like GBP, RON, PLN.")
        d = self.get_json(f"https://api.frankfurter.dev/v1/latest?amount={amount}&base={fr}&symbols={to}")
        return {"amount": d.get("amount"), "base": d.get("base"), "date": d.get("date"), "rates": d.get("rates", {}),
                "source": "European Central Bank reference rates via frankfurter.dev",
                "note": "Some currencies (e.g. AED, SAR, EGP) are not published by the ECB, so they won't appear."}
