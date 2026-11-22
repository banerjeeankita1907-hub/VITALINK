# Procurement optimization model

## Sets and parameters

Let (i\in I) index suppliers and (j\in J) index SKUs. Inputs include (d_j) forecast demand, (h_j) opening inventory, (c_{ij}) price, (r_i) reliability, (e_{ij}) emissions per unit, (m_{ij}) minimum order quantity, (C_i) supplier capacity, (L_i) lead time, (H) horizon, and (W) warehouse capacity.

## Decision variables

- (x_{ij}\in\mathbb{Z}_{\ge0}): ordered quantity;
- (y_{ij}\in\{0,1\}): order-line activation;
- (u_j\ge0): expected unmet demand;
- (v_j\ge0): expected ending inventory.

Orders with (L_i>H) are unavailable.

## Objective

Minimize:

[
\sum_{i,j}x_{ij}\left(c_{ij}+\lambda c_{ij}(1-r_i)+\gamma e_{ij}\right)
+\sum_{i,j}f_i y_{ij}+\sum_j p_j u_j+\sum_j q_j v_j
]

where (lambda) is risk aversion, (gamma) the carbon price, (f_i) the fixed order charge, (p_j) the shortage penalty, and (q_j) the holding cost.

## Constraints

Inventory balance:

[
v_j-u_j-\sum_i r_i x_{ij}=h_j-d_j,\quad \forall j
]

This follows from opening stock plus expected receipts equalling fulfilled demand plus ending stock, where fulfilled demand is (d_j-u_j).

Supplier capacity:

[
\sum_j x_{ij}\le C_i,\quad \forall i
]

Order activation and MOQ:

[
x_{ij}\le M_{ij}y_{ij},\quad x_{ij}\ge m_{ij}y_{ij}
]

Warehouse capacity:

[
\sum_j v_j\le W
]

Optional procurement budget:

[
\sum_{i,j}c_{ij}x_{ij}+\sum_{i,j}f_i y_{ij}\le B
]

Purchase quantities and activation variables are integer/binary; expected shortage and ending inventory may be continuous because reliability-adjusted receipts can be fractional.

## Important modelling caveat

Reliability is used as an expected-yield approximation (r_i x_{ij}). This is not a chance constraint and does not guarantee service under random failures. Scenarios test discrete outages and delays by re-solving the model. A future stochastic/robust model should use scenario-indexed decisions, recourse, or distributionally robust constraints.

The implementation uses `scipy.optimize.milp` with HiGHS. An optimum applies only to this finite formulation when the solver reports optimal termination; it is not an optimality claim for a real-world network.
