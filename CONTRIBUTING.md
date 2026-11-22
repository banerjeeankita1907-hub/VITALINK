# Contributing

VITALINK is an interdisciplinary research prototype. Contributions should preserve reproducibility and distinguish model output from field evidence.

1. Explain the SCM decision being represented before changing a business rule.
2. Add a deterministic test for every constraint, forecast rule or simulator behaviour.
3. Keep solver inputs, model assumptions and returned cost components inspectable.
4. Add a research note when a change alters the mathematical formulation.
5. Do not introduce real supplier/customer data without permission and a documented provenance statement.
6. Report solver status and limitations; do not label a feasible/non-optimal result as optimal.
7. Run `python -m compileall -q vitalink tests scripts` and `pytest` before submitting.

For research comparisons, use identical demand, inventory, capacity, budget and cost assumptions for all policies. Report service level next to cost.
