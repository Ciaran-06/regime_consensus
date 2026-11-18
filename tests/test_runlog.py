import pytest

from regime_consensus import runlog


@pytest.fixture
def log_path(tmp_path, monkeypatch):
    path = tmp_path / "runs.csv"
    monkeypatch.setattr(runlog, "LOG_PATH", path)
    return path


def test_new_run_passes_on_empty_log(log_path):
    runlog.check_new_run("diagnostic", "scripts/x.py", "first run")


def test_duplicate_run_is_refused(log_path):
    runlog.log_run("diagnostic", "5", "scripts/x.py", "first run", "result")
    with pytest.raises(RuntimeError, match="already been run"):
        runlog.check_new_run("diagnostic", "scripts/x.py", "first run")


def test_rerun_with_reason_passes(log_path):
    runlog.log_run("diagnostic", "5", "scripts/x.py", "first run", "result")
    runlog.check_new_run("diagnostic", "scripts/x.py", "Rerun of R01 after bug fix. first run")


def test_same_text_different_script_passes(log_path):
    runlog.log_run("diagnostic", "5", "scripts/x.py", "first run", "result")
    runlog.check_new_run("diagnostic", "scripts/y.py", "first run")


def test_full_budget_is_refused_before_running(log_path, monkeypatch):
    monkeypatch.setattr(runlog, "RUN_BUDGET", 1)
    runlog.log_run("diagnostic", "5", "scripts/x.py", "first run", "result")
    with pytest.raises(RuntimeError, match="budget used up"):
        runlog.check_new_run("diagnostic", "scripts/x.py", "second run")


def test_log_run_still_records_a_duplicate(log_path):
    runlog.log_run("diagnostic", "5", "scripts/x.py", "first run", "result")
    run_id = runlog.log_run("diagnostic", "5", "scripts/x.py", "first run", "result")
    assert run_id == "R02"