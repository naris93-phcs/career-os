from collections import Counter
from datetime import date, timedelta

from src.database import get_connection


def get_summary():
    connection = get_connection()

    total = connection.execute(
        "SELECT COUNT(*) AS n FROM jobs"
    ).fetchone()["n"]

    status_rows = connection.execute(
        """
        SELECT status, COUNT(*) AS n
        FROM jobs
        GROUP BY status
        ORDER BY n DESC
        """
    ).fetchall()

    eligibility_rows = connection.execute(
        """
        SELECT eligibility, COUNT(*) AS n
        FROM jobs
        GROUP BY eligibility
        ORDER BY n DESC
        """
    ).fetchall()

    country_rows = connection.execute(
        """
        SELECT country, COUNT(*) AS n
        FROM jobs
        WHERE TRIM(COALESCE(country, '')) <> ''
        GROUP BY country
        ORDER BY n DESC, country
        """
    ).fetchall()

    average_match = connection.execute(
        """
        SELECT ROUND(AVG(match_score), 1) AS avg_match
        FROM jobs
        WHERE match_score IS NOT NULL
        """
    ).fetchone()["avg_match"]

    applied = connection.execute(
        """
        SELECT COUNT(*) AS n
        FROM jobs
        WHERE status IN ('APPLIED', 'INTERVIEW', 'FINAL', 'OFFER', 'REJECTED')
        """
    ).fetchone()["n"]

    interviews = connection.execute(
        """
        SELECT COUNT(*) AS n
        FROM jobs
        WHERE status IN ('INTERVIEW', 'FINAL', 'OFFER')
        """
    ).fetchone()["n"]

    offers = connection.execute(
        "SELECT COUNT(*) AS n FROM jobs WHERE status = 'OFFER'"
    ).fetchone()["n"]

    skill_rows = connection.execute(
        """
        SELECT s.name, js.skill_type, COUNT(*) AS n
        FROM job_skills js
        JOIN skills s ON s.id = js.skill_id
        GROUP BY s.name, js.skill_type
        ORDER BY n DESC, s.name
        """
    ).fetchall()

    deadline_rows = connection.execute(
        """
        SELECT deadline, status
        FROM jobs
        WHERE TRIM(COALESCE(deadline, '')) <> ''
        """
    ).fetchall()

    connection.close()

    required_skills = Counter()
    missing_skills = Counter()

    for row in skill_rows:
        if row["skill_type"] == "REQUIRED":
            required_skills[row["name"]] = row["n"]
        else:
            missing_skills[row["name"]] = row["n"]

    response_rate = round((interviews / applied) * 100, 1) if applied else 0.0
    offer_rate = round((offers / applied) * 100, 1) if applied else 0.0
    today = date.today()
    soon_limit = today + timedelta(days=7)
    overdue = 0
    due_soon = 0
    for row in deadline_rows:
        if row["status"] in ("REJECTED", "WITHDRAWN", "OFFER"):
            continue
        try:
            deadline = date.fromisoformat(row["deadline"])
        except ValueError:
            continue
        if deadline < today:
            overdue += 1
        elif deadline <= soon_limit:
            due_soon += 1

    return {
        "total_jobs": total,
        "applied_jobs": applied,
        "interviews": interviews,
        "offers": offers,
        "response_rate": response_rate,
        "offer_rate": offer_rate,
        "average_match": average_match,
        "by_status": {row["status"]: row["n"] for row in status_rows},
        "by_eligibility": {
            row["eligibility"]: row["n"] for row in eligibility_rows
        },
        "by_country": {row["country"]: row["n"] for row in country_rows},
        "required_skills": required_skills.most_common(),
        "missing_skills": missing_skills.most_common(),
        "deadlines_tracked": len(deadline_rows),
        "overdue_deadlines": overdue,
        "deadlines_due_soon": due_soon,
    }
