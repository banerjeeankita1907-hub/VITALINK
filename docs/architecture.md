# Architecture

```text
Synthetic / partner demand + supplier and product master data
               |
               v
         Data validation
               |
        +------+------+
        |             |
        v             v
  Forecasting    Supplier scorecard
        |             |
        +------+------+
               |
               v
       Mixed-integer optimizer
               |
               v
       Procurement plan / KPIs
               |
       +-------+---------+
       |                 |
       v                 v
Scenario re-optimizer  Policy comparator
       |                 |
       +--------+--------+
                |
                v
          FastAPI layer
                |
                v
      Responsive control tower
```

## Module boundaries

- `data.py` handles CSV ingestion and typed date parsing.
- `forecast.py` owns the interpretable forecast and rolling-origin evaluation.
- `optimizer.py` owns the MILP decision variables, constraints, solver status and cost breakdown.
- `baselines.py` provides the intentionally simple comparison policy.
- `simulator.py` mutates supplier/demand scenario inputs and re-optimizes.
- `service.py` prepares a read model for the dashboard.
- `api.py` is a thin HTTP interface; it does not duplicate business logic.
- `web/` renders results and submits policy changes to the API.

The current architecture is single-warehouse and horizon-aggregated. Multi-echelon flow, day-by-day inventory aging and discrete-event replenishment are roadmap items, not hidden capabilities.
