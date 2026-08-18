import tempfile
from datetime import datetime, timezone
import pytest

from cos_core.storage.store import DataStore
from cos_core.models.calendar import CalendarEvent
from cos_core.services.meeting_prep import MeetingPrepService
from cos_core.connectors.base import CalendarEventDTO

def test_meeting_eligibility_filter():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        svc = MeetingPrepService(store=store)

        external_evt = CalendarEventDTO(
            event_id="e1",
            title="Partner Sync",
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            is_external=True,
        )
        assert svc.is_eligible_meeting(external_evt) is True

        internal_sync = CalendarEventDTO(
            event_id="e2",
            title="Internal Standup",
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            is_external=False,
            is_strategic=False,
        )
        assert svc.is_eligible_meeting(internal_sync) is False
