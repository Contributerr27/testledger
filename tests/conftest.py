from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from testledger.config import Config
from testledger.models import Outcome, TestResult, TestRun

FIXTURES = Path(__file__).parent / "fixtures"
NOW = datetime(2026, 11, 1, tzinfo=UTC)


@pytest.fixture
def fixtures() -> Path:
    return FIXTURES


@pytest.fixture
def cfg() -> Config:
    return Config(window_days=90)


def make_run(
    run_id: str,
    sha: str,
    attempt: int,
    days_ago: int,
    outcomes: dict[str, Outcome],
    duration: float = 1.0,
    file: str | None = None,
) -> TestRun:
    return TestRun(
        run_id=run_id,
        started_at=NOW - timedelta(days=days_ago),
        commit_sha=sha,
        attempt=attempt,
        results=[
            TestResult(
                test_id=t,
                name=t.rsplit(".", 1)[-1],
                suite=t.rsplit(".", 1)[0],
                outcome=o,
                duration_s=duration,
                file=file,
            )
            for t, o in outcomes.items()
        ],
    )
