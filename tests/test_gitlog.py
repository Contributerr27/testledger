"""Git ingestion against a real throwaway repository (requires the `git` CLI)."""

from __future__ import annotations

import os
import shutil
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from testledger.ingest.gitlog import collect_churn, collect_fix_commits

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")


def _git(repo: Path, *args: str) -> None:
    env = os.environ | {
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.com",
    }
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, env=env)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    test_file = tmp_path / "src/test/java/CalcTest.java"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("\n".join(f"line {i}" for i in range(50)), encoding="utf-8")
    (tmp_path / "src/main").mkdir(parents=True)
    (tmp_path / "src/main/Calc.java").write_text("class Calc {}", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "feat: add calculator and its tests")
    test_file.write_text(test_file.read_text(encoding="utf-8") + "\nextra 1\nextra 2\n", encoding="utf-8")
    _git(tmp_path, "commit", "-q", "-am", "test: tweak calc test")
    (tmp_path / "src/main/Calc.java").write_text("class Calc { int x; }", encoding="utf-8")
    _git(tmp_path, "commit", "-q", "-am", "fix: rounding bug in Calc")
    return tmp_path


def test_churn_counts_modifications_not_authoring(repo: Path):
    churn = collect_churn(repo, datetime.now(tz=UTC) - timedelta(days=1))
    rec = churn["src/test/java/CalcTest.java"]
    # The 50 lines written when the test was created are authoring, not maintenance.
    assert rec.commits == 1
    assert 0 < rec.lines_changed < 10
    assert "src/main/Calc.java" not in churn


def test_fix_commits_only_on_product_code(repo: Path):
    fixes = collect_fix_commits(repo, datetime.now(tz=UTC) - timedelta(days=1))
    assert [f.message for f in fixes] == ["fix: rounding bug in Calc"]
    assert fixes[0].files == ["src/main/Calc.java"]


def test_non_repo_returns_empty(tmp_path: Path):
    since = datetime.now(tz=UTC) - timedelta(days=1)
    assert collect_churn(tmp_path, since) == {} and collect_fix_commits(tmp_path, since) == []
