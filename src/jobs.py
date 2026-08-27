from datetime import date

from src.database import get_connection

VALID_ELIGIBILITY = {"APPLY", "STRETCH", "SKIP"}
VALID_STATUS = {
    "SAVED",
    "APPLIED",
    "REJECTED",
    "INTERVIEW",
    "FINAL",
    "OFFER",
    "WITHDRAWN",
}


def _clean(value):
    return value.strip() if isinstance(value, str) else value


def _split_skills(value):
    if not value:
        return []
    if isinstance(value, (list, tuple, set)):
        parts = value
    else:
        parts = value.replace(";", ",").split(",")

    seen = set()
    result = []
    for part in parts:
        skill = str(part).strip()
        key = skill.casefold()
        if skill and key not in seen:
            result.append(skill)
            seen.add(key)
    return result


def _save_skills(connection, job_id, skills, skill_type):
    for skill in _split_skills(skills):
        connection.execute(
            "INSERT OR IGNORE INTO skills(name) VALUES (?)",
            (skill,),
        )
        skill_id = connection.execute(
            "SELECT id FROM skills WHERE name = ? COLLATE NOCASE",
            (skill,),
        ).fetchone()["id"]

        connection.execute(
            """
            INSERT OR IGNORE INTO job_skills(job_id, skill_id, skill_type)
            VALUES (?, ?, ?)
            """,
            (job_id, skill_id, skill_type),
        )


def find_duplicate(company, role, url=""):
    connection = get_connection()

    duplicate = None
    if url and url.strip():
        duplicate = connection.execute(
            "SELECT * FROM jobs WHERE LOWER(TRIM(url)) = LOWER(TRIM(?)) LIMIT 1",
            (url,),
        ).fetchone()

    if duplicate is None:
        duplicate = connection.execute(
            """
            SELECT *
            FROM jobs
            WHERE LOWER(TRIM(company)) = LOWER(TRIM(?))
              AND LOWER(TRIM(role)) = LOWER(TRIM(?))
            LIMIT 1
            """,
            (company, role),
        ).fetchone()

    connection.close()
    return dict(duplicate) if duplicate else None


def add_job(
    company,
    role,
    country="",
    city="",
    url="",
    date_found=None,
    deadline="",
    match_score=None,
    eligibility="APPLY",
    status="SAVED",
    required_skills="",
    missing_skills="",
    cv_version="",
    cover_letter=False,
    notes="",
    date_applied="",
    salary="",
    allow_duplicate=False,
):
    company = _clean(company)
    role = _clean(role)
    eligibility = (_clean(eligibility) or "APPLY").upper()
    status = (_clean(status) or "SAVED").upper()

    if not company or not role:
        raise ValueError("Company and role are required.")

    if eligibility not in VALID_ELIGIBILITY:
        raise ValueError(f"Eligibility must be one of: {sorted(VALID_ELIGIBILITY)}")

    if status not in VALID_STATUS:
        raise ValueError(f"Status must be one of: {sorted(VALID_STATUS)}")

    if not allow_duplicate:
        duplicate = find_duplicate(company, role, url)
        if duplicate:
            return {
                "created": False,
                "duplicate": duplicate,
            }

    if match_score in ("", None):
        match_score = None
    else:
        match_score = int(match_score)
        if not 0 <= match_score <= 100:
            raise ValueError("Match score must be between 0 and 100.")

    if not date_found:
        date_found = date.today().isoformat()

    required_list = _split_skills(required_skills)
    missing_list = _split_skills(missing_skills)

    connection = get_connection()
    cursor = connection.execute(
        """
        INSERT INTO jobs (
            company, role, country, city, url, date_found, deadline,
            match_score, eligibility, status, required_skills,
            missing_skills, cv_version, cover_letter, notes,
            date_applied, salary
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            company,
            role,
            _clean(country),
            _clean(city),
            _clean(url),
            date_found,
            _clean(deadline),
            match_score,
            eligibility,
            status,
            ", ".join(required_list),
            ", ".join(missing_list),
            _clean(cv_version),
            int(bool(cover_letter)),
            _clean(notes),
            _clean(date_applied),
            _clean(salary),
        ),
    )
    job_id = cursor.lastrowid

    _save_skills(connection, job_id, required_list, "REQUIRED")
    _save_skills(connection, job_id, missing_list, "MISSING")

    connection.commit()
    connection.close()

    return {"created": True, "job_id": job_id}


def list_jobs(status=None):
    connection = get_connection()

    query = """
        SELECT id, company, role, country, city, match_score,
               eligibility, status, date_found, date_applied,
               deadline, salary, url
        FROM jobs
    """
    params = []

    if status:
        query += " WHERE status = ?"
        params.append(status.upper())

    query += " ORDER BY id DESC"

    rows = connection.execute(query, params).fetchall()
    connection.close()

    return [dict(row) for row in rows]


def get_job(job_id):
    connection = get_connection()
    row = connection.execute(
        "SELECT * FROM jobs WHERE id = ?",
        (job_id,),
    ).fetchone()
    connection.close()
    return dict(row) if row else None


def update_status(job_id, status):
    status = status.upper().strip()
    if status not in VALID_STATUS:
        raise ValueError(f"Status must be one of: {sorted(VALID_STATUS)}")

    connection = get_connection()

    if status == "APPLIED":
        connection.execute(
            """
            UPDATE jobs
            SET status = ?,
                date_applied = COALESCE(NULLIF(date_applied, ''), ?)
            WHERE id = ?
            """,
            (status, date.today().isoformat(), job_id),
        )
    else:
        connection.execute(
            "UPDATE jobs SET status = ? WHERE id = ?",
            (status, job_id),
        )

    connection.commit()
    changed = connection.total_changes
    connection.close()
    return changed > 0


def update_job(job_id, **fields):
    allowed = {
        "company", "role", "country", "city", "url", "date_found",
        "deadline", "match_score", "eligibility", "status",
        "required_skills", "missing_skills", "cv_version", "cover_letter",
        "notes", "date_applied", "salary",
    }
    unknown = set(fields) - allowed
    if unknown:
        raise ValueError(f"Unknown job fields: {sorted(unknown)}")

    company = _clean(fields.get("company"))
    role = _clean(fields.get("role"))
    if not company or not role:
        raise ValueError("Company and role are required.")

    eligibility = (_clean(fields.get("eligibility")) or "APPLY").upper()
    status = (_clean(fields.get("status")) or "SAVED").upper()
    if eligibility not in VALID_ELIGIBILITY:
        raise ValueError(f"Eligibility must be one of: {sorted(VALID_ELIGIBILITY)}")
    if status not in VALID_STATUS:
        raise ValueError(f"Status must be one of: {sorted(VALID_STATUS)}")

    match_score = fields.get("match_score")
    if match_score in ("", None):
        match_score = None
    else:
        match_score = int(match_score)
        if not 0 <= match_score <= 100:
            raise ValueError("Match score must be between 0 and 100.")

    required = _split_skills(fields.get("required_skills", ""))
    missing = _split_skills(fields.get("missing_skills", ""))
    values = {
        "company": company,
        "role": role,
        "country": _clean(fields.get("country", "")),
        "city": _clean(fields.get("city", "")),
        "url": _clean(fields.get("url", "")),
        "date_found": _clean(fields.get("date_found", "")),
        "deadline": _clean(fields.get("deadline", "")),
        "match_score": match_score,
        "eligibility": eligibility,
        "status": status,
        "required_skills": ", ".join(required),
        "missing_skills": ", ".join(missing),
        "cv_version": _clean(fields.get("cv_version", "")),
        "cover_letter": int(bool(fields.get("cover_letter"))),
        "notes": _clean(fields.get("notes", "")),
        "date_applied": _clean(fields.get("date_applied", "")),
        "salary": _clean(fields.get("salary", "")),
    }

    connection = get_connection()
    assignments = ", ".join(f"{name} = ?" for name in values)
    connection.execute(
        f"UPDATE jobs SET {assignments} WHERE id = ?",
        (*values.values(), job_id),
    )
    changed = connection.total_changes
    connection.execute("DELETE FROM job_skills WHERE job_id = ?", (job_id,))
    _save_skills(connection, job_id, required, "REQUIRED")
    _save_skills(connection, job_id, missing, "MISSING")
    connection.commit()
    connection.close()
    return changed > 0


def delete_job(job_id):
    connection = get_connection()
    connection.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    connection.commit()
    changed = connection.total_changes
    connection.close()
    return changed > 0
