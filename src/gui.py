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
        self.geometry("1280x800")
        self.minsize(1080, 680)
        self._configure_theme()

        self._build_ui()
        self.refresh_jobs()
        self.refresh_analytics()

    def _configure_theme(self):
        self.colors = {
            "ink": "#17233C", "muted": "#667085", "canvas": "#F5F7FB",
            "panel": "#FFFFFF", "line": "#DCE3EF", "teal": "#087F8C",
            "teal_dark": "#05616B", "coral": "#E76F51",
            "green": "#2A9D72", "red": "#C94C4C",
        }
        self.configure(bg=self.colors["canvas"])
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=self.colors["canvas"])
        style.configure("Panel.TFrame", background=self.colors["panel"])
        style.configure("TLabel", background=self.colors["canvas"], foreground=self.colors["ink"], font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=self.colors["canvas"], foreground=self.colors["ink"], font=("Segoe UI", 24, "bold"))
        style.configure("Subtitle.TLabel", background=self.colors["canvas"], foreground=self.colors["muted"], font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=self.colors["canvas"], foreground=self.colors["ink"], font=("Segoe UI", 12, "bold"))
        style.configure("TButton", padding=(13, 8), background=self.colors["panel"], foreground=self.colors["ink"], font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", "#E7EEF7")])
        style.configure("Accent.TButton", background=self.colors["teal"], foreground="white", padding=(16, 9))
        style.map("Accent.TButton", background=[("active", self.colors["teal_dark"])])
        style.configure("TNotebook", background=self.colors["canvas"], borderwidth=0)
        style.configure("TNotebook.Tab", background="#E8EDF5", foreground=self.colors["muted"], padding=(22, 10), font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", self.colors["panel"])], foreground=[("selected", self.colors["teal_dark"])])
        style.configure("Treeview", background=self.colors["panel"], fieldbackground=self.colors["panel"], foreground=self.colors["ink"], rowheight=34, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#E8EDF5", foreground=self.colors["ink"], relief="flat", padding=(8, 9), font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", "#CDEBEA")], foreground=[("selected", self.colors["ink"])])
        style.configure("TEntry", padding=8, fieldbackground=self.colors["panel"])
        style.configure("TCombobox", padding=7)
        style.configure("TLabelframe", background=self.colors["panel"], bordercolor=self.colors["line"])
        style.configure("TLabelframe.Label", background=self.colors["panel"], foreground=self.colors["ink"], font=("Segoe UI", 11, "bold"))

    def _build_ui(self):
        header = ttk.Frame(self, padding=(28, 22, 28, 14))
        header.pack(fill="x")
        ttk.Label(header, text="Career OS", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="Your job search, with a clearer next move.", style="Subtitle.TLabel").pack(side="left", padx=(16, 0), pady=(8, 0))

        notebook = ttk.Notebook(self)
        self.notebook = notebook
        notebook.pack(fill="both", expand=True, padx=22, pady=(0, 22))

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
        toolbar = ttk.Frame(self.jobs_tab, padding=(6, 14, 6, 12))
        toolbar.pack(fill="x")

        ttk.Label(toolbar, text="Move selected job to:").pack(side="left")

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

        self.tree.tag_configure("APPLIED", foreground=self.colors["teal_dark"])
        self.tree.tag_configure("INTERVIEW", foreground=self.colors["green"])
        self.tree.tag_configure("OFFER", foreground=self.colors["green"], font=("Segoe UI", 10, "bold"))
        self.tree.tag_configure("REJECTED", foreground=self.colors["red"])

        scrollbar = ttk.Scrollbar(
            self.jobs_tab,
            orient="vertical",
            command=self.tree.yview,
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_add_tab(self):
        scroll_container = ttk.Frame(self.add_tab)
        scroll_container.pack(fill="both", expand=True)

        canvas = tk.Canvas(
            scroll_container,
            background=self.colors["canvas"],
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(
            scroll_container,
            orient="vertical",
            command=canvas.yview,
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame = ttk.Frame(canvas, padding=(30, 22, 30, 30))
        frame_window = canvas.create_window((0, 0), window=frame, anchor="nw")

        def update_scroll_region(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def resize_form(event):
            canvas.itemconfigure(frame_window, width=event.width)

        frame.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", resize_form)
        self.add_form_canvas = canvas
        self.bind_all("<MouseWheel>", self._scroll_add_form)
        self.bind_all("<Button-4>", self._scroll_add_form)
        self.bind_all("<Button-5>", self._scroll_add_form)
        canvas.bind("<Prior>", lambda _event: canvas.yview_scroll(-8, "units"))
        canvas.bind("<Next>", lambda _event: canvas.yview_scroll(8, "units"))

        ttk.Label(frame, text="Add a job to your pipeline", style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 3))
        ttk.Label(frame, text="Capture the details now; keep the decision visible later.", style="Subtitle.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 18))

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

        for row, (label, key) in enumerate(fields, start=2):
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

        row = len(fields) + 2

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
            style="Accent.TButton",
        ).grid(row=row, column=1, sticky="e", pady=18)

        frame.columnconfigure(1, weight=1)

    def _scroll_add_form(self, event):
        if self.notebook.select() != str(self.add_tab):
            return

        if event.num == 4:
            units = -3
        elif event.num == 5:
            units = 3
        else:
            units = -max(1, round(event.delta / 120))
        self.add_form_canvas.yview_scroll(units, "units")
        return "break"

    def _build_analytics_tab(self):
        top = ttk.Frame(self.analytics_tab, padding=(6, 14, 6, 10))
        top.pack(fill="x")

        ttk.Button(
            top,
            text="Refresh analytics",
            command=self.refresh_analytics,
        ).pack(side="left")

        self.kpi_frame = ttk.Frame(top)
        self.kpi_frame.pack(side="right", fill="x", expand=True, padx=(20, 0))

        visual_row = ttk.Frame(self.analytics_tab, padding=(6, 0, 6, 12))
        visual_row.pack(fill="x")

        funnel_panel = ttk.LabelFrame(visual_row, text="Application funnel", padding=10)
        funnel_panel.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.funnel_canvas = tk.Canvas(
            funnel_panel,
            height=176,
            background=self.colors["panel"],
            highlightthickness=0,
        )
        self.funnel_canvas.pack(fill="both", expand=True)

        action_panel = ttk.LabelFrame(visual_row, text="Next best moves", padding=10)
        action_panel.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self.action_text = tk.Text(action_panel, height=9, wrap="word")
        self.action_text.pack(fill="both", expand=True)
        self.action_text.configure(
            background=self.colors["panel"], foreground=self.colors["ink"],
            relief="flat", borderwidth=0, padx=10, pady=7,
            font=("Segoe UI", 10), insertbackground=self.colors["ink"],
        )

        body = ttk.Frame(self.analytics_tab, padding=(6, 0, 6, 6))
        body.pack(fill="both", expand=True)

        left = ttk.LabelFrame(body, text="Status / Countries", padding=10)
        right = ttk.LabelFrame(body, text="Skill Intelligence", padding=10)

        left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        right.pack(side="left", fill="both", expand=True, padx=(6, 0))

        status_columns = ("category", "count")
        self.status_table = ttk.Treeview(left, columns=status_columns, show="headings", height=12)
        self.status_table.heading("category", text="STATUS / COUNTRY")
        self.status_table.heading("count", text="JOBS")
        self.status_table.column("category", anchor="w", width=210, stretch=True)
        self.status_table.column("count", anchor="e", width=75, stretch=False)
        self.status_table.pack(fill="both", expand=True)

        skill_columns = ("skill", "required", "missing")
        self.skills_table = ttk.Treeview(right, columns=skill_columns, show="headings", height=12)
        self.skills_table.heading("skill", text="SKILL")
        self.skills_table.heading("required", text="REQUIRED")
        self.skills_table.heading("missing", text="TO BUILD")
        self.skills_table.column("skill", anchor="w", width=220, stretch=True)
        self.skills_table.column("required", anchor="e", width=85, stretch=False)
        self.skills_table.column("missing", anchor="e", width=85, stretch=False)
        self.skills_table.pack(fill="both", expand=True)

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
                tags=(job["status"] or "SAVED",),
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

        for child in self.kpi_frame.winfo_children():
            child.destroy()

        kpis = (
            ("TRACKED", s["total_jobs"], self.colors["ink"]),
            ("APPLIED", s["applied_jobs"], self.colors["teal_dark"]),
            ("INTERVIEWS", s["interviews"], self.colors["green"]),
            ("OFFERS", s["offers"], self.colors["green"]),
            ("RESPONSE RATE", f"{s['response_rate']}%", self.colors["coral"]),
        )
        for title, value, color in kpis:
            card = tk.Frame(self.kpi_frame, bg=self.colors["panel"], padx=13, pady=7, highlightbackground=self.colors["line"], highlightthickness=1)
            card.pack(side="left", fill="x", expand=True, padx=(5, 0))
            tk.Label(card, text=title, bg=self.colors["panel"], fg=self.colors["muted"], font=("Segoe UI", 8, "bold")).pack(anchor="w")
            tk.Label(card, text=value, bg=self.colors["panel"], fg=color, font=("Segoe UI", 16, "bold")).pack(anchor="w")

        self._draw_funnel(s)
        self._write_next_moves(s)

        for item in self.status_table.get_children():
            self.status_table.delete(item)
        for item in self.skills_table.get_children():
            self.skills_table.delete(item)

        for key, value in s["by_status"].items():
            self.status_table.insert("", "end", values=(key, value))

        self.status_table.insert("", "end", values=("COUNTRIES", ""), tags=("section",))
        for key, value in s["by_country"].items():
            self.status_table.insert("", "end", values=(key, value))
        if not s["by_country"]:
            self.status_table.insert("", "end", values=("No country data yet", ""))

        self.status_table.tag_configure("section", foreground=self.colors["teal_dark"], font=("Segoe UI", 9, "bold"))

        required = dict(s["required_skills"][:15])
        missing = dict(s["missing_skills"][:15])
        for skill in sorted(set(required) | set(missing), key=lambda name: (-max(required.get(name, 0), missing.get(name, 0)), name.casefold())):
            self.skills_table.insert("", "end", values=(skill, required.get(skill, ""), missing.get(skill, "")))
        if not required and not missing:
            self.skills_table.insert("", "end", values=("No skill data yet", "", ""))

    def _draw_funnel(self, summary):
        canvas = self.funnel_canvas
        canvas.delete("all")
        canvas.update_idletasks()
        width = max(canvas.winfo_width(), 420)
        stages = (
            ("Tracked", summary["total_jobs"], self.colors["ink"]),
            ("Applied", summary["applied_jobs"], self.colors["teal"]),
            ("Interviews", summary["interviews"], self.colors["green"]),
            ("Offers", summary["offers"], self.colors["coral"]),
        )
        max_value = max((value for _, value, _ in stages), default=1) or 1
        left = 102
        right = width - 28
        bar_width = max(right - left, 160)
        for index, (label, value, color) in enumerate(stages):
            y = 17 + index * 38
            canvas.create_text(0, y + 10, text=label, anchor="w", fill=self.colors["muted"], font=("Segoe UI", 9, "bold"))
            canvas.create_rectangle(left, y, right, y + 20, fill="#E8EEF5", outline="")
            filled = max(8, bar_width * value / max_value) if value else 0
            if filled:
                canvas.create_rectangle(left, y, left + filled, y + 20, fill=color, outline="")
            canvas.create_text(right + 2, y + 10, text=str(value), anchor="e", fill=self.colors["ink"], font=("Segoe UI", 10, "bold"))

    def _write_next_moves(self, summary):
        moves = []
        if not summary["total_jobs"]:
            moves.append("Add your first target job to start the funnel.")
        elif not summary["applied_jobs"]:
            moves.append("Choose your strongest saved job and submit the first application.")
        elif summary["response_rate"] < 15:
            moves.append("Response rate is low. Review CV versions and tailor the next 3 applications.")
        else:
            moves.append("Keep the pipeline moving: follow up on active applications this week.")

        if summary["missing_skills"]:
            skill, count = summary["missing_skills"][0]
            moves.append(f"Build evidence for {skill}; it appears in {count} tracked job brief(s).")
        if summary["average_match"] is not None and summary["average_match"] < 60:
            moves.append("Average match is below 60. Focus searches on roles closer to your strongest skills.")
        if len(moves) < 3:
            moves.append("Log each outcome promptly so the funnel stays useful.")

        self.action_text.delete("1.0", "end")
        self.action_text.insert("1.0", "\n".join(f"{index}. {move}" for index, move in enumerate(moves[:3], start=1)))

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
