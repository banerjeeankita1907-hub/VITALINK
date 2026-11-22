# Development roadmap

## v0.1 — Reproducible technical foundation
- [x] Synthetic SKU demand data and data provenance.
- [x] Forecast baseline and rolling-origin metrics.
- [x] MILP supplier procurement with capacity, MOQ, lead-time, storage and budget constraints.
- [x] Expected reliability and carbon price terms.
- [x] Greedy nominal-price policy comparator.
- [x] Supplier scorecard and disruption what-if engine.
- [x] FastAPI and control-tower dashboard.
- [x] Unit/API tests and CI.

## v0.2 — Perishability and day-by-day operations
- [ ] Age-bucket inventory state and FEFO issue rule.
- [ ] Expiry/spoilage and temperature excursion scenario.
- [ ] Shipment arrival schedule and lead-time uncertainty.
- [ ] Daily simulation trace with stockout and wastage metrics.
- [ ] Calibration of holding, lost-sales and spoilage costs with an SCM reviewer.

## v0.3 — Network design and robust planning
- [ ] Multiple distribution centres and retail demand nodes.
- [ ] Transportation lane costs, vehicle capacity and delivery windows.
- [ ] Multi-echelon allocation / transshipment model.
- [ ] Scenario-based stochastic recourse or robust optimization.
- [ ] Sensitivity analysis across fixed, published seeds.

## v1.0 — Research validation
- [ ] External baseline comparison with reproducible environment and solver versions.
- [ ] Real anonymized data under appropriate permission.
- [ ] Repeated runs, confidence intervals and ablation studies.
- [ ] Independent SCM and CS review.
- [ ] Deployment security, authentication, audit trail and monitoring.
