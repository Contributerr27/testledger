"""Jenkins ingester.

Uses the Jenkins JSON API (``/job/<name>/api/json`` and the
``testReport`` endpoint of each build). Works with the JUnit plugin and the
Cucumber Reports plugin's JUnit export. Reruns are detected when the same
commit SHA appears in consecutive builds (``lastBuiltRevision`` in build
actions), so a "rebuild until green" shows up as rerun cost.

Authentication: basic auth with user + API token from environment variables
named by ``sources.jenkins.user_env`` / ``token_env``.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime

import requests

from testledger.models import Outcome, TestResult, TestRun

_STATUS = {
    "PASSED": Outcome.PASSED,
    "FIXED": Outcome.PASSED,
    "FAILED": Outcome.FAILED,
    "REGRESSION": Outcome.FAILED,
    "SKIPPED": Outcome.SKIPPED,
}


class JenkinsClient:
    def __init__(
        self,
        base_url: str,
        user: str | None = None,
        token: str | None = None,
        session: requests.Session | None = None,
    ):
        self.base = base_url.rstrip("/")
        self.session = session or requests.Session()
        if user and token:
            self.session.auth = (user, token)
        self.session.headers["User-Agent"] = "testledger"

    def builds(self, job: str, max_builds: int = 100) -> list[dict]:
        job_path = "/job/" + "/job/".join(job.split("/"))
        resp = self.session.get(
            f"{self.base}{job_path}/api/json",
            params={
                "tree": f"builds[number,timestamp,result,actions[lastBuiltRevision[SHA1,branch[name]]]]{{0,{max_builds}}}"
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("builds", [])

    def test_report(self, job: str, number: int) -> dict | None:
        job_path = "/job/" + "/job/".join(job.split("/"))
        resp = self.session.get(f"{self.base}{job_path}/{number}/testReport/api/json", timeout=60)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()


def _sha_and_branch(build: dict) -> tuple[str | None, str | None]:
    for action in build.get("actions", []):
        rev = action.get("lastBuiltRevision") if isinstance(action, dict) else None
        if rev:
            branches = rev.get("branch", [])
            return rev.get("SHA1"), (branches[0].get("name") if branches else None)
    return None, None


def fetch_builds(
    base_url: str,
    job: str,
    *,
    since: datetime,
    user_env: str = "JENKINS_USER",
    token_env: str = "JENKINS_TOKEN",
    max_builds: int = 100,
    client: JenkinsClient | None = None,
) -> list[TestRun]:
    client = client or JenkinsClient(base_url, os.environ.get(user_env), os.environ.get(token_env))
    runs: list[TestRun] = []
    seen_sha: dict[str, int] = {}
    # Jenkins returns newest first; reverse so attempts count upward in time.
    for build in reversed(client.builds(job, max_builds)):
        ts = datetime.fromtimestamp(build["timestamp"] / 1000, tz=UTC)
        if ts < since:
            continue
        report = client.test_report(job, build["number"])
        if not report:
            continue
        sha, branch = _sha_and_branch(build)
        attempt = 1
        if sha:
            seen_sha[sha] = seen_sha.get(sha, 0) + 1
            attempt = seen_sha[sha]
        results: list[TestResult] = []
        for suite in report.get("suites", []):
            for case in suite.get("cases", []):
                outcome = _STATUS.get(case.get("status", "PASSED").upper(), Outcome.PASSED)
                cls = case.get("className", suite.get("name", ""))
                results.append(
                    TestResult(
                        test_id=f"{cls}.{case.get('name')}",
                        name=case.get("name", ""),
                        suite=cls,
                        outcome=outcome,
                        duration_s=float(case.get("duration", 0.0)),
                        message=(case.get("errorDetails") or "")[:300] or None,
                    )
                )
        runs.append(
            TestRun(
                run_id=f"jenkins-{job.replace('/', '_')}-{build['number']}",
                started_at=ts,
                commit_sha=sha,
                branch=branch,
                attempt=attempt,
                source="jenkins",
                results=results,
            )
        )
    return runs
