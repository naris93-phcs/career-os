import tkinter as tk
from tkinter import messagebox, ttk

from src.analytics import get_summary
from src.excel_export import export_to_excel
from src.jobs import (
    VALID_ELIGIBILITY,
    VALID_STATUS,
    add_job,
    delete_job,
    list_jobs,
    update_status,
)


class CareerOSApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Career OS")
        self.geometry("1250x760")
        self.minsize(1050, 650)

        self._build_ui()
        self.refresh_jobs()
        self.refresh_analytics()

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.jobs_tab = ttk.Frame(notebook)
        self.add_tab = ttk.Frame(notebook)
        self.analytics_tab = ttk.Frame(notebook)

        notebook.add(self.jobs_tab, text="Jobs")
        notebook.add(self.add_tab, text="Add Job")
        notebook.add(self.analytics_tab, text="Analytics")

        self._build_jobs_tab()
        self._build_add_tab()
        self._build_analytics_tab()

    def _build_jobs_tab(self):
        toolbar = ttk.Frame(self.jobs_tab)
        toolbar.pack(fill="x", pady=(0, 8))

        ttk.Label(toolbar, text="New status:").pack(side="left")

        self.status_var = tk.StringVar(value="APPLIED")
        status_box = ttk.Combobox(
            toolbar,
            textvariable=self.status_var,
            values=sorted(VALID_STATUS),
            state="readonly",
            width=14,
        )
        status_box.pack(side="left", padx=6)

        ttk.Button(
            toolbar,
            text="Update selected",
            command=self.update_selected_status,
        ).pack(side="left", padx=4)

        ttk.Button(
            toolbar,
            text="Delete selected",
            command=self.delete_selected,
        ).pack(side="left", padx=4)

        ttk.Button(
            toolbar,
            text="Refresh",
            command=self.refresh_jobs,
        ).pack(side="left", padx=4)

        ttk.Button(
            toolbar,
            text="Export Excel",
            command=self.export_excel,
        ).pack(side="right", padx=4)

        columns = (
            "id",
            "company",
            "role",
            "country",
            "match",
            "eligibility",
            "status",
            "found",
            "applied",
        )

        self.tree = ttk.Treeview(
            self.jobs_tab,
            columns=columns,
            show="headings",
            height=25,
        )

        headings = {
            "id": "ID",
            "company": "Company",
            "role": "Role",
            "country": "Country",
            "match": "Match",
            "eligibility": "Eligibility",
            "status": "Status",
            "found": "Found",
            "applied": "Applied",
        }

        widths = {
            "id": 50,
            "company": 150,
            "role": 320,
            "country": 120,
            "match": 70,
            "eligibility": 100,
            "status": 100,
            "found": 100,
            "applied": 100,
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")

        scrollbar = ttk.Scrollbar(
            self.jobs_tab,
            orient="vertical",
            command=self.tree.yview,
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_add_tab(self):
        frame = ttk.Frame(self.add_tab, padding=15)
        frame.pack(fill="both", expand=True)

        fields = [
            ("Company *", "company"),
            ("Role *", "role"),
            ("Country", "country"),
            ("City", "city"),
            ("URL", "url"),
            ("Deadline (YYYY-MM-DD)", "deadline"),
            ("Match score (0-100)", "match_score"),
            ("Salary", "salary"),
            ("Required skills (comma separated)", "required_skills"),
            ("Missing skills (comma separated)", "missing_skills"),
            ("CV version", "cv_version"),
        ]

        self.entries = {}

        for row, (label, key) in enumerate(fields):
            ttk.Label(frame, text=label).grid(
                row=row,
                column=0,
                sticky="w",
                padx=(0, 10),
                pady=4,
            )

            entry = ttk.Entry(frame, width=75)
            entry.grid(row=row, column=1, sticky="ew", pady=4)
            self.entries[key] = entry

        row = len(fields)

        ttk.Label(frame, text="Eligibility").grid(
            row=row, column=0, sticky="w", pady=4
        )
        self.eligibility_var = tk.StringVar(value="APPLY")
        ttk.Combobox(
            frame,
            textvariable=self.eligibility_var,
            values=sorted(VALID_ELIGIBILITY),
            state="readonly",
            width=20,
        ).grid(row=row, column=1, sticky="w", pady=4)

        row += 1

        ttk.Label(frame, text="Cover letter").grid(
            row=row, column=0, sticky="w", pady=4
        )
        self.cover_letter_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame,
            variable=self.cover_letter_var,
        ).grid(row=row, column=1, sticky="w", pady=4)

        row += 1

        ttk.Label(frame, text="Notes").grid(
            row=row, column=0, sticky="nw", pady=4
        )
        self.notes_text = tk.Text(frame, width=75, height=6)
        self.notes_text.grid(row=row, column=1, sticky="ew", pady=4)

        row += 1

        ttk.Button(
            frame,
            text="Save Job",
            command=self.save_job,
        ).grid(row=row, column=1, sticky="e", pady=12)

        frame.columnconfigure(1, weight=1)

    def _build_analytics_tab(self):
        top = ttk.Frame(self.analytics_tab, padding=15)
        top.pack(fill="x")

        ttk.Button(
            top,
            text="Refresh analytics",
            command=self.refresh_analytics,
        ).pack(side="left")

        self.kpi_label = ttk.Label(
            top,
            text="",
            font=("Segoe UI", 12, "bold"),
        )
        self.kpi_label.pack(side="left", padx=20)

        body = ttk.Frame(self.analytics_tab, padding=(15, 0, 15, 15))
        body.pack(fill="both", expand=True)

        left = ttk.LabelFrame(body, text="Status / Countries", padding=10)
        right = ttk.LabelFrame(body, text="Skill Intelligence", padding=10)

        left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        right.pack(side="left", fill="both", expand=True, padx=(6, 0))

        self.status_text = tk.Text(left, wrap="word")
        self.status_text.pack(fill="both", expand=True)

        self.skills_text = tk.Text(right, wrap="word")
        self.skills_text.pack(fill="both", expand=True)

    def refresh_jobs(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for job in list_jobs():
            self.tree.insert(
                "",
                "end",
                values=(
                    job["id"],
                    job["company"],
                    job["role"],
                    job["country"] or "",
                    job["match_score"] if job["match_score"] is not None else "",
                    job["eligibility"] or "",
                    job["status"] or "",
                    job["date_found"] or "",
                    job["date_applied"] or "",
                ),
            )

    def save_job(self):
        data = {
            key: entry.get().strip()
            for key, entry in self.entries.items()
        }

        try:
            result = add_job(
                company=data["company"],
                role=data["role"],
                country=data["country"],
                city=data["city"],
                url=data["url"],
                deadline=data["deadline"],
                match_score=data["match_score"],
                eligibility=self.eligibility_var.get(),
                required_skills=data["required_skills"],
                missing_skills=data["missing_skills"],
                cv_version=data["cv_version"],
                cover_letter=self.cover_letter_var.get(),
                notes=self.notes_text.get("1.0", "end").strip(),
                salary=data["salary"],
            )
        except Exception as exc:
            messagebox.showerror("Career OS", str(exc))
            return

        if not result["created"]:
            duplicate = result["duplicate"]
            answer = messagebox.askyesno(
                "Possible duplicate",
                f"This looks like an existing job:\n\n"
                f"[{duplicate['id']}] {duplicate['company']} — {duplicate['role']}\n\n"
                f"Save another copy anyway?",
            )
            if not answer:
                return

            result = add_job(
                company=data["company"],
                role=data["role"],
                country=data["country"],
                city=data["city"],
                url=data["url"],
                deadline=data["deadline"],
                match_score=data["match_score"],
                eligibility=self.eligibility_var.get(),
                required_skills=data["required_skills"],
                missing_skills=data["missing_skills"],
                cv_version=data["cv_version"],
                cover_letter=self.cover_letter_var.get(),
                notes=self.notes_text.get("1.0", "end").strip(),
                salary=data["salary"],
                allow_duplicate=True,
            )

        messagebox.showinfo(
            "Career OS",
            f"Job saved with ID {result['job_id']}.",
        )

        for entry in self.entries.values():
            entry.delete(0, "end")
        self.notes_text.delete("1.0", "end")
        self.eligibility_var.set("APPLY")
        self.cover_letter_var.set(False)

        self.refresh_jobs()
        self.refresh_analytics()

    def _selected_job_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Career OS", "Select a job first.")
            return None

        values = self.tree.item(selected[0], "values")
        return int(values[0])

    def update_selected_status(self):
        job_id = self._selected_job_id()
        if job_id is None:
            return

        try:
            update_status(job_id, self.status_var.get())
        except Exception as exc:
            messagebox.showerror("Career OS", str(exc))
            return

        self.refresh_jobs()
        self.refresh_analytics()

    def delete_selected(self):
        job_id = self._selected_job_id()
        if job_id is None:
            return

        if not messagebox.askyesno(
            "Career OS",
            f"Delete job #{job_id}?",
        ):
            return

        delete_job(job_id)
        self.refresh_jobs()
        self.refresh_analytics()

    def refresh_analytics(self):
        s = get_summary()

        self.kpi_label.config(
            text=(
                f"Tracked: {s['total_jobs']}   |   "
                f"Applied: {s['applied_jobs']}   |   "
                f"Interviews: {s['interviews']}   |   "
                f"Offers: {s['offers']}   |   "
                f"Interview rate: {s['response_rate']}%"
            )
        )

        status_lines = ["BY STATUS"]
        for key, value in s["by_status"].items():
            status_lines.append(f"{key:<15} {value}")

        status_lines.extend(["", "BY COUNTRY"])
        for key, value in s["by_country"].items():
            status_lines.append(f"{key:<22} {value}")

        self.status_text.delete("1.0", "end")
        self.status_text.insert("1.0", "\n".join(status_lines))

        skill_lines = ["TOP REQUIRED SKILLS"]
        for skill, count in s["required_skills"][:15]:
            skill_lines.append(f"{skill:<30} {count}")

        skill_lines.extend(["", "TOP MISSING SKILLS"])
        for skill, count in s["missing_skills"][:15]:
            skill_lines.append(f"{skill:<30} {count}")

        self.skills_text.delete("1.0", "end")
        self.skills_text.insert("1.0", "\n".join(skill_lines))

    def export_excel(self):
        try:
            path = export_to_excel()
        except Exception as exc:
            messagebox.showerror("Career OS", f"Export failed:\n{exc}")
            return

        messagebox.showinfo(
            "Career OS",
            f"Excel export created:\n{path}",
        )


def run_gui():
    app = CareerOSApp()
    app.mainloop()
