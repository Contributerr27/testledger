# Changelog

All notable changes to this project are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning: [SemVer](https://semver.org/).

## [0.1.0] — 2026-11-17

### Added
- Ledger engine: per-test debits (CI compute, rerun compute, triage time, maintenance churn) and credits (regressions caught, optional risk-coverage value).
- Same-SHA rerun flake detection; flake rate measured per commit tested.
- Regression credit: genuine first-attempt failure followed by a product-code fix commit within 3 days.
- Verdicts: quarantine, retire, demote, fix, asset, hold — all thresholds configurable.
- Ingesters: JUnit/Surefire XML, TestNG XML, Cucumber JSON, git history, GitHub Actions REST API, Jenkins JSON API.
- AI-generated test governance: provenance markers, assertion density, PIT/Stryker/mutmut mutation-score join.
- Reports: Quality Investment Memo (Markdown + HTML), balance sheet, income statement, write-offs, AI liabilities, full `ledger.json`.
- CLI: `init`, `analyze`, `memo`, `pr-comment`.
- Composite GitHub Action with job summary, artifact upload and a single upserted PR comment.
- Demo generator producing a 12-week synthetic test estate with git history.
- CI matrix: Windows, macOS, Linux × Python 3.11, 3.12, 3.13.
