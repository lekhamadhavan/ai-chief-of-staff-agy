import tempfile
import time
from cos_core.storage.store import DataStore
from cos_core.services.briefing import BriefingService

def test_morning_briefing_performance_and_content():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        svc = BriefingService(store=store)
        
        start_time = time.time()
        res = svc.generate_morning_briefing()
        duration = time.time() - start_time

        # Target performance objective: < 30s (SC-001)
        assert duration < 5.0  # Runs in under 5 seconds locally
        assert "Ranked Focus Recommendation" in res["output"]
        assert "Today's Schedule" in res["output"]
