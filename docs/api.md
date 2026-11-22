# API reference

The API is served by FastAPI. Interactive OpenAPI documentation is available at `/docs` when the service is running.

## `GET /health`

Liveness response for the API process.

## `GET /api/overview`

Returns the dashboard read model: forecast, rolling-origin metrics, MILP procurement plan, cheapest-nominal greedy comparator, supplier scorecard, scenarios and historical/forecast chart series.

## `GET /api/forecast?horizon_days=7`

Returns per-SKU daily and aggregate forecasts. The horizon must be 1–30 days.

## `POST /api/optimize`

Optional JSON fields:

- `demand`: map of SKU to planning-horizon demand units; omitted means use the generated-data forecast.
- `inventory`: opening inventory by SKU; omitted means use `data/products.json`.
- `horizon_days`: integer 1–30.
- `storage_capacity_units`: positive integer.
- `budget_inr`: optional non-negative gross procurement budget.
- `risk_aversion`: 0–20, multiplier on the expected supplier-failure premium.

Returns order lines, SKU inventory balance, service level, supplier utilization and objective cost breakdown.

## `POST /api/compare`

Accepts the same request fields as `POST /api/optimize`. Returns both the optimal MILP plan and a cheapest-nominal-price greedy baseline, run with matching demand, inventory, horizon, capacity, budget and cost-policy inputs, plus a side-by-side cost/service-level summary. The greedy policy is a heuristic, not an optimal benchmark.

## `POST /api/simulate`

Optional JSON fields:

- `demand_multiplier`: 0.1–5.0.
- `supplier_outage`: supplier identifier to make unavailable.
- `supplier_delay_id`: supplier whose lead time should be delayed.
- `extra_lead_days`: 0–30 additional days.

The API re-solves the planning model after applying the scenario. It does not simulate random shipment-level outcomes.
