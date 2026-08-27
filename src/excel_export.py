"""
Tiny dependency-free XLSX exporter.

This intentionally supports only the small subset Career OS needs:
plain values, multiple sheets, and basic column widths. It uses only
the Python standard library so Career OS has zero external dependencies.
"""

from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED

from src.analytics import get_summary
from src.database import get_connection


def _col_letter(index):
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _cell_xml(row, col, value, style=0):
    ref = f"{_col_letter(col)}{row}"
    style_xml = f' s="{style}"' if style else ""

    if value is None:
        value = ""

    if isinstance(value, bool):
        return f'<c r="{ref}"{style_xml} t="b"><v>{1 if value else 0}</v></c>'

    if isinstance(value, (int, float)):
        return f'<c r="{ref}"{style_xml}><v>{value}</v></c>'

    text = escape(str(value))
    return (
        f'<c r="{ref}"{style_xml} t="inlineStr">'
        f'<is><t xml:space="preserve">{text}</t></is></c>'
    )


def _sheet_xml(rows, widths=None, sheet_name=""):
    max_cols = max((len(row) for row in rows), default=1)

    cols_xml = ""
    if widths:
        cols = []
        for index, width in enumerate(widths, start=1):
            cols.append(
                f'<col min="{index}" max="{index}" width="{width}" customWidth="1"/>'
            )
        cols_xml = f"<cols>{''.join(cols)}</cols>"

    sheet_rows = []
    today = datetime.now().date()
    for r_index, row in enumerate(rows, start=1):
        cells = []
        for c_index, value in enumerate(row, start=1):
            style = 1 if r_index == 1 else 0
            if sheet_name == "Jobs" and r_index > 1:
                if c_index == 11 and value:
                    try:
                        days = (datetime.strptime(str(value), "%Y-%m-%d").date() - today).days
                        style = 2 if days < 0 else 3 if days <= 7 else 0
                    except ValueError:
                        pass
                elif c_index == 8:
                    style = {"OFFER": 4, "INTERVIEW": 5, "REJECTED": 6}.get(str(value), 0)
            cells.append(_cell_xml(r_index, c_index, value, style))
        sheet_rows.append(f'<row r="{r_index}">{"".join(cells)}</row>')

    dimension = f"A1:{_col_letter(max_cols)}{max(len(rows), 1)}"

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <dimension ref="{dimension}"/>
        {cols_xml}
    <sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/><selection pane="bottomLeft" activeCell="A2" sqref="A2"/></sheetView></sheetViews>
  <sheetData>
    {''.join(sheet_rows)}
  </sheetData>
</worksheet>
'''


def _styles_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
 <numFmts count="0"/>
 <fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Calibri"/></font></fonts>
 <fills count="5"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF087F8C"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFFE699"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFFC7CE"/><bgColor indexed="64"/></patternFill></fill></fills>
 <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
 <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
 <cellXfs count="7"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" applyAlignment="1"><alignment horizontal="center"/></xf><xf numFmtId="0" fontId="0" fillId="4" borderId="0"/><xf numFmtId="0" fontId="0" fillId="3" borderId="0"/><xf numFmtId="0" fontId="0" fillId="3" borderId="0"/><xf numFmtId="0" fontId="0" fillId="2" borderId="0"/><xf numFmtId="0" fontId="0" fillId="4" borderId="0"/></cellXfs>
 <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>
'''


def _workbook_xml(sheet_names):
    sheets = []

    for index, name in enumerate(sheet_names, start=1):
        sheets.append(
            f'<sheet name="{escape(name)}" sheetId="{index}" r:id="rId{index}"/>'
        )

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
 <sheets>{''.join(sheets)}</sheets>
</workbook>
'''


def _workbook_rels(sheet_count):
    rels = []

    for index in range(1, sheet_count + 1):
        rels.append(
            f'<Relationship Id="rId{index}" '
            f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{index}.xml"/>'
        )

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
{''.join(rels)}
</Relationships>
'''


def _content_types(sheet_count):
    overrides = [
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    ]

    for index in range(1, sheet_count + 1):
        overrides.append(
            f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
            f'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="xml" ContentType="application/xml"/>
 {''.join(overrides)}
</Types>
'''


ROOT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1"
  Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
  Target="xl/workbook.xml"/>
</Relationships>
'''


def _load_export_data():
    connection = get_connection()

    jobs = connection.execute(
        """
        SELECT id, company, role, country, city, match_score, eligibility,
               status, date_found, date_applied, deadline, salary,
               required_skills, missing_skills, cv_version,
               cover_letter, url, notes
        FROM jobs
        ORDER BY id
        """
    ).fetchall()

    skills = connection.execute(
        """
        SELECT s.name, js.skill_type, COUNT(*) AS frequency
        FROM job_skills js
        JOIN skills s ON s.id = js.skill_id
        GROUP BY s.name, js.skill_type
        ORDER BY frequency DESC, s.name
        """
    ).fetchall()

    connection.close()

    summary = get_summary()

    job_headers = [
        "ID",
        "Company",
        "Role",
        "Country",
        "City",
        "Match Score",
        "Eligibility",
        "Status",
        "Date Found",
        "Date Applied",
        "Deadline",
        "Salary",
        "Required Skills",
        "Missing Skills",
        "CV Version",
        "Cover Letter",
        "URL",
        "Notes",
    ]

    jobs_rows = [job_headers]

    for row in jobs:
        jobs_rows.append([
            row["id"],
            row["company"],
            row["role"],
            row["country"],
            row["city"],
            row["match_score"],
            row["eligibility"],
            row["status"],
            row["date_found"],
            row["date_applied"],
            row["deadline"],
            row["salary"],
            row["required_skills"],
            row["missing_skills"],
            row["cv_version"],
            "Yes" if row["cover_letter"] else "No",
            row["url"],
            row["notes"],
        ])

    skills_rows = [["Skill", "Type", "Frequency"]]

    for row in skills:
        skills_rows.append([
            row["name"],
            row["skill_type"],
            row["frequency"],
        ])

    analytics_rows = [
        ["Metric", "Value"],
        ["Jobs tracked", summary["total_jobs"]],
        ["Applications", summary["applied_jobs"]],
        ["Interviews", summary["interviews"]],
        ["Offers", summary["offers"]],
        ["Interview rate (%)", summary["response_rate"]],
        ["Offer rate (%)", summary["offer_rate"]],
        ["Average match", summary["average_match"] or ""],
        [],
        ["Status", "Count"],
    ]

    analytics_rows.extend([
        [key, value]
        for key, value in summary["by_status"].items()
    ])

    analytics_rows.extend([
        [],
        ["Country", "Count"],
    ])

    analytics_rows.extend([
        [key, value]
        for key, value in summary["by_country"].items()
    ])

    return {
        "Jobs": (
            jobs_rows,
            [
                6, 22, 38, 16, 16, 12, 12, 12, 14,
                14, 14, 16, 30, 30, 18, 12, 45, 45
            ],
        ),
        "Skills": (
            skills_rows,
            [28, 14, 12],
        ),
        "Analytics": (
            analytics_rows,
            [28, 18],
        ),
    }


def export_to_excel(output_path=None):
    # If no custom path is supplied, always save Career OS exports
    # inside the user's permanent CareerOS folder.
    if output_path is None:
        export_dir = Path.home() / "CareerOS" / "exports"

        export_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output_path = (
            export_dir
            / f"career_tracker_{stamp}.xlsx"
        )

    else:
        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    sheets = _load_export_data()
    names = list(sheets)

    with ZipFile(output_path, "w", ZIP_DEFLATED) as xlsx:

        xlsx.writestr(
            "[Content_Types].xml",
            _content_types(len(names)),
        )

        xlsx.writestr(
            "_rels/.rels",
            ROOT_RELS,
        )

        xlsx.writestr(
            "xl/workbook.xml",
            _workbook_xml(names),
        )

        xlsx.writestr("xl/styles.xml", _styles_xml())

        xlsx.writestr(
            "xl/_rels/workbook.xml.rels",
            _workbook_rels(len(names)),
        )

        for index, name in enumerate(names, start=1):
            rows, widths = sheets[name]

            xlsx.writestr(
                f"xl/worksheets/sheet{index}.xml",
                _sheet_xml(rows, widths, name),
            )

    return output_path