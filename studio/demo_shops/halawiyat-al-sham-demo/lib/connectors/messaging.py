"""Messages: WhatsApp (click-to-chat, free), WhatsApp Business Cloud API, Twilio SMS."""
import re
import urllib.parse
from . import Connector, ConnectorError, basic


def _e164(n: str) -> str:
    n = re.sub(r"[^\d+]", "", n or "")
    if n.startswith("00"):
        n = "+" + n[2:]
    if n.startswith("0"):
        n = "+44" + n[1:]
    if not re.fullmatch(r"\+\d{8,15}", n):
        raise ConnectorError("Phone number must be a UK number (07…) or international (+…).")
    return n


class WhatsAppClickToChat(Connector):
    id = "whatsapp_link"
    name = "WhatsApp order button (click-to-chat)"
    category = "Messages"
    cost_type = "free"
    what_it_does = "Customers tap a button and WhatsApp opens with their order already typed to the shop's number. No account or key needed."
    credentials = [{"key": "phone", "label": "Shop WhatsApp number", "secret": False, "required": True}]
    docs_url = "https://faq.whatsapp.com/5913398998672934"
    pricing = {"text": "Free (uses the normal WhatsApp or WhatsApp Business app).", "url": "https://business.whatsapp.com/", "checked": "2026-09-25"}
    status = "working-tested"
    status_note = "Builds https://wa.me/<number>?text=… links; tested by our automated tests. Opening the link needs WhatsApp on the phone."
    live_tested_on = "2026-09-26"
    actions = {"link": {"label": "Make an order link", "params": [{"key": "text", "label": "Message", "example": "Hello, I'd like to order…"}]}}
    shop_features = ["WhatsApp order button with the basket typed in"]

    def test_connection(self):
        self.need("phone")
        return {"ok": True, "message": "Ready: " + self.act_link({"text": "Hello"})["url"]}

    def act_link(self, p):
        self.need("phone")
        return {"url": f"https://wa.me/{_e164(self.creds['phone']).lstrip('+')}?text=" + urllib.parse.quote(p.get("text") or "")}


class WhatsAppCloud(Connector):
    id = "whatsapp_cloud"
    name = "WhatsApp Business Cloud API"
    category = "Messages"
    cost_type = "paid"
    what_it_does = "Sends WhatsApp messages from the shop's business number automatically (e.g. 'your order is ready'). Needs a Meta business setup."
    credentials = [{"key": "access_token", "label": "Access token", "secret": True, "required": True,
                    "help": "developers.facebook.com → your app → WhatsApp → API setup."},
                   {"key": "phone_number_id", "label": "Phone number ID", "secret": False, "required": True}]
    docs_url = "https://developers.facebook.com/docs/whatsapp/cloud-api/"
    pricing = {"text": "Charged per message by Meta; more message types become chargeable from 1 Oct 2026 (from the 25 Sept 2026 fact-check).",
               "url": "https://business.whatsapp.com/products/platform-pricing", "checked": "2026-09-25"}
    status = "unverified"
    status_note = ("Meta's developer docs could not be read from our box on 2026-09-26 (they returned an error), so the endpoint "
                   "(graph.facebook.com/<version>/<phone-number-id>/messages) is from our knowledge, not re-checked today. "
                   "Also: outside a 24-hour customer chat, WhatsApp only allows pre-approved template messages.")
    actions = {"send_text": {"label": "Send a text (only inside a 24h customer chat)", "params": [
        {"key": "to", "label": "Customer number", "example": "07700900123"}, {"key": "text", "label": "Message", "example": "Your order is ready"}]}}
    GRAPH = "https://graph.facebook.com/v21.0"

    def _h(self):
        self.need("access_token", "phone_number_id")
        return {"Authorization": "Bearer " + self.creds["access_token"]}

    def test_connection(self):
        d = self.get_json(f"{self.GRAPH}/{self.creds.get('phone_number_id', '')}", headers=self._h())
        return {"ok": True, "message": f"Working: number {d.get('display_phone_number', '?')} ({d.get('verified_name', '')})."}

    def act_send_text(self, p):
        h = self._h()
        d = self.send_json(f"{self.GRAPH}/{self.creds['phone_number_id']}/messages", headers=h, body={
            "messaging_product": "whatsapp", "to": _e164(p.get("to")).lstrip("+"), "type": "text",
            "text": {"body": (p.get("text") or "")[:4096]}})
        return {"message_ids": [m.get("id") for m in d.get("messages", [])]}


class TwilioSMS(Connector):
    id = "twilio_sms"
    name = "Twilio SMS"
    category = "Messages"
    cost_type = "paid"
    what_it_does = "Sends text messages (e.g. 'your order is ready', low-stock alerts to the owner)."
    credentials = [{"key": "account_sid", "label": "Account SID (AC…)", "secret": False, "required": True},
                   {"key": "auth_token", "label": "Auth token", "secret": True, "required": True, "help": "console.twilio.com → Account info."},
                   {"key": "from_number", "label": "Twilio number to send from (+44…)", "secret": False, "required": True}]
    docs_url = "https://www.twilio.com/docs/messaging/api/message-resource"
    pricing = {"text": "Price not checked today — see Twilio's UK SMS pricing page.", "url": "https://www.twilio.com/en-us/sms/pricing/gb", "checked": None}
    status = "code-ready-needs-key"
    status_note = "POST /2010-04-01/Accounts/{sid}/Messages.json confirmed in Twilio's docs on 2026-09-26. Not tested here (no account)."
    actions = {"send": {"label": "Send an SMS", "params": [{"key": "to", "label": "To", "example": "07700900123"}, {"key": "text", "label": "Message", "example": "Your order is ready"}]}}

    def _h(self):
        self.need("account_sid", "auth_token")
        return {"Authorization": basic(self.creds["account_sid"], self.creds["auth_token"])}

    def test_connection(self):
        d = self.get_json(f"https://api.twilio.com/2010-04-01/Accounts/{self.creds.get('account_sid', '')}.json", headers=self._h())
        return {"ok": True, "message": f"Working: Twilio account '{d.get('friendly_name', '?')}' ({d.get('status')})."}

    def act_send(self, p):
        h = self._h()
        self.need("from_number")
        d = self.send_json(f"https://api.twilio.com/2010-04-01/Accounts/{self.creds['account_sid']}/Messages.json", headers=h,
                           form={"To": _e164(p.get("to")), "From": _e164(self.creds["from_number"]), "Body": (p.get("text") or "")[:1600]})
        return {"sid": d.get("sid"), "status": d.get("status")}
