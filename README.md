# VITALINK — Disruption-Aware Supply-Chain Digital Twin

**An interdisciplinary research-engineering project combining Supply Chain Management (SCM), operations research, forecasting and software systems.**

VITALINK is a decision-support prototype for a simplified Indian food distribution network. It combines a transparent demand-forecast baseline, mixed-integer procurement optimization, supplier scoring and disruption what-if analysis in a web control tower.

> **Research honesty:** this repository currently uses synthetic demand and illustrative supplier terms. It is a reproducible technical prototype, not field-validated procurement software. The included optimization solves a defined finite model; it does not establish that the policy is better for real businesses.

## The problem

Food distribution businesses must balance product availability, working capital, supplier reliability, lead times, storage capacity and waste. Decisions made from nominal purchase price alone can create shortages or concentrate risk in a fragile supplier.

VITALINK asks:

**How should a food distributor procure inventory when demand, supplier reliability, lead time, capacity and carbon intensity all matter at once?**

The initial scope is one aggregate distribution warehouse supplied by a small supplier network, with four product categories: tomato, onion, rice and milk.

## What works in this release

| Capability | Implementation |
|---|---|
| Demand planning | Weekly-seasonal blended level baseline with rolling-origin holdout metrics |
| Procurement optimization | Integer supplier-SKU procurement model using SciPy MILP / HiGHS |
| SCM constraints | Supplier aggregate capacity, MOQ, lead-time feasibility, warehouse ending-stock capacity, optional cash budget |
| Supplier risk | Reliability-adjusted expected receipts and configurable risk premium |
| Sustainability | Emissions coefficients and configurable carbon price |
| Decision baseline | Cheapest nominal-price greedy supplier policy |
| Disruption digital twin | Demand spike, supplier outage, lead-time delay and compound scenario re-optimization |
| Supplier assessment | Transparent weighted reliability / lead time / price / carbon scorecard |
| Dashboard | Responsive control tower with forecasts, KPIs, order lines, SKU outlook, supplier scorecard and stress tests |
| API | FastAPI endpoints for overview, forecast, optimization and custom simulation |
| Engineering | pytest suite, Python CI matrix, Dockerfile and Compose |

## Launch locally

Requirements: Python 3.11 or newer.

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

pip install -e ".[dev]"
python scripts/generate_synthetic_data.py
pytest
uvicorn vitalink.api:app --reload
```

Open:

- Dashboard: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

Run with Docker:

```bash
docker compose up --build
```

## API examples

Forecast the next seven days:

```bash
curl "http://127.0.0.1:8000/api/forecast?horizon_days=7"
```

Re-optimize under a different risk policy and cash budget:

```bash
curl -X POST http://127.0.0.1:8000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{"horizon_days":7,"risk_aversion":3.5,"budget_inr":85000}'
```

Test a supplier outage and demand shock:

```bash
curl -X POST http://127.0.0.1:8000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"demand_multiplier":1.25,"supplier_outage":"FARM_COOP"}'
```

## Optimization model

For each supplier (i) and SKU (j), the model chooses integer order quantity (x_{ij}), binary order activation (y_{ij}), expected unmet demand (u_j), and expected ending inventory (v_j).

It minimizes purchase spend, reliability risk premium, carbon cost, fixed ordering cost, holding cost and shortage penalty:

[
\min \sum_{i,j}x_{ij}(c_{ij}+\lambda c_{ij}(1-r_i)+\gamma e_{ij})
+\sum_{i,j}f_i y_{ij}+\sum_j p_j u_j+\sum_j q_j v_j
]

Subject to inventory balance, supplier capacity, minimum order quantities, supplier-SKU activation, warehouse storage and optional budget constraints. See [docs/optimization-model.md](docs/optimization-model.md) for the complete formulation.

**Reliability is an expected-yield approximation.** The model estimates receipts as reliability multiplied by ordered quantity. This is not a stochastic guarantee or chance constraint. Discrete outage and lead-time shocks are modelled separately by scenario re-optimization.

## Experiments and evaluation

The included 480-row dataset has 120 daily observations for each of four products from 2025-01-01 to 2025-04-30. It is generated with a fixed seed and is not observed market or company data.

The forecast evaluation uses a rolling-origin holdout and reports MAE, WAPE, bias and seasonal-naive WAPE. The procurement comparator reports the MILP plan beside a transparent cheapest-nominal-price greedy heuristic, holding demand, inventory and model cost terms constant. The scenario lab runs baseline, demand spike, supplier outage, lead-time delay and compound shock.

These are experiments on synthetic assumptions. A meaningful academic claim requires multiple generated instances, sensitivity analysis, external solver/policy comparisons and real partner data with permission. See [docs/research-protocol.md](docs/research-protocol.md).

## Division of academic work

### Supply Chain Management contribution
- Define the network, product characteristics, procurement policies and business constraints.
- Elicit supplier evaluation weights and calibrate service-level / shortage / holding assumptions.
- Validate inventory, lead-time and capacity semantics with operations stakeholders.
- Interpret trade-offs in cost, availability, working capital, resilience and emissions.

### Computer Science / Operations Research contribution
- Implement data pipelines, forecast evaluation and reproducible experiments.
- Formulate and solve the mixed-integer optimization model.
- Build simulation, API, dashboard, test suite and CI.
- Run sensitivity analysis, profile scalability and document algorithmic limitations.

The project should be submitted as joint interdisciplinary work only when both contributions have actually been completed and reviewed.

## Repository map

```text
vitalink/
  api.py                 FastAPI application and web endpoints
  baselines.py           Greedy nominal-price comparator
  config.py              Product, supplier and scenario configuration
  data.py                Demand CSV loader
  forecast.py            Forecast and rolling-origin evaluation
  optimizer.py           Mixed-integer procurement optimization
  scoring.py             Transparent supplier scorecard
  service.py             Dashboard read model and orchestration
  simulator.py            What-if disruption engine
web/
  index.html              Control-tower interface
  app.js                  Dashboard rendering and API interactions
  style.css               Responsive visual system
data/
  daily_demand.csv        Deterministic synthetic demand history
  products.json           SKU and cost assumptions
  suppliers.json           Illustrative supplier attributes
  scenarios.json           Reproducible disruption scenarios
docs/
  scm-methodology.md
  optimization-model.md
  research-protocol.md
  limitations.md
tests/
  test_api.py
  test_data_and_scorecard.py
  test_forecast.py
  test_optimizer.py
  test_simulator.py
  test_baselines.py
```

## Roadmap

1. Multi-period inventory ageing, FEFO and product expiry / cold-chain spoilage.
2. Multi-echelon network flow with warehouse-to-store transportation, route capacity and delivery windows.
3. Stochastic demand and supplier disruption with scenario-based recourse or robust service-level constraints.
4. Forecast benchmarks (seasonal naive, exponential smoothing and tree-based models) with leakage-safe rolling evaluation.
5. Real anonymized/consented partner data, calibration interviews and sensitivity studies.
6. Comparative tests against established optimization and supply-chain planning tools.

## Safety and use

VITALINK does not place purchase orders, process payments, or connect to a live ERP. It is for coursework, engineering experiments and prototype demonstrations only. Do not use the generated recommendations for real procurement or food-safety decisions.

See [known limitations](docs/limitations.md), [data provenance](data/README.md), and [security policy](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).
