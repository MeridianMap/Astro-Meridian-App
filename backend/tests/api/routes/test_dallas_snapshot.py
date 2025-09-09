"""
Single test file to capture and print the full Enhanced Natal JSON
for the provided Dallas chart (1987-07-15 09:01 America/Chicago; 14:01Z).
This also writes a snapshot under top-level reference/snapshots.
"""

import json
import os
import sys
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

# Ensure backend is on sys.path when running directly
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app  # noqa: E402


class TestDallasSnapshot:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_capture_full_output_for_verification(self, client):
        # Chart: Wed, 15 July 1987, Dallas, TX (US), 96w48, 32n47, 9:01 a.m. local, UTC 14:01
        request_payload = {
            "subject": {
                "name": "Dallas 1987-07-15 09:01",
                "datetime": {"iso_string": "1987-07-15T09:01:00"},
                "latitude": {"decimal": 32.7833333333},
                "longitude": {"decimal": -96.8},
                "timezone": {"name": "America/Chicago"},
            },
            "configuration": {
                "house_system": "P",
                "include_asteroids": True,
                "include_nodes": True,
                "include_lilith": True,
            },
            "include_aspects": True,
            "aspect_orb_preset": "traditional",
            "metadata_level": "audit",
            "include_arabic_parts": True,
            "include_all_traditional_parts": True,
            "include_dignities": True,
        }

        response = client.post("/ephemeris/v2/natal-enhanced", json=request_payload)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True

        # Print full JSON for manual review
        print("\nFULL ENHANCED NATAL JSON (Dallas 1987-07-15 09:01):\n")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        # Write snapshot under top-level reference/snapshots
        repo_root = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "..", ".."))
        snapshots_dir = os.path.join(repo_root, "reference", "snapshots")
        os.makedirs(snapshots_dir, exist_ok=True)

        event_stamp = "19870715T140100Z"  # UTC event time
        capture_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"api_enhanced_snapshot_{capture_stamp}_{event_stamp}_dallas-1987-07-15-0901_p32.7833_m96.8000.json"
        out_path = os.path.join(snapshots_dir, filename)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\nSnapshot written to: {os.path.relpath(out_path, start=repo_root)}\n")


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
