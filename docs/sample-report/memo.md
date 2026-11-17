# Quality Investment Memo — Acme Commerce (demo)

**Period:** last 90 days · **Generated:** 2026-11-17T14:33:36+00:00 · **Runs analysed:** 160 · **Tests on the books:** 15

## 1. Bottom line

| | USD |
|---|---:|
| Carrying cost of the test estate (CI, reruns, triage, maintenance) | 1223.54 |
| Value delivered (regressions caught × cost of a production defect) | 12000.00 |
| **Net** | **10776.46** |
| Portfolio ROI | 8.808 |

6 regression(s) were caught before production in the window.
6 tests are net assets; 7 are net liabilities.

## 2. Recommended reallocation

| Action | Tests | Annualised impact |
|---|---:|---:|
| Retire / quarantine | 5 | save ≈ $3582 |
| Demote UI tests to service/unit layer | 2 | save ≈ $858 |
| Fix (flaky or slow but valuable) | 0 | protects value already being delivered |
| Keep as assets | 4 | — |
| Hold (insufficient evidence) | 4 | re-evaluate next quarter |

## 3. Where the money goes

| Cost category | USD |
|---|---:|
| ci compute | 6.10 |
| rerun compute | 2.44 |
| triage time | 945.00 |
| maintenance | 270.00 |


| By layer | Tests | Cost | Value | Regressions |
|---|---:|---:|---:|---:|
| unit | 3 | 0.00 | 4000.00 | 2 |
| service | 4 | 22.60 | 4000.00 | 2 |
| ui | 8 | 1200.93 | 4000.00 | 2 |


## 4. Top liabilities (act on these first)

| Test | Layer | Flake | Avg s | Cost | Value | Verdict |
|---|---|---:|---:|---:|---:|---|
| `com.acme.ui.CheckoutSeleniumTest.full_checkout_chrome` | ui | 40% | 95.2 | 563.92 | 0.00 | **quarantine** |
| `checkout;guest-checkout-with-card` | ui | 10% | 83.3 | 113.74 | 0.00 | **retire** |
| `com.acme.ui.ReportsExportSeleniumTest.csv_export` | ui | 8% | 123.1 | 91.84 | 0.00 | **retire** |
| `com.acme.ui.LoginSeleniumTest.valid_login` | ui | 6% | 39.5 | 68.09 | 0.00 | **retire** |
| `com.acme.ui.LoginSeleniumTest.remember_me_cookie` | ui | 4% | 42.8 | 45.64 | 0.00 | **retire** |
| `search;search-by-sku` | ui | 0% | 29.1 | 0.43 | 0.00 | **hold** |
| `com.acme.api.OrderServiceIT.rejects_oos_item` | service | 0% | 2.1 | 0.03 | 0.00 | **hold** |


## 5. Top assets (protect these)

| Test | Layer | Regressions caught | Cost | Value |
|---|---|---:|---:|---:|
| `com.acme.unit.PriceCalculatorTest.applies_discount` | unit | 1 | 0.00 | 2000.00 |
| `com.acme.unit.TaxRulesTest.vat_rounding` | unit | 1 | 0.00 | 2000.00 |
| `com.acme.api.InventoryContractIT.schema_v2` | service | 1 | 0.03 | 2000.00 |
| `com.acme.api.OrderServiceIT.creates_order` | service | 1 | 22.54 | 2000.00 |
| `checkout;registered-checkout-with-saved-card` | ui | 1 | 46.21 | 2000.00 |
| `com.acme.ui.CheckoutSeleniumTest.apply_coupon` | ui | 1 | 271.06 | 2000.00 |



## 6. AI-generated test governance

1 tests are marked AI-generated; 1 fall below the governance thresholds (mutation score ≥ 0.5, assertion density ≥ 0.8). These are **unverified liabilities**: they add carrying cost without evidence they would fail on a real defect.

| Test | Mutation score | Assertion density | Cost |
|---|---:|---:|---:|
| `com.acme.ai.RecommendationServiceTest.returns_items` | 0.21 | 0.0 | 0.00 |



## 7. Assumptions (challenge these)

- engineer hourly usd: 75.0
- ci minute usd: 0.008
- triage minutes per false alarm: 18.0
- maintenance minutes per line: 1.5
- regression value usd: 2000.0
- risk coverage value usd: 0.0

- Window: 90 days, 160 runs analysed.
- Rates: engineer $75.0/h, CI $0.008/min, regression value $2000.0.
- Fix commits detected: 5; test files with churn: 1.


*Method: every test is booked like an account. Debits are CI minutes, rerun minutes, engineer triage time on flaky failures and maintenance churn from git history. Credits are genuine first-attempt failures followed within 3 days by a product fix commit, valued at the organisation's cost of a production defect. Full method: docs/methodology.md.*