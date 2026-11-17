# Contributing to TestLedger

Thanks for helping. TestLedger is small on purpose: every module has one job, and every number in the memo must be traceable to an input and a configurable rate.

## Setup

```bash
git clone https://github.com/surkuar/testledger.git
cd testledger
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Before you open a PR

```bash
ruff format src tests examples
ruff check src tests examples
pytest
```

CI runs the same commands on Windows, macOS and Linux with Python 3.11–3.13, then runs the end-to-end demo.

## Ground rules

- **Platform independence:** use `pathlib`, pass `encoding="utf-8"` to every file read/write, call subprocesses with argument lists (never `shell=True`).
- **Offline tests:** network clients accept an injected `session`; stub it. Tests must never call real APIs.
- **Explainable numbers:** a new cost or value must be a new `EntryKind` with its rate in `config.Rates`, documented in `docs/methodology.md`.
- **Recommend, never act:** TestLedger never deletes or edits tests. Verdicts are advice for humans.

## Good first contributions

- A GitLab CI or Azure DevOps ingester (`src/testledger/ingest/`, returning `list[TestRun]`)
- An Allure or NUnit result parser
- `testledger diff` comparing two `ledger.json` files quarter over quarter
- CODEOWNERS join so the memo can be grouped by team

## Reporting a problem

Open an issue with the command you ran, your `testledger.yml` (redact tokens), and the `summary.json` it produced.
