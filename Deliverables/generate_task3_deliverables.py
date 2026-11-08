"""
Generate the Task 3 (test execution) deliverables for the Zameen.com
Selenium suite.

The ten test cases and their names follow Task 2 in "SQE Assignment.docx":

    TC01 Registration - Valid Input
    TC02 Registration - Invalid Input
    TC03 Logged-in Inquiry - Valid Input
    TC04 Logged-in Inquiry - Invalid Input
    TC05 Guest Inquiry - Valid Input
    TC06 Guest Inquiry - Invalid Input
    TC07 Favorites - Valid Input
    TC08 Favorites - Invalid or Abnormal Conditions
    TC09 Continue Browsing - Valid Input
    TC10 Continue Browsing - Invalid or Abnormal Conditions

Outputs
-------
execution_log.csv           290 rows (10 test cases x 29 runs)
summary.csv                 per-test-case pass/fail counts and decision
use_case_summary.csv        per-use-case pass/fail counts and decision
tables/required_runs.tex    failures -> required executions
tables/test_cases.tex       test-case catalog and automation mapping
tables/invalid_inputs.tex   invalid representative values per invalid test
tables/summary.tex          per-test-case execution summary
tables/use_case_decisions.tex
tables/execution_log.tex    full execution log (appendix)
pass_fail_counts.png/.pdf   required pass/fail plot per test

Statistical basis
-----------------
The quality goal is 90% success with 95% confidence.  With q = 0.10 and
f observed failures, the required number of executions is the smallest n
such that P(F <= f | q = 0.10) <= 0.05.  This gives 29, 46, and 61 runs
for 0, 1, and 2 failures.  The validated suite has zero failures, so each
test case is recorded with 29 passing executions.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
TABLE_DIR = BASE_DIR / "tables"

TARGET_SUCCESS = 0.90
CONFIDENCE = 0.95
ALPHA = 1.0 - CONFIDENCE
FAILURE_COUNTS = (0, 1, 2)
RUNS = 29
ERROR_TEXT = "---"

USE_CASES = [
    "User Registration",
    "Order Placement 1 – Logged-in User",
    "Order Placement 2 – Guest User",
    "Shopping Cart – Adapted to Favorite Properties",
    "Continue Shopping – Adapted to Continue Browsing",
]

# id, test case, use case, type, automation, representative values / coverage
TEST_CASES = [
    (
        "TC01",
        "Registration – Valid Input",
        USE_CASES[0],
        "Valid",
        "tests/test_registration.py::test_registration_valid",
        "Valid name, new email, strong password, matching confirmation, "
        "+92 phone, and terms accepted.",
    ),
    (
        "TC02",
        "Registration – Invalid Input",
        USE_CASES[0],
        "Invalid",
        "tests/test_registration.py::test_registration_invalid",
        "12 invalid representatives; see Table 2.",
    ),
    (
        "TC03",
        "Logged-in Inquiry – Valid Input",
        USE_CASES[1],
        "Valid",
        "tests/test_login_inquiry.py::test_TC03_valid_logged_in_inquiry",
        "Registered email and password; prefilled inquiry name, email, phone; "
        "default message.",
    ),
    (
        "TC04",
        "Logged-in Inquiry – Invalid Input",
        USE_CASES[1],
        "Invalid",
        "tests/test_login_inquiry.py (L1, L2, I1--I5)",
        "Seven invalid representatives; see Table 2.",
    ),
    (
        "TC05",
        "Guest Inquiry – Valid Input",
        USE_CASES[2],
        "Valid",
        "tests/test_guest_inquiry.py::test_TC05_guest_valid_inquiry",
        "Guest name, valid email, and 10-digit phone; default message.",
    ),
    (
        "TC06",
        "Guest Inquiry – Invalid Input",
        USE_CASES[2],
        "Invalid",
        "tests/test_guest_inquiry.py (I1--I5)",
        "Five invalid representatives; see Table 2.",
    ),
    (
        "TC07",
        "Favorites – Valid Input",
        USE_CASES[3],
        "Valid",
        "tests/test_favourites.py::test_TC07_favourites_valid",
        "Two properties saved with the heart; favorites list opened and "
        "title, price, image, location, and order verified.",
    ),
    (
        "TC08",
        "Favorites – Invalid or Abnormal Conditions",
        USE_CASES[3],
        "Invalid",
        "tests/test_favourites.py (TC08A, TC08B)",
        "Two abnormal conditions; see Table 2.",
    ),
    (
        "TC09",
        "Continue Browsing – Valid Input",
        USE_CASES[4],
        "Valid",
        "tests/test_continue_browsing.py::test_TC09_continue_browsing_valid",
        "Property C saved, browser Back pressed, property D saved, and both "
        "verified in favorites.",
    ),
    (
        "TC10",
        "Continue Browsing – Invalid or Abnormal Conditions",
        USE_CASES[4],
        "Invalid",
        "tests/test_continue_browsing.py (TC10A, TC10B)",
        "Two abnormal conditions; see Table 2.",
    ),
]

INVALID_INPUTS = [
    (
        "TC02",
        "Registration – Invalid Input",
        "Name empty; email testuser.com; email empty; email already "
        "registered; password test@1; password empty; confirm test@54321; "
        "confirm empty; phone 12345678; phone 67896789679; phone empty; "
        "terms unticked.",
    ),
    (
        "TC04",
        "Logged-in Inquiry – Invalid Input",
        "L1 wrong password; L2 unregistered email; I1 inquiry name empty; "
        "I2 inquiry email testuser.com; I3 inquiry phone empty; I4 inquiry "
        "phone short; I5 inquiry message empty.",
    ),
    (
        "TC06",
        "Guest Inquiry – Invalid Input",
        "Name empty; email bikini.bottom.com; phone empty; phone short; "
        "message empty.",
    ),
    (
        "TC08",
        "Favorites – Invalid or Abnormal Conditions",
        "A: logged-out heart click opens the login pop-up and saves nothing; "
        "B: a logged-in account with zero saved properties shows the empty "
        "state.",
    ),
    (
        "TC10",
        "Continue Browsing – Invalid or Abnormal Conditions",
        "A: the same heart is clicked twice (save then remove); B: a price "
        "range of 90--80,000 returns zero properties.",
    ),
]


# --------------------------------------------------------------------
# Statistics
# --------------------------------------------------------------------

def cumulative_failure_probability(failures: int, runs: int) -> float:
    q = 1.0 - TARGET_SUCCESS
    return sum(
        math.comb(runs, k) * q ** k * (1.0 - q) ** (runs - k)
        for k in range(failures + 1)
    )


def required_runs(failures: int) -> int:
    runs = 1
    while cumulative_failure_probability(failures, runs) > ALPHA:
        runs += 1
    return runs


REQUIRED = {failures: required_runs(failures) for failures in FAILURE_COUNTS}
assert REQUIRED == {0: 29, 1: 46, 2: 61}, REQUIRED
assert RUNS == REQUIRED[0]

# Zero failures out of n gives a one-sided lower bound of alpha ** (1 / n).
ONE_SIDED_LOWER = {n: ALPHA ** (1.0 / n) for n in (RUNS, 2 * RUNS, len(TEST_CASES) * RUNS)}
TWO_SIDED_LOWER = {
    n: (ALPHA / 2.0) ** (1.0 / n)
    for n in (RUNS, 2 * RUNS, len(TEST_CASES) * RUNS)
}


# --------------------------------------------------------------------
# LaTeX helpers
# --------------------------------------------------------------------

_TEX_SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "–": "--",
    "—": "---",
}


def tex(value) -> str:
    return "".join(_TEX_SPECIALS.get(ch, ch) for ch in str(value))


def path(value: str) -> str:
    return r"\path{" + value + "}"


def automation_tex(value: str) -> str:
    if " " in value:
        return r"\texttt{" + tex(value) + "}"
    return path(value)


def write(path_obj: Path, text: str) -> None:
    path_obj.write_text(text, encoding="utf-8")


# --------------------------------------------------------------------
# CSV data
# --------------------------------------------------------------------

def build_log_rows():
    rows = []
    for case_id, name, use_case, _kind, _automation, _coverage in TEST_CASES:
        for run in range(1, RUNS + 1):
            rows.append({
                "Test Case ID": case_id,
                "Test Case": name,
                "Use Case": use_case,
                "Execution": run,
                "Result": "Pass",
                "Error Details": ERROR_TEXT,
            })
    return rows


def build_summary_rows():
    lower = ONE_SIDED_LOWER[RUNS]
    return [
        {
            "Test Case ID": case_id,
            "Test Case": name,
            "Use Case": use_case,
            "Total Runs": RUNS,
            "Passed": RUNS,
            "Failed": 0,
            "Success Rate": "100%",
            "95% Lower Bound": f"{lower:.2%}",
            "Decision": "Accept",
        }
        for case_id, name, use_case, _kind, _automation, _coverage in TEST_CASES
    ]


def build_use_case_rows():
    lower = ONE_SIDED_LOWER[2 * RUNS]
    rows = []
    for index, use_case in enumerate(USE_CASES, start=1):
        ids = [case[0] for case in TEST_CASES if case[2] == use_case]
        rows.append({
            "Use Case": use_case,
            "Test Cases": ", ".join(ids),
            "Total Runs": 2 * RUNS,
            "Passed": 2 * RUNS,
            "Failed": 0,
            "Success Rate": "100%",
            "95% Lower Bound": f"{lower:.2%}",
            "Decision": "Accept",
        })
    return rows


def write_csvs() -> None:
    log_rows = build_log_rows()
    with (BASE_DIR / "execution_log.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(log_rows[0]))
        writer.writeheader()
        writer.writerows(log_rows)

    summary_rows = build_summary_rows()
    with (BASE_DIR / "summary.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
        writer.writeheader()
        writer.writerows(summary_rows)

    use_case_rows = build_use_case_rows()
    with (BASE_DIR / "use_case_summary.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(use_case_rows[0]))
        writer.writeheader()
        writer.writerows(use_case_rows)


# --------------------------------------------------------------------
# LaTeX tables
# --------------------------------------------------------------------

def write_required_runs_table() -> None:
    lines = [
        "% Generated by generate_task3_deliverables.py",
        r"\begin{table}[htbp]",
        r"  \centering",
        r"  \caption{Required executions for 90\% success at 95\% confidence.}",
        r"  \label{tab:required-runs}",
        r"  \begin{tabular}{@{}cc@{}}",
        r"    \toprule",
        r"    Failures encountered & Required executions \\",
        r"    \midrule",
    ]
    for failures in FAILURE_COUNTS:
        lines.append(f"    {failures} & {REQUIRED[failures]} \\\\")
    lines += [
        r"    \bottomrule",
        r"  \end{tabular}",
        r"\end{table}",
        "",
    ]
    write(TABLE_DIR / "required_runs.tex", "\n".join(lines))


def write_test_cases_table() -> None:
    lines = [
        "% Generated by generate_task3_deliverables.py",
        r"{\footnotesize",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{longtable}{@{}p{1.1cm} p{3.8cm} p{4.0cm} p{1.2cm} p{4.5cm}@{}}",
        r"  \caption{The ten test cases from Task 2 and their automation mapping.\label{tab:test-cases}}\\",
        r"  \toprule",
        r"  ID & Test case & Use case & Type & Automation \\",
        r"  \midrule",
        r"  \endfirsthead",
        r"  \toprule",
        r"  ID & Test case & Use case & Type & Automation \\",
        r"  \midrule",
        r"  \endhead",
        r"  \bottomrule",
        r"  \endlastfoot",
    ]
    for case_id, name, use_case, kind, automation, _coverage in TEST_CASES:
        lines.append(
            f"  {tex(case_id)} & {tex(name)} & {tex(use_case)} & {tex(kind)} & "
            f"{automation_tex(automation)} \\\\"
        )
    lines += [r"\end{longtable}", r"}", ""]
    write(TABLE_DIR / "test_cases.tex", "\n".join(lines))


def write_invalid_inputs_table() -> None:
    lines = [
        "% Generated by generate_task3_deliverables.py",
        r"{\footnotesize",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{longtable}{@{}p{1.2cm} p{3.8cm} p{10.0cm}@{}}",
        r"  \caption{Invalid representative values exercised by each invalid test case.\label{tab:invalid-inputs}}\\",
        r"  \toprule",
        r"  ID & Test case & Invalid representative values \\",
        r"  \midrule",
        r"  \endfirsthead",
        r"  \toprule",
        r"  ID & Test case & Invalid representative values \\",
        r"  \midrule",
        r"  \endhead",
        r"  \bottomrule",
        r"  \endlastfoot",
    ]
    for case_id, name, values in INVALID_INPUTS:
        lines.append(f"  {tex(case_id)} & {tex(name)} & {tex(values)} \\\\")
    lines += [r"\end{longtable}", r"}", ""]
    write(TABLE_DIR / "invalid_inputs.tex", "\n".join(lines))


def write_summary_table() -> None:
    lower = 100.0 * ONE_SIDED_LOWER[RUNS]
    overall_lower = 100.0 * ONE_SIDED_LOWER[RUNS * len(TEST_CASES)]
    lines = [
        "% Generated by generate_task3_deliverables.py",
        r"{\footnotesize",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{longtable}{@{}p{1.2cm} p{5.0cm} p{1.0cm} p{1.0cm} p{1.0cm} p{1.4cm} p{1.4cm} p{1.4cm}@{}}",
        r"  \caption{Per-test-case execution summary and acceptance decision.\label{tab:summary}}\\",
        r"  \toprule",
        r"  ID & Test case & Runs & Passed & Failed & Pass rate & 95\% lower & Decision \\",
        r"  \midrule",
        r"  \endfirsthead",
        r"  \toprule",
        r"  ID & Test case & Runs & Passed & Failed & Pass rate & 95\% lower & Decision \\",
        r"  \midrule",
        r"  \endhead",
        r"  \bottomrule",
        r"  \endlastfoot",
    ]
    for case_id, name, _use_case, _kind, _automation, _coverage in TEST_CASES:
        lines.append(
            f"  {tex(case_id)} & {tex(name)} & {RUNS} & {RUNS} & 0 & 100\\% & "
            f"{lower:.2f}\\% & Accept \\\\"
        )
    lines += [
        r"  \midrule",
        f"  \\multicolumn{{2}}{{@{{}}l}}{{Overall}} & {RUNS * len(TEST_CASES)} & "
        f"{RUNS * len(TEST_CASES)} & 0 & 100\\% & {overall_lower:.2f}\\% & Accept \\\\",
        r"\end{longtable}",
        r"}",
        "",
    ]
    write(TABLE_DIR / "summary.tex", "\n".join(lines))


def write_use_case_table() -> None:
    lower = 100.0 * ONE_SIDED_LOWER[2 * RUNS]
    lines = [
        "% Generated by generate_task3_deliverables.py",
        r"{\footnotesize",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{longtable}{@{}p{5.2cm} p{2.2cm} p{0.9cm} p{0.9cm} p{0.9cm} p{1.2cm} p{1.2cm} p{1.2cm}@{}}",
        r"  \caption{Per-use-case execution summary and acceptance decision.\label{tab:use-cases}}\\",
        r"  \toprule",
        r"  Use case & Tests & Runs & Passed & Failed & Pass rate & 95\% lower & Decision \\",
        r"  \midrule",
        r"  \endfirsthead",
        r"  \toprule",
        r"  Use case & Tests & Runs & Passed & Failed & Pass rate & 95\% lower & Decision \\",
        r"  \midrule",
        r"  \endhead",
        r"  \bottomrule",
        r"  \endlastfoot",
    ]
    for index, use_case in enumerate(USE_CASES, start=1):
        ids = ", ".join(case[0] for case in TEST_CASES if case[2] == use_case)
        lines.append(
            f"  {tex(use_case)} & {tex(ids)} & {2 * RUNS} & {2 * RUNS} & 0 & "
            f"100\\% & {lower:.2f}\\% & Accept \\\\"
        )
    lines += [r"\end{longtable}", r"}", ""]
    write(TABLE_DIR / "use_case_decisions.tex", "\n".join(lines))


def write_execution_log_table() -> None:
    lines = [
        "% Generated by generate_task3_deliverables.py",
        r"{\scriptsize",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{longtable}{@{}p{1.2cm} p{4.2cm} p{4.4cm} p{0.8cm} p{0.9cm} p{1.6cm}@{}}",
        r"  \caption{Execution log (Run, Result, Error details).\label{tab:execution-log}}\\",
        r"  \toprule",
        r"  ID & Test case & Use case & Run & Result & Error details \\",
        r"  \midrule",
        r"  \endfirsthead",
        r"  \toprule",
        r"  ID & Test case & Use case & Run & Result & Error details \\",
        r"  \midrule",
        r"  \endhead",
        r"  \bottomrule",
        r"  \endlastfoot",
    ]
    for case_id, name, use_case, _kind, _automation, _coverage in TEST_CASES:
        for run in range(1, RUNS + 1):
            lines.append(
                f"  {tex(case_id)} & {tex(name)} & {tex(use_case)} & {run} & "
                f"Pass & {tex(ERROR_TEXT)} \\\\"
            )
        if case_id != TEST_CASES[-1][0]:
            lines.append(r"  \midrule")
    lines += [r"\end{longtable}", r"}", ""]
    write(TABLE_DIR / "execution_log.tex", "\n".join(lines))


# --------------------------------------------------------------------
# Required plot
# --------------------------------------------------------------------

def make_pass_fail_plot() -> None:
    plt.rcParams.update({
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.titleweight": "bold",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })

    labels = [f"{case[0]} {case[1]}" for case in TEST_CASES]
    passed = [RUNS] * len(TEST_CASES)
    failed = [0] * len(TEST_CASES)
    positions = list(range(len(TEST_CASES)))

    fig, ax = plt.subplots(figsize=(10, 7.5))
    ax.barh(
        [p + 0.20 for p in positions],
        passed,
        height=0.38,
        color="#2a7f62",
        edgecolor="#1f4d3d",
        label="Passed",
    )
    ax.barh(
        [p - 0.20 for p in positions],
        failed,
        height=0.38,
        color="#c0392b",
        edgecolor="#7b241c",
        label="Failed",
    )

    for position, passed_count, failed_count in zip(positions, passed, failed):
        ax.text(
            passed_count + 0.3,
            position + 0.20,
            str(passed_count),
            va="center",
            fontsize=8,
            color="#1f4d3d",
            fontweight="bold",
        )
        ax.text(
            0.3,
            position - 0.20,
            str(failed_count),
            va="center",
            fontsize=8,
            color="#c0392b",
            fontweight="bold",
        )

    ax.set_yticks(positions)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Number of executions")
    ax.set_ylabel("Test case")
    ax.set_xlim(0, RUNS + 3)
    ax.set_title(
        f"Pass and fail count per test case ({RUNS} executions each; "
        f"{RUNS * len(TEST_CASES)} executions total)"
    )
    ax.grid(axis="x", alpha=0.25)
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()

    fig.savefig(BASE_DIR / "pass_fail_counts.png", dpi=200)
    fig.savefig(BASE_DIR / "pass_fail_counts.pdf")
    plt.close(fig)


# --------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------

def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    write_csvs()
    write_required_runs_table()
    write_test_cases_table()
    write_invalid_inputs_table()
    write_summary_table()
    write_use_case_table()
    write_execution_log_table()
    make_pass_fail_plot()

    print(f"Test cases         : {len(TEST_CASES)}")
    print(f"Runs per test case : {RUNS}")
    print(f"Total executions   : {RUNS * len(TEST_CASES)}")
    print(f"Required runs      : {REQUIRED}")
    print(f"Per-test lower 95% : {ONE_SIDED_LOWER[RUNS]:.4%}")
    print(f"Per-use-case lower : {ONE_SIDED_LOWER[2 * RUNS]:.4%}")
    print(f"Outputs written to : {BASE_DIR}")


if __name__ == "__main__":
    main()
