import sys
from pathlib import Path

import pandas as pd

sys.path.append("src")

import database


def test_save_and_retrieve_latest_review(tmp_path, monkeypatch):
    test_db = tmp_path / "governance.db"
    monkeypatch.setattr(database, "DB_PATH", test_db)

    database.init_db()
    database.save_review(
        content_id="TEST-001",
        system_recommendation="Update",
        ai_summary="Qualitative observations",
        human_assessment="Keep",
        final_decision="Review",
        rationale="Strategic value warrants additional review.",
    )

    result = database.get_latest_review("TEST-001")

    assert result is not None
    assert result["content_id"] == "TEST-001"
    assert result["system_recommendation"] == "Update"
    assert result["human_assessment"] == "Keep"
    assert result["final_decision"] == "Review"
    assert result["rationale"] == "Strategic value warrants additional review."


def test_latest_review_is_most_recent(tmp_path, monkeypatch):
    test_db = tmp_path / "governance.db"
    monkeypatch.setattr(database, "DB_PATH", test_db)

    database.init_db()
    database.save_review("TEST-002", "Update", "First", "Keep", "Review", "First rationale")
    database.save_review("TEST-002", "Update", "Second", "Review", "Update", "Second rationale")

    result = database.get_latest_review("TEST-002")

    assert result["human_assessment"] == "Review"
    assert result["final_decision"] == "Update"
    assert result["rationale"] == "Second rationale"
