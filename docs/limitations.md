# Known limitations and safeguards

1. **Synthetic data only.** The committed demand series is generated, not observed. It must not be presented as market research or partner-company evidence.
2. **One aggregate warehouse.** Current optimization is a single-node procurement model, not a complete multi-echelon network flow model.
3. **Expected reliability.** Reliability scales expected receipts. It does not imply a guaranteed delivery or chance-constrained service level.
4. **No inventory ageing.** Shelf-life metadata is present but expiry, FEFO, cold-chain excursions and spoilage are not implemented in the initial optimization.
5. **Deterministic forecast.** The included seasonal-blended baseline is deliberately interpretable. It is not claimed to be an advanced forecasting model.
6. **Proxy costs.** Stockout penalty, holding and risk premium are configurable assumptions requiring stakeholder calibration.
7. **Emissions proxies.** Emission factors are illustrative configuration inputs, not supplier-specific audited lifecycle values.
8. **Solver dependency.** Integer optimality is conditional on solver status and the exact mathematical formulation. A feasible result is not an optimal result unless the solver reports optimal termination.
9. **No automated purchase execution.** VITALINK only produces recommendations; it does not place orders, issue payments or connect to ERP systems.
10. **No production assurance.** Authentication, authorization, tenant isolation, audit-grade logging, observability and deployment hardening are not yet implemented.

## Safe use

Use this release for coursework, code review, controlled experiments and prototype demonstrations only. Do not use recommendations for real procurement, food safety, cold-chain compliance or financial commitments.
