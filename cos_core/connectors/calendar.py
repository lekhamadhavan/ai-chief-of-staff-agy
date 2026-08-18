from datetime import datetime, timezone
from typing import List, Optional
import json
import urllib.request
import urllib.parse

from cos_core.connectors.base import (
    IGoogleCalendarConnector,
    CalendarEventDTO,
)
from cos_core.storage.store import DataStore
from cos_core.connectors.google_auth import get_valid_access_token


class GoogleCalendarConnectorAdapter(IGoogleCalendarConnector):
    """
    Google Calendar Connector implementation (strictly Read-Only for V1).
    Fetches live Google Calendar events via OAuth tokens, falling back
    gracefully to DataStore cached records when offline.
    """

    def __init__(self, store: Optional[DataStore] = None, live_mode: bool = False):
        self.store = store or DataStore()
        self.live_mode = live_mode

    def fetch_events(self, start_date: datetime, end_date: datetime) -> List[CalendarEventDTO]:
        token = get_valid_access_token()
        if token:
            try:
                live_events = self._fetch_live_events(token, start_date, end_date)
                if live_events is not None:
                    return live_events
            except Exception as e:
                print(f"[CalendarConnector] Live fetch notice: {e}. Falling back to cached data.")

        # Fallback to cached store
        cached = self.store.load_cached_events()
        events = []
        for item in cached:
            evt_start = item.start_time.astimezone(timezone.utc) if item.start_time.tzinfo else item.start_time.replace(tzinfo=timezone.utc)
            s_date = start_date.astimezone(timezone.utc) if start_date.tzinfo else start_date.replace(tzinfo=timezone.utc)
            e_date = end_date.astimezone(timezone.utc) if end_date.tzinfo else end_date.replace(tzinfo=timezone.utc)

            if s_date <= evt_start <= e_date:
                events.append(
                    CalendarEventDTO(
                        event_id=item.event_id,
                        title=item.title,
                        description=item.description,
                        start_time=item.start_time,
                        end_time=item.end_time,
                        attendees=item.attendee_emails,
                        location=item.location,
                        is_external=item.is_external,
                        is_strategic=item.is_strategic,
                    )
                )
        return events

    def _fetch_live_events(self, token: str, start_date: datetime, end_date: datetime) -> List[CalendarEventDTO]:
        s_iso = start_date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        e_iso = end_date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        time_min = urllib.parse.quote(s_iso)
        time_max = urllib.parse.quote(e_iso)

        url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin={time_min}&timeMax={time_max}&singleEvents=true&orderBy=startTime"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})

        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        items = data.get("items", [])
        events = []
        for item in items:
            start_info = item.get("start", {})
            end_info = item.get("end", {})

            start_raw = start_info.get("dateTime", start_info.get("date"))
            end_raw = end_info.get("dateTime", end_info.get("date"))

            try:
                st = datetime.fromisoformat(start_raw.replace("Z", "+00:00"))
            except Exception:
                st = start_date

            try:
                et = datetime.fromisoformat(end_raw.replace("Z", "+00:00"))
            except Exception:
                et = end_date

            attendees = [a.get("email") for a in item.get("attendees", []) if a.get("email")]

            events.append(
                CalendarEventDTO(
                    event_id=item.get("id", "evt_unknown"),
                    title=item.get("summary", "Untitled Event"),
                    description=item.get("description", ""),
                    start_time=st,
                    end_time=et,
                    attendees=attendees,
                    location=item.get("location", ""),
                    is_external=len(attendees) > 1,
                    is_strategic=False,
                )
            )

        return events

    def get_event_details(self, event_id: str) -> Optional[CalendarEventDTO]:
        cached = self.store.load_cached_events()
        matching = [item for item in cached if item.event_id == event_id]
        if not matching:
            return None
        item = matching[0]
        return CalendarEventDTO(
            event_id=item.event_id,
            title=item.title,
            description=item.description,
            start_time=item.start_time,
            end_time=item.end_time,
            attendees=item.attendee_emails,
            location=item.location,
            is_external=item.is_external,
            is_strategic=item.is_strategic,
        )

    def check_availability(self, start_time: datetime, end_time: datetime) -> bool:
        events = self.fetch_events(
            start_time.replace(hour=0, minute=0, second=0),
            end_time.replace(hour=23, minute=59, second=59),
        )
        s_time = start_time.astimezone(timezone.utc) if start_time.tzinfo else start_time.replace(tzinfo=timezone.utc)
        e_time = end_time.astimezone(timezone.utc) if end_time.tzinfo else end_time.replace(tzinfo=timezone.utc)

        for evt in events:
            evt_start = evt.start_time.astimezone(timezone.utc) if evt.start_time.tzinfo else evt.start_time.replace(tzinfo=timezone.utc)
            evt_end = evt.end_time.astimezone(timezone.utc) if evt.end_time.tzinfo else evt.end_time.replace(tzinfo=timezone.utc)
            if (s_time < evt_end) and (e_time > evt_start):
                return False
        return True
