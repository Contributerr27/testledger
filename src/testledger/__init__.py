"""TestLedger — Test Estate Balance Sheet.

Treats an automated test suite as an investment portfolio: every test carries a
cost (CI minutes, reruns, triage, maintenance churn) and produces a return
(regressions caught). TestLedger ingests CI results and git history, books
every cost and value entry into a double-entry style ledger, and renders
executive-facing reports: a Balance Sheet, an Income Statement, a Write-off
list and a one-page Quality Investment Memo.
"""

__version__ = "0.1.0"
