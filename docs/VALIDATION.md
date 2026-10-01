# Validation · portfolio v0.1.0

Executed on 1 October 2026 with Python's standard library:

- `python billing.py`: 100 fictional accounts; 95 drafts, 5 held accounts. Total before tax: 7,914.42 fictional currency units.
- `python -m unittest discover -s tests -v`: 5 tests passed.
- Independent fixtures check the 31.50 total for 150 units, half-up rounding, zero consumption, each deliberate defect and account partition/reconciliation.
- Non-finite readings, unexpected dates and orphan identifiers are handled explicitly.

This prepares draft calculations only. Rates, thresholds, account identifiers and readings are fictitious. No invoices are issued. No historical processing-time improvement, tax handling, legal compliance or production readiness is asserted.

## Portfolio v0.2.0

Seven tests pass. New independent fixtures verify that an eligible account without any readings is held and an account outside the register blocks processing. CLI summary distinguishes provided CSV from synthetic generation. No jurisdiction-specific tariff or tax validation is claimed.
