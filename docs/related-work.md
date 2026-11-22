# Related concepts and reading guide

VITALINK draws on established operations-management and operations-research ideas; it does not claim to invent them.

## Supply-chain management

- Chopra, S. and Meindl, P., *Supply Chain Management: Strategy, Planning, and Operation*. Use this for network design, demand planning, sourcing, inventory and coordination concepts.
- Silver, E. A., Pyke, D. F. and Thomas, D. J., *Inventory and Production Management in Supply Chains*. Use this for inventory policies, service levels and replenishment logic.

## Forecasting

- Hyndman, R. J. and Athanasopoulos, G., *Forecasting: Principles and Practice*. Use this for time-series evaluation, rolling-origin validation, seasonal-naive benchmarks and forecast accuracy measures.

## Optimization and simulation

- Mixed-integer linear programming is a standard way to encode discrete order activation, MOQs and capacity constraints.
- Discrete-event simulation is a natural next step for representing day-by-day arrivals, inventory age and stockout dynamics; v0.1 currently uses aggregate-period scenario re-optimization rather than a day-level DES.

## Software implementation

- SciPy's `scipy.optimize.milp` is used as the optimization interface. Record the Python, SciPy and solver versions with every research run.
- FastAPI provides the HTTP interface; it is not part of the supply-chain mathematical contribution.

A literature review for a thesis or paper should retrieve exact editions, publication years and page numbers from the institution's library before citation. This guide is a starting point, not a substitute for a formal systematic review.
