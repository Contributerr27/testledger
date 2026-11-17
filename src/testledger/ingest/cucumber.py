"""Cucumber JSON report parser (cucumber-jvm, cucumber-ruby, cucumber-js share the schema).

A scenario is one ``TestResult``; its outcome is the worst step outcome.
Scenario Outline examples carry distinct ids so each example row is a test.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from testledger.models import Outcome, TestResult, TestRun

_STEP_RANK = {"passed": 0, "skipped": 1, "pending": 1, "undefined": 2, "failed": 3}


def parse_cucumber_json(
    path: str | Path,
    *,
    run_id: str | None = None,
    started_at: datetime | None = None,
    commit_sha: str | None = None,
    branch: str | None = None,
    attempt: int = 1,
) -> TestRun:
    p = Path(path)
    features = json.loads(p.read_text(encoding="utf-8"))
    results: list[TestResult] = []

    for feature in features:
        feature_name = feature.get("name", p.stem)
        uri = feature.get("uri")
        for element in feature.get("elements", []):
            if element.get("type") == "background":
                continue
            worst = "passed"
            duration_ns = 0
            msg = None
            for step in element.get("steps", []) + element.get("before", []) + element.get("after", []):
                res = step.get("result", {})
                status = res.get("status", "passed")
                duration_ns += int(res.get("duration", 0) or 0)
                if _STEP_RANK.get(status, 0) > _STEP_RANK.get(worst, 0):
                    worst = status
                    msg = (res.get("error_message") or "")[:300] or None
            if worst == "failed" or worst == "undefined":
                outcome = Outcome.FAILED
            elif worst in ("skipped", "pending"):
                outcome = Outcome.SKIPPED
            else:
                outcome = Outcome.PASSED
            scenario_id = element.get("id") or f"{feature_name};{element.get('name')}"
            tags = [t.get("name", "") for t in element.get("tags", [])]
            results.append(
                TestResult(
                    test_id=scenario_id,
                    name=element.get("name", "unnamed scenario"),
                    suite=feature_name,
                    file=uri,
                    outcome=outcome,
                    duration_s=duration_ns / 1e9,
                    message=msg,
                    tags=tags,
                )
            )

    ts = started_at or datetime.fromtimestamp(p.stat().st_mtime, tz=UTC)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    return TestRun(
        run_id=run_id or p.stem,
        started_at=ts,
        commit_sha=commit_sha,
        branch=branch,
        attempt=attempt,
        source="cucumber",
        results=results,
    )
