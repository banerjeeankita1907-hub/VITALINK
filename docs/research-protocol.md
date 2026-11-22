# Research and evaluation protocol

## Research question

Can disruption-aware integer procurement planning reduce modeled total cost and unmet demand relative to a simple nominal-price reorder policy under uncertain demand, lead times and supplier availability, while keeping service levels and storage use explicit?

## Hypotheses to test

- **H1 — Cost/service trade-off:** accounting for supplier reliability and shortage penalties changes the selected supplier mix compared with nominal unit-price selection.
- **H2 — Disruption response:** a re-optimized plan under an outage or lead-time shock has lower modeled penalty cost than keeping the original purchase plan unchanged.
- **H3 — Capacity awareness:** supplier capacity and MOQs materially affect feasibility and shortage outcomes when demand spikes.
- **H4 — Sustainability trade-off:** changing the carbon price changes the supplier allocation where price, carbon intensity and reliability differ.

These are hypotheses, not results.

## Reproducible experimental setup

1. Pin the data version and random seed. The included dataset is synthetic and deterministic.
2. Use the rolling-origin holdout implemented in `vitalink/forecast.py`; do not compute metrics on periods used to calculate the forecast level.
3. Report the weekly-seasonal blended forecast and seasonal-naive forecast side by side.
4. Hold inventory, planning horizon and demand forecast constant while varying one scenario factor at a time.
5. Run baseline, +25% demand, farm-cooperative outage, aggregator delay and compound shock.
6. Compare the MILP against the included cheapest-nominal-price greedy heuristic using the same demand, inventory, model costs and supplier inputs.
7. Export solver inputs, SciPy version, solver status, objective breakdown and SKU-level outcomes for every run.
8. Repeat across fixed seeds when stochastic demand/outage generation is introduced.

## Metrics

- Forecast: MAE, WAPE and signed bias.
- Operations: service level, shortage units, ending stock, supplier utilization and recovery time (when multi-period dynamics are added).
- Economics: procurement spend, fixed order cost, holding, shortage penalty, risk premium, carbon cost and total modeled cost.
- Sustainability: emissions proxy from order quantity multiplied by supplier-SKU emissions factors.
- Computation: solve time, optimality status and model size.

## Baselines

**Implemented in v0.1:** a greedy policy that selects nominally cheapest eligible suppliers per SKU, respects quoted lead time, supplier capacity, MOQ and aggregate ending-stock capacity, then reports the same modeled cost components and service level.

**Further baselines for a defensible study:** static reorder-point/min-max inventory, forecast-only policy without supplier-risk/carbon terms, and a policy using an established commercial or open-source optimizer. Ensure constraints and service levels are comparable. Do not let one policy appear cheaper merely by accepting more stockouts.

## Reproducibility and limitations

The current project provides the dataset, deterministic demand evaluation, scenarios, optimization model and one transparent heuristic comparator. It does not yet include repeated stochastic trials, field calibration, external solver comparison, or an empirical claim that VITALINK beats a competing policy. Results must be described as model outputs on synthetic data until those extensions are completed.
