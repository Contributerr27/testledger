"""CI client tests run fully offline using stub HTTP sessions."""

from __future__ import annotations

import io
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from testledger.ingest.github_actions import GitHubActionsClient, fetch_runs
from testledger.ingest.jenkins import JenkinsClient, fetch_builds


class _Resp:
    def __init__(self, payload, status=200, raw: bytes | None = None):
        self._payload, self.status_code, self.content = payload, status, raw or b""

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


class _GHSession:
    headers: dict = {}

    def __init__(self, fixtures: Path):
        self.fixtures = fixtures
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.write(fixtures / "junit/surefire.xml", "TEST-results.xml")
            zf.write(fixtures / "cucumber/cucumber.json", "cucumber.json")
        self.zip = buf.getvalue()

    def get(self, url, params=None, timeout=None):
        if url.endswith("/runs"):
            if params.get("page", 1) > 1:
                return _Resp({"workflow_runs": []})
            return _Resp(json.loads((self.fixtures / "ci/gha_runs.json").read_text(encoding="utf-8")))
        if url.endswith("/artifacts"):
            return _Resp(
                {
                    "artifacts": [
                        {
                            "id": 1,
                            "name": "test-results",
                            "expired": False,
                            "archive_download_url": "https://x/zip",
                        }
                    ]
                }
            )
        if url.endswith("/zip"):
            return _Resp(None, raw=self.zip)
        raise AssertionError(url)


def test_github_actions_fetch_runs_detects_attempts(fixtures: Path):
    client = GitHubActionsClient("acme/shop", token="t", session=_GHSession(fixtures))
    runs = fetch_runs("acme/shop", workflow="ci.yml", since=datetime(2026, 9, 1, tzinfo=UTC), client=client)
    assert len(runs) == 2
    assert {r.attempt for r in runs} == {1, 2} and all(r.commit_sha == "abc1234def" for r in runs)
    assert all(r.source == "github-actions" for r in runs)
    assert len(runs[0].results) == 15  # 12 junit + 3 cucumber merged


class _JSession:
    headers: dict = {}
    auth = None

    def __init__(self, fixtures: Path):
        self.fixtures = fixtures

    def get(self, url, params=None, timeout=None):
        if url.endswith("/job/acme-main/api/json"):
            return _Resp(json.loads((self.fixtures / "ci/jenkins_job.json").read_text(encoding="utf-8")))
        if "/11/testReport" in url:
            return _Resp(
                json.loads((self.fixtures / "ci/jenkins_report_fail.json").read_text(encoding="utf-8"))
            )
        if "/12/testReport" in url:
            return _Resp(
                json.loads((self.fixtures / "ci/jenkins_report_pass.json").read_text(encoding="utf-8"))
            )
        return _Resp(None, status=404)


def test_jenkins_fetch_builds_counts_same_sha_as_rerun(fixtures: Path):
    client = JenkinsClient("https://ci.acme.com", session=_JSession(fixtures))
    runs = fetch_builds(
        "https://ci.acme.com", "acme-main", since=datetime(2026, 9, 1, tzinfo=UTC), client=client
    )
    assert [r.attempt for r in runs] == [1, 2]
    first, second = runs
    assert first.failed == 1 and second.failed == 0
    assert first.branch == "origin/main" and first.source == "jenkins"
