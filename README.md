# Career OS

A lightweight local job-search tracker built with Python, SQLite and Tkinter.

## Features

- Graphical interface
- Add and list jobs
- APPLY / STRETCH / SKIP classification
- Application status updates
- Duplicate detection by URL or company + role
- Required and missing skill tracking
- Skill-frequency analytics
- Application funnel analytics
- Excel (.xlsx) export with Jobs, Skills and Analytics sheets
- Local SQLite storage
- No third-party Python dependencies

## Run

Activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Then:

```powershell
python main.py
```

Your existing `database/career.db` is preserved. On first run, Career OS automatically upgrades an older v0.1 database schema if needed.

## Status values

- SAVED
- APPLIED
- REJECTED
- INTERVIEW
- FINAL
- OFFER
- WITHDRAWN

## Privacy

The SQLite database contains personal job-search information and should remain excluded from Git via `.gitignore`.
