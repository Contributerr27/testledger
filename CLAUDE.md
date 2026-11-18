# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

TestLedger turns CI test results + git history into a per-test P&L (cost vs. value), assigns each test a verdict (`retire / demote / fix / quarantine / asset / hold`), and renders an executive "Quality Investment Memo". Python ≥ 3.11, src-layout package `testledger`, Typer CLI entry point `testledger = testledger.cli:app`. Also ships as a composite GitHub Action (`action.yml`).

## Commands

```bash
pip install -e ".[dev]"                     # setup (use .venv; Windows: .venv\Scripts\activate)
pytest                                      # full suite, offline
pytest tests/test_engine.py                 # one file
pytest tests/test_engine.py -k flake        # one test / pattern
ruff format src tests examples
ruff check src tests examples               # run both before PRs (CI does)
mypy src

# End-to-end demo (also run by CI)
python examples/generate_demo.py demo-estate
cd demo-estate && testledger analyze --config testledger.yml --reports . --mutation mutation.json --out reports
testledger memo reports
```

CLI commands: `init`, `analyze`, `memo`, `pr-comment`. `analyze --fail-on-quarantine` exits 2 when any test is quarantine-grade.

## Architecture

Pipeline: **ingest → `list[TestRun]` + churn/fix commits + AI scan → ledger engine → report builder → output folder**.

- `models.py` — domain model shared by everything: `TestRun`/`TestResult` (normalised input), `ChurnRecord`, `FixCommit`, `LedgerEntry` (one debit/credit with an `EntryKind`), `TestAccount` (per-test book with `total_cost/total_value/net/roi`), `Ledger`, `Verdict`, `Layer`.
- `config.py` — pydantic schema for `testledger.yml` (`Rates`, thresholds, `sources`, `layers`). Every number in the memo must trace to a rate/threshold here.
- `ingest/` — each ingester returns `list[TestRun]`. JUnit/TestNG (auto-detected) and Cucumber parse local files; `github_actions.py` and `jenkins.py` are REST clients. `gitlog.py` shells out to `git log` for test-file churn and product-code fix commits.
- `cli.py` — orchestrates. For local report folders, rerun metadata comes from the directory name `<YYYYMMDD>[THHMM]-<sha>-attempt<N>` (`_meta_from_path`); without it there is no rerun/flake detection.
- `aitest/detector.py` — flags AI-generated tests (provenance markers, assertion density) and joins mutation scores (PIT XML, Stryker JSON, or `{file: score}`) by `FooTest ↔ Foo`.
- `ledger/engine.py` — the core logic (`build_ledger`, `_assign_verdicts`):
  - **Flake** = same-SHA fail→pass across attempts. This is the only flake signal.
  - **Regression credit** = attempt-1 failure not in a flaky (sha,test) pair, followed within `FIX_WINDOW` (3 days, module constant) by a product-code commit whose subject matches the fix pattern. A fix commit is consumed once per test.
  - Layer classification via substring rules; UI is checked first.
  - Verdict decision tree is documented in `docs/design.md` §6.4.
- `reports/builder.py` — `build_reports` → `ReportBundle` → `write_reports` emits `memo.md/html` (Jinja templates in `templates/`), `balance_sheet.json`, `income_statement.json`, `writeoffs.json`, `ai_liabilities.json`, `ledger.json`, `summary.json`.

`docs/methodology.md` holds the cost/value formulas; `docs/design.md` holds architecture and decision diagrams. Keep both in sync with engine changes.

## Ground rules (from CONTRIBUTING.md)

- Platform-independent: `pathlib`, `encoding="utf-8"` on every file read/write, subprocesses with argument lists (never `shell=True`). CI runs on Windows/macOS/Linux × Python 3.11–3.13.
- Tests are offline: network clients accept an injected `session`; stub it (see `tests/test_ci_clients.py`, fixtures in `tests/fixtures/ci/`). Git tests use a throwaway repo. `tests/conftest.py` has `make_run(...)` and a fixed `NOW` for building synthetic runs.
- A new cost or value must be a new `EntryKind`, with its rate in `config.Rates`, documented in `docs/methodology.md`.
- Recommend, never act: the tool never deletes or edits tests.

## Gotcha

`.gitignore` contains `reports/`, which also matches `src/testledger/reports/`. The builder module is therefore **not tracked in git**. Use `git add -f` for it, or anchor the ignore rule (e.g. `/reports/`).
