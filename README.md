# Cross-Corridor Capacity Analysis with pandapower — Svedala grid

A six-notebook course teaching cross-zonal capacity analysis on the **simplified
Svedala transmission model** from KTH-EPE.

## Course structure

| # | Notebook | What students learn |
|---|----------|---------------------|
| 1 | `01_grid_model_loading.ipynb`     | Reconstitute the Svedala net from CSVs, inspect zones |
| 2 | `02_base_case_powerflow.ipynb`    | Run an AC power flow, check operating limits |
| 3 | `03_corridor_definition.ipynb`    | Define NORR→MITT corridor, GSK, base flow |
| 4 | `04_single_transfer_step.ipynb`   | Apply one ΔP shift, observe corridor response |
| 5 | `05_capacity_sweep.ipynb`         | Iterative sweep + bisection → TTC, both directions |
| 6 | `06_reporting.ipynb`              | Map overlay, capacity table, report export |

## Setup

```bash
pip install pandapower matplotlib pandas networkx tabulate
jupyter lab
```

Then open `01_grid_model_loading.ipynb`.

## The corridor

The default corridor is **`ZON_NORR` → `ZON_MITT`** — the Swedish "Snitt 2 / SE2-SE3"
boundary, where hydro-rich North Sweden exports power to load-heavy Central Sweden.
Notebook 3 shows how to switch to a different corridor (e.g. MITT → SYDVÄST).

## Files

Same as the N-1 course — `data/`, `svedala_loader.py`, `report/` (created at runtime).
