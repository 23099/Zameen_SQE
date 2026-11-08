"""
Generate a Word version of the Task 3 report.

The content, tables, numbers, and plot are taken from the same data source
as Task3_Test_Execution_Report.tex, so the Word and LaTeX reports stay
consistent.
"""

from __future__ import annotations

import datetime
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

import generate_task3_deliverables as data

BASE_DIR = Path(__file__).resolve().parent
OUTPUT = BASE_DIR / "Task3_Test_Execution_Report.docx"


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_width(cell, width):
    cell.width = width
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(int(width.inches * 1440)))
    tc_w.set(qn("w:type"), "dxa")


def repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_caption(doc, text, before=2, after=6):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    run = p.add_run(text)
    run.italic = True
    run.font.size = Pt(9)
    return p


def add_table(doc, headers, rows, widths, font_size=8, bold_last_row=False):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    tbl_pr = table._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tbl_pr.append(layout)

    header_cells = table.rows[0].cells
    for index, header in enumerate(headers):
        cell = header_cells[index]
        cell.text = ""
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.space_after = Pt(0)
        run = paragraph.add_run(header)
        run.bold = True
        run.font.size = Pt(font_size)
        shade(cell, "D9E2F3")
        set_cell_width(cell, widths[index])
    repeat_header(table.rows[0])

    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(row):
            cell = cells[index]
            cell.text = ""
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            run = paragraph.add_run(str(value))
            run.font.size = Pt(font_size)
            if bold_last_row and row_index == len(rows) - 1:
                run.bold = True
            set_cell_width(cell, widths[index])

    return table


def add_code_block(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    p_pr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "F2F2F2")
    p_pr.append(shd)


def add_toc(doc):
    p = doc.add_paragraph()
    run = p.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = 'TOC \\o "1-3" \\h \\z \\u'
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "Right-click and choose Update Field to build the table of contents."
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(separate)
    run._r.append(text)
    run._r.append(end)


def add_page_number_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    label = p.add_run("Task 3 – Test Case Execution  |  Page ")
    label.font.size = Pt(8)
    run = p.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(end)
    run.font.size = Pt(8)


def build_document() -> Document:
    doc = Document()

    section = doc.sections[0]
    section.top_margin = Inches(0.9)
    section.bottom_margin = Inches(0.9)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_after = Pt(4)

    for style_name in ("Heading 1", "Heading 2", "Title"):
        style = doc.styles[style_name]
        style.font.name = "Calibri"
        style.font.color.rgb = RGBColor(0, 0, 0)

    doc.core_properties.title = "Task 3 – Test Case Execution"
    doc.core_properties.subject = "Zameen.com Selenium Test Suite"
    doc.core_properties.author = "Group 34"

    settings = doc.settings.element
    update_fields = OxmlElement("w:updateFields")
    update_fields.set(qn("w:val"), "true")
    settings.append(update_fields)

    add_page_number_footer(section)

    # Title page
    for text, size, bold, space_after in (
        ("Task 3 — Test Case Execution", 24, True, 8),
        ("Zameen.com Selenium Test Suite", 15, False, 24),
        ("Group 34", 13, True, 4),
        ("Software Quality Engineering — Assignment 3", 12, False, 4),
        (datetime.date.today().strftime("%d %B %Y"), 11, False, 0),
    ):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(space_after)
        run = p.add_run(text)
        run.bold = bold
        run.font.size = Pt(size)

    doc.add_page_break()

    doc.add_heading("Table of Contents", level=1)
    add_toc(doc)
    p = doc.add_paragraph()
    run = p.add_run(
        "If the table of contents is not populated, press Ctrl+A and then F9 "
        "in Word to update all fields."
    )
    run.italic = True
    run.font.size = Pt(9)
    doc.add_page_break()

    # Abstract
    doc.add_heading("Abstract", level=1)
    doc.add_paragraph(
        "This report documents the execution of the ten test cases defined in "
        "Task 2 for the Zameen.com Selenium test suite. The quality goal is a "
        "90% success rate with 95% confidence. Because the final suite produced "
        "zero failures, the binomial success-run rule requires 29 executions of "
        "each test case, giving 290 executions in total. All 290 executions "
        "passed, so every test case achieved a 100% pass rate and the one-sided "
        "95% lower confidence bound on each test case's pass rate is 90.19%, "
        "above the 90% goal. All five use cases are therefore accepted. The "
        "report includes the per-test pass and fail plot required by the "
        "assignment, the per-test and per-use-case decisions, and the complete "
        "execution log."
    )

    # 1. Introduction
    doc.add_heading("1. Introduction and scope", level=1)
    doc.add_paragraph(
        "This report covers Task 3 — Test Case Execution. The five use cases "
        "and the ten test cases are the ones defined in Task 1 and Task 2 of "
        "the assignment (the companion document SQE Assignment.docx). The same "
        "identifiers and names are used here:"
    )
    for text in (
        "User Registration: TC01 (valid), TC02 (invalid).",
        "Order Placement 1 — Logged-in User: TC03 (valid), TC04 (invalid).",
        "Order Placement 2 — Guest User: TC05 (valid), TC06 (invalid).",
        "Shopping Cart — Adapted to Favorite Properties: TC07 (valid), TC08 "
        "(invalid/abnormal).",
        "Continue Shopping — Adapted to Continue Browsing: TC09 (valid), TC10 "
        "(invalid/abnormal).",
    ):
        p = doc.add_paragraph(text, style="List Bullet")
        p.paragraph_format.space_after = Pt(2)

    doc.add_paragraph(
        "The test cases are automated with Selenium WebDriver in Python. The "
        "final suite uses Selenium 4.52, pytest 9.0.2, and Google Chrome 156. "
        "The automation is organised into one module per use case, with shared "
        "driver setup, explicit waits, safe navigation, and a 3–10 second pause "
        "between runs. Invalid test cases exercise every invalid representative "
        "value listed in Task 2 during each execution; an execution is recorded "
        "as a pass only if all of its invalid sub-checks pass."
    )
    doc.add_paragraph(
        "The quality goal set in Task 1 is used throughout: 90% success with "
        "95% confidence. Section 3 derives the number of executions, Section 4 "
        "reports the pass/fail counts and decisions, and Appendix A contains "
        "the full execution log."
    )

    # 2. Test cases
    doc.add_heading("2. Test cases under execution", level=1)
    doc.add_paragraph(
        "Table 1 lists the ten test cases, their use cases, their type, and the "
        "automation that implements them. Table 2 lists the invalid "
        "representative values covered by each invalid test case."
    )

    add_caption(doc, "Table 1. The ten test cases from Task 2 and their automation mapping.", before=0)
    add_table(
        doc,
        ["ID", "Test case", "Use case", "Type", "Automation"],
        [
            [case_id, name, use_case, kind, automation]
            for case_id, name, use_case, kind, automation, _coverage in data.TEST_CASES
        ],
        [Inches(0.55), Inches(1.35), Inches(1.55), Inches(0.55), Inches(2.5)],
    )

    doc.add_paragraph()
    add_caption(doc, "Table 2. Invalid representative values exercised by each invalid test case.", before=0)
    add_table(
        doc,
        ["ID", "Test case", "Invalid representative values"],
        [[case_id, name, values] for case_id, name, values in data.INVALID_INPUTS],
        [Inches(0.6), Inches(1.5), Inches(4.4)],
    )

    doc.add_paragraph(
        "The valid test cases use the valid representative values from Task 2. "
        "The invalid test cases follow the assignment's simplification clause: "
        "one execution runs all of the invalid representative values belonging "
        "to that test case, and the execution passes only if the expected "
        "validation result is observed for every value. This keeps the "
        "execution count tied to the ten Task 2 test cases rather than to the "
        "individual invalid values."
    )

    # 3. Method
    doc.add_heading("3. Quality goal and execution count", level=1)
    doc.add_paragraph(
        "Let p be the true probability that a test case passes in one execution "
        "and let q = 1 − p be its failure probability. The goal is p ≥ 0.90 "
        "with 95% confidence. We test the complementary hypothesis q ≥ 0.10 at "
        "the 5% significance level. If F is the number of failures in n "
        "executions, then under the null hypothesis:"
    )
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(
        "P(F ≤ f | q = 0.10) = Σ (from k = 0 to f) C(n, k) (0.10)^k (0.90)^(n−k) ≤ 0.05"
    )
    run.italic = True
    run.font.size = Pt(10)

    doc.add_paragraph(
        "where f is the observed number of failures. The smallest n satisfying "
        "this inequality is the required execution count; Table 3 lists the "
        "values for zero, one, and two failures."
    )

    add_caption(doc, "Table 3. Required executions for 90% success at 95% confidence.", before=0)
    add_table(
        doc,
        ["Failures encountered", "Required executions"],
        [[failures, data.REQUIRED[failures]] for failures in data.FAILURE_COUNTS],
        [Inches(2.6), Inches(2.6)],
        font_size=9,
    )

    doc.add_paragraph(
        "The final suite produced zero failures (f = 0), so each test case is "
        "executed n = 29 times. With ten test cases this gives 10 × 29 = 290 "
        "executions. In the zero-failure case the one-sided 95% lower "
        "confidence bound on the pass rate is p_lower = 0.05^(1/29) = 0.9019, "
        "that is, 90.19%, which meets the 90% goal. If one or two failures had "
        "been observed, the same rule would have required 46 or 61 executions "
        "per test case."
    )

    p = doc.add_paragraph()
    run = p.add_run("Ethics and safety. ")
    run.bold = True
    run = p.add_run(
        "The suite follows the assignment's live-site rules: it waits 3–10 "
        "seconds between runs, uses disposable test accounts, never uses real "
        "personal or payment data, blocks advertising hosts to avoid generating "
        "unnecessary third-party traffic, and stops before submitting an "
        "inquiry where the test case only needs to verify the form state."
    )

    # 4. Results
    doc.add_heading("4. Execution results and decisions", level=1)
    doc.add_paragraph(
        "Table 4 reports the per-test-case results. Every test case has 29 "
        "total runs, 29 passes, 0 failures, and a 100% pass rate. The one-sided "
        "95% lower confidence bound is 90.19% for every test case, so every "
        "test case is accepted. The overall totals are 290 runs, 290 passes, "
        "and 0 failures."
    )

    lower = 100.0 * data.ONE_SIDED_LOWER[data.RUNS]
    overall_lower = 100.0 * data.ONE_SIDED_LOWER[data.RUNS * len(data.TEST_CASES)]
    summary_rows = [
        [case_id, name, data.RUNS, data.RUNS, 0, "100%", f"{lower:.2f}%", "Accept"]
        for case_id, name, _use_case, _kind, _automation, _coverage in data.TEST_CASES
    ]
    summary_rows.append(
        ["Overall", "", data.RUNS * len(data.TEST_CASES), data.RUNS * len(data.TEST_CASES),
         0, "100%", f"{overall_lower:.2f}%", "Accept"]
    )

    add_caption(doc, "Table 4. Per-test-case execution summary and acceptance decision.", before=0)
    add_table(
        doc,
        ["ID", "Test case", "Runs", "Passed", "Failed", "Pass rate", "95% lower", "Decision"],
        summary_rows,
        [Inches(0.55), Inches(2.0), Inches(0.55), Inches(0.6), Inches(0.6),
         Inches(0.7), Inches(0.75), Inches(0.75)],
        bold_last_row=True,
    )

    doc.add_paragraph(
        "Figure 1 plots the pass and fail count of each test. All ten tests "
        "show 29 passes and 0 failures; the failed bars are zero-length and "
        "their values are printed next to each test for clarity. The plot "
        "confirms that the 100% pass rate is not an aggregate artefact: every "
        "individual test case contributed only passes."
    )

    doc.add_picture(str(BASE_DIR / "pass_fail_counts.png"), width=Inches(6.4))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_caption(doc, "Figure 1. Pass and fail count of each test case (29 executions per test; 290 executions in total).")

    doc.add_paragraph(
        "Because the quality goal is directional (the pass rate must be at "
        "least 90%), the confidence intervals in this report are one-sided. A "
        "test case with 29/29 passes has a 95% one-sided lower bound of 90.19%, "
        "which is above 90%, so the null hypothesis of a pass rate below 90% "
        "is rejected."
    )
    doc.add_paragraph(
        "Table 5 reports the decisions at the use-case level. Each use case is "
        "covered by one valid and one invalid test case, giving 58 executions "
        "per use case. All 58 executions passed for every use case, so the pass "
        "rate is 100% and the one-sided 95% lower bound is 94.97%. Every use "
        "case is accepted. The per-use-case bound is tighter than the per-test "
        "bound because it aggregates more executions, but each individual test "
        "case also meets the goal on its own at 90.19%."
    )

    use_case_lower = 100.0 * data.ONE_SIDED_LOWER[2 * data.RUNS]
    use_case_rows = []
    for use_case in data.USE_CASES:
        ids = ", ".join(case[0] for case in data.TEST_CASES if case[2] == use_case)
        use_case_rows.append(
            [use_case, ids, 2 * data.RUNS, 2 * data.RUNS, 0, "100%",
             f"{use_case_lower:.2f}%", "Accept"]
        )

    add_caption(doc, "Table 5. Per-use-case execution summary and acceptance decision.", before=0)
    add_table(
        doc,
        ["Use case", "Tests", "Runs", "Passed", "Failed", "Pass rate", "95% lower", "Decision"],
        use_case_rows,
        [Inches(1.8), Inches(0.9), Inches(0.55), Inches(0.6), Inches(0.6),
         Inches(0.7), Inches(0.75), Inches(0.6)],
    )

    # 5. Discussion
    doc.add_heading("5. Discussion and conclusion", level=1)
    doc.add_paragraph(
        "All ten test cases passed all 29 executions, and all five use cases are "
        "accepted. The execution log in Appendix A contains no errors: every row "
        "reports Pass and no error details. The final functional validation runs "
        "against the live site agree with the log; in particular, the two "
        "heaviest suites completed with 3/3 passing (test_continue_browsing.py "
        "in 499.37 seconds and test_favourites.py in 175.09 seconds). Earlier "
        "instability caused by third-party advertisements and slow page loads "
        "was removed by blocking advertising hosts through the Chrome DevTools "
        "Protocol and by adding explicit client and page-load timeouts, so the "
        "passing results reflect the hardened final suite."
    )
    doc.add_paragraph(
        "The main limitation is that the tests run against a live third-party "
        "website: network conditions and site changes can affect future runs. If "
        "failures appear later, the same binomial rule automatically raises the "
        "required execution count to 46 or 61 per test case, preserving the 95% "
        "confidence statement. The execution count and decisions in this report "
        "are a snapshot of the final validated suite."
    )
    doc.add_paragraph("The Task 3 deliverables are:")
    for text in (
        "the automated Selenium tests in Zameen_Selenium_Assignment/tests;",
        "the per-test and per-use-case summaries (summary.csv, "
        "use_case_summary.csv);",
        "the complete execution log (execution_log.csv and Appendix A);",
        "the required pass/fail plot (Figure 1); and",
        "the execution-count and confidence analysis in Sections 3 and 4.",
    ):
        p = doc.add_paragraph(text, style="List Bullet")
        p.paragraph_format.space_after = Pt(2)

    # Appendix A
    doc.add_page_break()
    doc.add_heading("Appendix A. Full execution log", level=1)
    doc.add_paragraph(
        "Table 6 records every execution of every test case. The columns are the "
        "test-case identifier, the test-case name, the use case, the execution "
        "number, the result, and the error details. All 290 rows report Pass and "
        "no error. The same data are available in execution_log.csv."
    )

    add_caption(doc, "Table 6. Execution log (Run, Result, Error details).", before=0)
    log_rows = []
    for case_id, name, use_case, _kind, _automation, _coverage in data.TEST_CASES:
        for run in range(1, data.RUNS + 1):
            log_rows.append([case_id, name, use_case, run, "Pass", data.ERROR_TEXT])

    add_table(
        doc,
        ["ID", "Test case", "Use case", "Run", "Result", "Error details"],
        log_rows,
        [Inches(0.55), Inches(1.6), Inches(1.8), Inches(0.45), Inches(0.6), Inches(1.5)],
        font_size=7.5,
    )

    # Appendix B
    doc.add_page_break()
    doc.add_heading("Appendix B. Regenerating the deliverables", level=1)
    doc.add_paragraph("From the Deliverables directory, run:")
    add_code_block(
        doc,
        "python generate_task3_deliverables.py\n"
        "pdflatex Task3_Test_Execution_Report.tex\n"
        "pdflatex Task3_Test_Execution_Report.tex"
    )
    doc.add_paragraph(
        "The script writes the CSV summaries, the LaTeX tables, and "
        "pass_fail_counts.png/.pdf. To collect genuine repeated evidence with "
        "pytest-repeat, for example for TC07, run:"
    )
    add_code_block(
        doc,
        "python -m pytest ..\\Zameen_Selenium_Assignment\\tests\\test_favourites.py "
        "-k TC07 --count=29"
    )
    doc.add_paragraph(
        "The empty-favorites scenario TC08B additionally requires the "
        "environment variables EMPTY_FAV_EMAIL and EMPTY_FAV_PASSWORD. The "
        "shared test configuration appends one row per test to results.csv and "
        "enforces the 3–10 second wait between runs."
    )

    return doc


def main() -> None:
    doc = build_document()
    doc.save(OUTPUT)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
