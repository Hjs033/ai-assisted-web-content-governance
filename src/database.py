import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "governance.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id TEXT NOT NULL,
            system_recommendation TEXT NOT NULL,
            ai_summary TEXT NOT NULL,
            human_assessment TEXT NOT NULL,
            final_decision TEXT NOT NULL,
            rationale TEXT NOT NULL,
            criteria_version TEXT NOT NULL DEFAULT '1.0',
            prompt_version TEXT NOT NULL DEFAULT '1.0',
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_review(
    content_id,
    system_recommendation,
    ai_summary,
    human_assessment,
    final_decision,
    rationale,
):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO audit_log
        (content_id, system_recommendation, ai_summary, human_assessment,
         final_decision, rationale, criteria_version, prompt_version, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, '1.0', '1.0', ?)
        """,
        (
            content_id,
            system_recommendation,
            ai_summary,
            human_assessment,
            final_decision,
            rationale,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    conn.close()


def get_latest_review(content_id):
    """Return the most recent saved governance decision for a content item."""
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT id, content_id, system_recommendation, ai_summary,
               human_assessment, final_decision, rationale,
               criteria_version, prompt_version, timestamp
        FROM audit_log
        WHERE content_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        conn,
        params=(content_id,),
    )
    conn.close()
    if df.empty:
        return None
    return df.iloc[0].to_dict()


def get_audit_records():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT id, content_id, system_recommendation,
               human_assessment, final_decision, rationale,
               criteria_version, prompt_version, timestamp
        FROM audit_log ORDER BY id DESC
        """,
        conn,
    )
    conn.close()
    return df
