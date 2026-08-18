import tempfile
from datetime import datetime, timezone, timedelta
from cos_core.storage.store import DataStore
from cos_core.models.calendar import CalendarEvent
from cos_core.services.meeting_prep import MeetingPrepService

def test_meeting_prep_brief_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        now = datetime.now(timezone.utc)
        evt = CalendarEvent(
            event_id="evt_strategic",
            title="Strategic Investor Alignment",
            start_time=now + timedelta(hours=2),
            end_time=now + timedelta(hours=3),
            attendee_emails=["investor@capital.com"],
            is_external=True,
            is_strategic=True,
        )
        store.save_cached_events([evt])

        svc = MeetingPrepService(store=store)
        res = svc.generate_meeting_prep()

        assert res["eligible_meetings_count"] == 1
        assert "Strategic Investor Alignment" in res["output"]
        assert "investor@capital.com" in res["output"]
        assert "Recommended Talking Points" in res["output"]
