"""
Google Calendar — put confirmed bookings into the salon's Google Calendar.

Endpoints from Google's official docs (checked 2026-09-26):
  POST https://oauth2.googleapis.com/token  (grant_type=refresh_token) → short-lived access token
  POST https://www.googleapis.com/calendar/v3/calendars/{calendarId}/events  (events.insert,
       scope https://www.googleapis.com/auth/calendar.events)
Needs the owner's own Google Cloud OAuth client and a refresh token. Not tested
here (we have no salon Google account). No key? The app's .ics "add to calendar"
file works with no setup at all.
"""
from urllib.parse import quote
from . import Connector, ConnectorError


class GoogleCalendar(Connector):
    id = "google_calendar"
    name = "Google Calendar"
    category = "Bookings"
    cost_type = "free key"
    what_it_does = ("Adds each confirmed booking to the salon's Google Calendar, so the owner sees the day on their phone. "
                    "Without keys, use the free .ics 'add to calendar' button instead.")
    credentials = [
        {"key": "client_id", "label": "OAuth client ID", "secret": False, "required": True,
         "help": "Google Cloud console → APIs & Services → Credentials → OAuth client (enable the Google Calendar API)."},
        {"key": "client_secret", "label": "OAuth client secret", "secret": True, "required": True, "help": "Shown with the client ID."},
        {"key": "refresh_token", "label": "Refresh token", "secret": True, "required": True,
         "help": "Obtained once by the owner signing in to Google with the calendar.events scope."},
        {"key": "calendar_id", "label": "Calendar ID", "secret": False, "required": False,
         "help": "Leave empty for the main calendar ('primary')."},
    ]
    docs_url = "https://developers.google.com/workspace/calendar/api/v3/reference/events/insert"
    pricing = {"text": "Price not checked — Google publishes Calendar API usage limits rather than a price list.",
               "url": "https://developers.google.com/workspace/calendar/api/guides/quota", "checked": None}
    status = "code-ready-needs-key"
    status_note = "events.insert endpoint, body and scopes read in Google's docs on 2026-09-26. Not tested (no Google account for a salon)."
    actions = {"add_event": {"label": "Add a booking to the calendar", "params": [
        {"key": "event", "label": "Event body (built by the app from a booking)", "example": "{…}"}]}}
    shop_features = ["Confirmed bookings appear in the salon's Google Calendar"]

    def _token(self):
        self.need("client_id", "client_secret", "refresh_token")
        d = self.send_json("https://oauth2.googleapis.com/token", form={
            "client_id": self.creds["client_id"], "client_secret": self.creds["client_secret"],
            "refresh_token": self.creds["refresh_token"], "grant_type": "refresh_token"})
        if not d.get("access_token"):
            raise ConnectorError("Google did not return an access token. Check the client and refresh token.", 401)
        return d["access_token"]

    def test_connection(self):
        tok = self._token()
        cal = quote(self.creds.get("calendar_id") or "primary", safe="")
        d = self.get_json(f"https://www.googleapis.com/calendar/v3/calendars/{cal}", headers={"Authorization": "Bearer " + tok})
        return {"ok": True, "message": f"Connected to calendar: {d.get('summary') or cal}"}

    def act_add_event(self, p):
        ev = p.get("event")
        if not isinstance(ev, dict) or not ev.get("start") or not ev.get("end"):
            raise ConnectorError("An event needs a start and an end.")
        tok = self._token()
        cal = quote(self.creds.get("calendar_id") or "primary", safe="")
        d = self.send_json(f"https://www.googleapis.com/calendar/v3/calendars/{cal}/events",
                           headers={"Authorization": "Bearer " + tok}, body=ev)
        return {"id": d.get("id"), "link": d.get("htmlLink"), "status": d.get("status")}
