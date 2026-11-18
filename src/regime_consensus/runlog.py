"""The run log (runs.csv). Every analysis script calls check_new_run at the top and log_run at the end,
so no run goes unrecorded and no run is repeated by accident.

    check_new_run(run_type, script, what_changed)            refuse a duplicate or over-budget run, before any data is loaded
    log_run(run_type, phase, script, what_changed, result)   append one row, return its run ID
    budget_used()                                            counted runs so far

IDs: data checks get D01, D02, ...; every other run type gets R01, R02, ... (R00 is the exploratory phase).
Data checks and exploratory runs do not count towards the run budget (NOTES.md section 7).
"""

from __future__ import annotations

import csv
from datetime import date
from typing import Literal

import pandas as pd

from regime_consensus.config import LOG_PATH, RUN_BUDGET

# Must match the header of runs.csv exactly, in this order.
COLUMNS = ["run_id", "date", "type", "counts_toward_budget", "phase", "script", "what_changed", "result"]

RunType = Literal["exploratory", "data", "diagnostic", "confirmatory"]

# For each run type: the ID prefix, and whether it uses up the run budget.
RUN_TYPES: dict[str, tuple[str, bool]] = {
    "exploratory": ("R", False),
    "data": ("D", False),
    "diagnostic": ("R", True),
    "confirmatory": ("R", True),
}


def _read_log() -> pd.DataFrame:
    if not LOG_PATH.exists():
        return pd.DataFrame(columns=COLUMNS)
    log = pd.read_csv(LOG_PATH, dtype=str)
    if list(log.columns) != COLUMNS:
        raise ValueError(f"{LOG_PATH} has columns {list(log.columns)}, expected {COLUMNS}. Fix the file before logging.")
    return log


def _next_run_id(log: pd.DataFrame, prefix: str) -> str:
    """The next ID for this prefix, counting only IDs with the same prefix: 'R01' -> 'R02', 'D04' -> 'D05'."""
    same_prefix = log["run_id"].dropna()
    same_prefix = same_prefix[same_prefix.str.startswith(prefix)]
    numbers = pd.to_numeric(same_prefix.str[len(prefix):], errors="coerce")
    next_number = int(numbers.max()) + 1 if numbers.notna().any() else 1
    return f"{prefix}{next_number:02d}"


def _run_type_info(run_type: str) -> tuple[str, bool]:
    if run_type not in RUN_TYPES:
        raise ValueError(f"run_type must be one of {list(RUN_TYPES)}, got {run_type!r}")
    return RUN_TYPES[run_type]


def _used(log: pd.DataFrame) -> int:
    return int((log["counts_toward_budget"] == "yes").sum())


def budget_used() -> int:
    """Number of runs so far that count towards the budget."""
    return _used(_read_log())


def check_new_run(run_type: RunType, script: str, what_changed: str) -> None:
    """Call at the top of a script, before loading any data.

    Raises if the budget is used up, or if runs.csv already has a run with the same script and
    what_changed. A deliberate rerun must say why in what_changed, which makes it a new entry.
    """
    _, counts = _run_type_info(run_type)
    log = _read_log()

    if counts and _used(log) >= RUN_BUDGET:
        raise RuntimeError(f"Run budget used up ({_used(log)} of {RUN_BUDGET}). Stop and write up (BACKTESTING.md rule 11).")

    duplicates = log[(log["script"] == script) & (log["what_changed"] == what_changed)]
    if not duplicates.empty:
        ids = ", ".join(duplicates["run_id"])
        raise RuntimeError(
            f"{script} has already been run with this what_changed ({ids}). "
            "If this is a deliberate rerun, say why in what_changed."
        )


def log_run(run_type: RunType, phase: str, script: str, what_changed: str, result: str) -> str:
    """Append one run to runs.csv and return its run ID.

    Never refuses a duplicate: by the time this is called the run has happened, so it must be recorded.
    Duplicates are stopped earlier, by check_new_run.
    """
    prefix, counts = _run_type_info(run_type)

    log = _read_log()
    used = _used(log)
    if counts and used >= RUN_BUDGET:
        raise RuntimeError(f"Run budget used up ({used} of {RUN_BUDGET}). Stop and write up (BACKTESTING.md rule 11).")

    row = {
        "run_id": _next_run_id(log, prefix),
        "date": date.today().isoformat(),
        "type": run_type,
        "counts_toward_budget": "yes" if counts else "no",
        "phase": phase,
        "script": script,
        "what_changed": what_changed,
        "result": result,
    }

    is_new_file = not LOG_PATH.exists()
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        if is_new_file:
            writer.writeheader()
        writer.writerow(row)

    remaining = RUN_BUDGET - used - (1 if counts else 0)
    print(f"Logged {row['run_id']} ({run_type}). Budget: {RUN_BUDGET - remaining} of {RUN_BUDGET} used, {remaining} left.")
    return row["run_id"]