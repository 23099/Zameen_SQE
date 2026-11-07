# conftest.py
import csv, os, random, re, time
import pytest

RESULTS = os.getenv("RESULTS_FILE", "results.csv")
NAME_TO_TC = {
    "test_registration_valid": "TC01",
    "test_registration_invalid": "TC02",
}

def tc_id(name):
    if name in NAME_TO_TC:
        return NAME_TO_TC[name]
    m = re.search(r"TC(\d+)", name)
    return f"TC{m.group(1)}" if m else name

@pytest.fixture(autouse=True)
def polite_wait():
    yield
    time.sleep(random.uniform(3, 10))      # assignment rule: 3-10 s between runs

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    rep = (yield).get_result()
    if rep.when == "call" or (rep.when == "setup" and rep.failed):
        new = not os.path.exists(RESULTS)
        with open(RESULTS, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["tc", "test", "run_id", "result", "seconds", "error"])
            w.writerow([
                tc_id(item.originalname), item.originalname, item.name,
                "PASS" if rep.passed else "FAIL", round(rep.duration, 1),
                str(rep.longrepr)[-200:].replace("\n", " ") if rep.failed else "",
            ])