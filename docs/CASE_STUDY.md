# Billing preparation case study

## Decision
Which accounts have sufficiently consistent readings to prepare a billing draft, and which require manual review?

## Implementation
Python groups cumulative readings at two period boundaries. It rejects missing or duplicate endpoints, non-finite values, unexpected dates, negative deltas and unusually high consumption. Decimal arithmetic rounds demonstration charges explicitly. Draft and hold populations are disjoint and reconcile to the account population.

## Demonstrated result
The seeded fixture produces 95 drafts and holds all five deliberately defective accounts. The fictional draft total before tax is 7,914.42. Independent tests verify a 150-unit example, rounding, zero consumption and each defect. An optional eligible-account register detects accounts with no readings at all; unknown accounts cause a blocking error.

## Tradeoffs
This is draft preparation, not a real tariff calculator or invoicing integration. Boundaries, rates and review threshold are fixed demonstration assumptions. Meter resets require review. Without an eligible register, entirely absent accounts cannot be detected. A provided CSV is labelled separately from synthetic generation.

## Evidence
Run `python billing.py` and the seven tests. Supply `--registry eligible_accounts.csv` to activate population completeness checks. No company data, identifiers or code is included.
