# Billing Automation & Data Quality

**Automate preparation. Keep exceptions visible.** A personal Python portfolio demo by Diego Gallo that converts cumulative readings into validated billing drafts and a separate exception queue.

This newly implemented demo demonstrates transferable experience in billing preparation, reconciliation and operational controls. It contains **no employer data, code, names, tariffs or internal business rules**. It is not a production invoicing system.

## Run

Run from the root of this repository (`billing-automation-data-quality`).

Python 3.11+; standard library only.

```bash
python billing.py
python -m unittest discover -s tests -v
```

The deterministic synthetic dataset contains 100 fictional accounts. Five deliberately defective accounts are held; 95 produce drafts. No real invoices are created or sent. Review `outputs/billing_drafts.csv`, `outputs/exceptions.csv` and `outputs/run_summary.json` in Excel or a text editor.

You may rerun the same demonstration schema with a synthetic CSV:

```bash
python billing.py --input outputs/synthetic_input.csv
```

## Controls before calculation

| Control | Treatment |
|---|---|
| Exactly one reading at each period boundary | Missing or duplicate boundary → hold |
| Valid, finite, nonnegative cumulative values | Invalid input → hold |
| Nonnegative change | Reset, rollover or negative change → hold; no estimation |
| Consumption above a fixed review threshold | Hold for investigation; no automatic correction |
| Unexpected dates | Hold; no silent filtering |
| Missing account identifier | Reject run; no silent orphan drop |

Account populations reconcile: **draft + held = input accounts**, with no overlap. An absent account cannot be detected from a readings-only input; a future customer register should define the full eligible population.

## Demonstration calculation

The fixed period is September 2026: boundary readings on `2026-09-01` and `2026-10-01`. Consumption is the closing cumulative reading minus the opening reading. The arbitrary demonstration rate is 0.18 currency units/unit plus a 4.50 fixed charge; the review threshold is 2,000 units. These are fictional values, not Spanish or energy-market tariffs.

Amounts use `Decimal`, rounded half-up to two decimals at the variable-charge stage. For 150 units: `150 × 0.18 + 4.50 = 31.50`, before any tax. Tax, discounts, proration, meter resets, estimates, multiple readings within the period and regulatory invoicing are outside this demo.

## Evidence and reproducibility

Tests independently verify an expected charge, decimal rounding, zero consumption, each injected defect, account partition, reconciliation, non-finite values and input-order independence. A fixed seed reproduces the same demo. Outputs are regenerated locally and excluded from Git.

No processing-time improvement is claimed for this demo. Historical professional achievements belong in the CV and require their own evidence.

## Español

Automatización de preparación de facturación y calidad de datos con Python: valida lecturas acumuladas, separa incidencias, calcula borradores y reconcilia la población de cuentas. Demuestra criterio de negocio y trazabilidad, con datos y valores completamente ficticios.

## Next steps

Add an eligible-account register, period configuration, structured audit logs, input-version fingerprints and integration tests for approved sample datasets. Source code is available for portfolio review; no open-source licence has been assigned.

## Clone this project

```bash
git clone https://github.com/diiego2102/billing-automation-data-quality.git
cd billing-automation-data-quality
```

Follow the run commands above from this folder.
