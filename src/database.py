import sqlite3
import sys
from pathlib import Path


if getattr(sys, "frozen", False):
    DATA_DIR = Path.home() / "CareerOS"
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    DATA_DIR = PROJECT_ROOT / "database"


DB_PATH = DATA_DIR / "career.db"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _add_missing_columns(connection):
    existing = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(jobs)").fetchall()
    }

    columns = {
        "city": "TEXT",
        "deadline": "TEXT",
        "match_score": "INTEGER",
        "cv_version": "TEXT",
        "cover_letter": "INTEGER DEFAULT 0",
        "notes": "TEXT",
        "date_applied": "TEXT",
        "salary": "TEXT",
    }

    for name, definition in columns.items():
        if name not in existing:
            connection.execute(
                f"ALTER TABLE jobs ADD COLUMN {name} {definition}"
            )


def create_database():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            country TEXT,
            city TEXT,
            url TEXT,
            date_found TEXT NOT NULL,
            deadline TEXT,
            match_score INTEGER,
            eligibility TEXT,
            status TEXT DEFAULT 'SAVED',
            required_skills TEXT,
            missing_skills TEXT,
            cv_version TEXT,
            cover_letter INTEGER DEFAULT 0,
            notes TEXT,
            date_applied TEXT,
            salary TEXT
        )
        """
    )

    _add_missing_columns(connection)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS job_skills (
            job_id INTEGER NOT NULL,
            skill_id INTEGER NOT NULL,
            skill_type TEXT NOT NULL CHECK(skill_type IN ('REQUIRED', 'MISSING')),
            PRIMARY KEY (job_id, skill_id, skill_type),
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
        )
        """
    )

    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)"
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_jobs_company_role ON jobs(company, role)"
    )

    connection.commit()
    connection.close()
