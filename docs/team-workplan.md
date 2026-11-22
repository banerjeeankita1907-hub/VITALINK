# Interdisciplinary team workplan

This workplan separates domain ownership from implementation ownership. Both contributors should review the full model and jointly approve assumptions.

## Supply Chain Management student

### Deliverables
- Draw the as-is and to-be supply network.
- Define SKU segmentation, shelf-life classes and demand drivers.
- Elicit supplier reliability, lead-time distributions, MOQs, price breaks and capacity.
- Define the service-level target, lost-sales/backorder treatment, holding and expiry costs.
- Validate scorecard weights with a documented procurement decision matrix.
- Review the scenario set and interpret inventory, supplier concentration and working-capital impacts.

### Evidence
A data dictionary, process map, parameter justification log, stakeholder interview notes (with consent), and an SCM interpretation of every experiment.

## Computer Science / Operations Research expert

### Deliverables
- Implement ingestion, validation and reproducible forecasting.
- Formulate and test the MILP, documenting variable and constraint semantics.
- Implement baseline comparators, what-if simulator and dashboard.
- Add property tests, solver-status checks, API tests and CI.
- Run scalability, sensitivity and ablation experiments.
- Package deployment and reproducibility instructions.

### Evidence
Source code, test logs, solver configuration, benchmark artifacts, exact experiment seeds, and limitations.

## Joint review checkpoints

1. **Model sign-off:** validate inventory balance, fulfilled demand and shortage semantics with hand-computed examples.
2. **Data sign-off:** verify data provenance, units, time zone, missingness and outlier handling.
3. **Experiment sign-off:** agree metrics and fair baselines before comparing outcomes.
4. **Research sign-off:** interpret effects and limitations together; do not claim causal business savings from synthetic model output.
