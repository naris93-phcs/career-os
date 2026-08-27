# Career OS

**A local-first Python desktop application for managing, analysing, and improving a structured job-search pipeline.**

Career OS turns job searching from a collection of bookmarks, notes, and spreadsheets into a structured, data-driven workflow.

It provides a single desktop interface for tracking opportunities, evaluating role fit, identifying recurring skill gaps, monitoring application outcomes, and deciding where to focus next.

Built with **Python and Tkinter**, Career OS keeps personal application data local while providing analytics and decision-support tools directly inside the application.

---

## Features

### Job Pipeline Management

Track opportunities throughout the entire application process.

For every position, Career OS can store:

* Company
* Role
* Country and city
* Original job posting URL
* Application deadline
* Match score
* Eligibility
* Application status
* Salary
* Required skills
* Missing skills
* CV version
* Cover letter status
* Notes
* Date found
* Date applied

Jobs can move through different stages of the application pipeline, including:

`SAVED → APPLIED → INTERVIEW → OFFER`

Rejected opportunities remain recorded so application outcomes can contribute to the overall search analytics.

---

## Direct Job Posting Access

Each tracked opportunity can retain the URL of the original vacancy.

From the Jobs dashboard, a position can be selected and opened directly in the default browser using the **Open Job Posting** action.

This keeps the main interface compact while maintaining immediate access to the original vacancy.

---

## Match & Eligibility Tracking

Career OS separates two important questions:

**Am I eligible for this position?**

and

**How strongly does my current profile match it?**

Each vacancy can therefore be evaluated using:

* Eligibility status
* Match score from `0–100`
* Required skills
* Missing skills

This makes it easier to distinguish between strong targets, reasonable stretch opportunities, and applications that are unlikely to justify the time investment.

---

## Skill Intelligence

Career OS aggregates skill requirements across tracked vacancies.

The analytics system can identify:

* Frequently requested skills
* Recurring skill gaps
* Technologies worth prioritising
* Areas where portfolio development may have the highest impact

Instead of choosing new skills or technologies arbitrarily, development priorities can be informed by actual patterns in the job pipeline.

---

## Application Analytics

The Analytics dashboard provides a live overview of the search.

Tracked metrics include:

* Total jobs
* Applications submitted
* Interviews
* Offers
* Response rate
* Average match score
* Applications by status
* Applications by country
* Frequently required skills
* Frequently missing skills

An application funnel visualises progression through the pipeline:

`Tracked → Applied → Interviews → Offers`

---

## Decision Support

Career OS is designed to do more than store vacancies.

The **Insights** and **Next Best Moves** sections analyse the current pipeline and generate actionable signals based on:

* Upcoming deadlines
* Overdue opportunities
* Response rate
* Average role match
* Repeated skill gaps
* Current application activity

The objective is to turn accumulated job-search data into practical decisions about what to apply for, what to learn, and what to prioritise next.

---

## Excel Export

Career OS supports exporting pipeline data to Excel for:

* External analysis
* Archiving
* Reporting
* Manual review
* Long-term tracking

---

## Local-First by Design

Career OS is designed as a **local-first application**.

Personal job-search data stays on the user's machine and is intentionally excluded from version control.

This allows the source code to be shared publicly without exposing private application records.

---

## Technology

Career OS currently uses:

* **Python**
* **Tkinter / ttk**
* Local persistent data storage
* Modular Python application architecture
* Data aggregation and analytics
* Excel export
* Git for version control

---

## Project Structure

The application is organised around separate modules for the GUI, job management, analytics, and data export.

A simplified structure looks like:

```text
career-os/
│
├── src/
│   ├── analytics.py
│   ├── excel_export.py
│   ├── jobs.py
│   └── ...
│
├── gui.py
├── .gitignore
└── README.md
```

Generated application builds and personal data are kept outside version control.

---

## Running the Application

Career OS is a Python desktop application.

The application can be launched using its Python entry point from the project directory.

A standalone Windows executable can also be generated using **PyInstaller**, allowing the application to run without manually launching the Python source.

---

## Windows Executable

Career OS has been successfully packaged as a standalone Windows application.

PyInstaller-generated files are intentionally excluded from the main Git repository because they are generated build artifacts rather than source code.

The local build structure includes:

```text
dist/
└── CareerOS.exe
```

Future stable versions may be distributed separately through **GitHub Releases**.

---

## Version Control

Generated files, local environments, and personal application data are intentionally excluded from Git.

Recommended exclusions include:

```text
dist/
build/
*.db
*.sqlite
*.sqlite3
exports/
.venv/
__pycache__/
.env
```

This keeps the repository focused on reproducible source code while protecting private job-search information.

---

## Design Philosophy

Job searching is fundamentally a decision-making problem under limited time.

A candidate may be evaluating dozens of roles with different deadlines, locations, skill requirements, eligibility conditions, and application costs.

Career OS treats this process as a structured pipeline rather than an unorganised collection of vacancies.

The workflow follows:

**Discover → Evaluate → Prioritise → Apply → Track → Analyse → Improve**

The system is intended to help answer questions such as:

* Which opportunities deserve attention first?
* Which positions are the strongest matches?
* Which applications are reasonable stretches?
* Which skill gaps appear repeatedly?
* Where should development time be invested?
* Is the current application strategy producing interviews?
* Which countries or role types are producing better outcomes?
* Which CV versions perform best?

---

## Roadmap

Potential future development includes:

* Advanced job filtering and search
* Deadline-based prioritisation
* Configurable application scoring
* Improved visual analytics
* Skill-gap trend analysis
* CV-version performance tracking
* Company and role-type analytics
* Follow-up reminders
* Job-source tracking
* Application history
* Improved data visualisation
* Automated backup and restore
* Improved release packaging

---

## Privacy

Career OS may contain sensitive personal job-search information.

Databases, exported application records, credentials, environment files, and other personal data should **never be committed to a public repository**.

Only the application source code and appropriate project documentation should be version controlled.

---

## Development Status

**Active development**

Career OS is currently being used and iteratively improved as part of a real-world job-search workflow.

Features are added based on practical needs encountered during active use of the application.

---

## License

No open-source license has been selected yet.

---

## Author

Developed as an independent Python software project focused on structured job-search management, analytics, and decision support.

---

**Career OS**

*Track the pipeline. Understand the gaps. Make the next move count.*
