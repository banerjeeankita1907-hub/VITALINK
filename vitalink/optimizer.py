from __future__ import annotations

from typing import Any

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix


class OptimizationError(RuntimeError):
    """Raised when the procurement model cannot produce a usable plan."""


def solve_procurement(
    products: dict[str, dict[str, Any]],
    suppliers: list[dict[str, Any]],
    inventory: dict[str, int],
    demand: dict[str, float],
    *,
    horizon_days: int = 7,
    storage_capacity_units: float = 2600,
    budget_inr: float | None = None,
    risk_aversion: float = 2.0,
    carbon_price_inr_per_kg: float = 0.75,
    time_limit_seconds: float = 15,
) -> dict[str, Any]:
    """Solve an integer procurement plan with explicit operational constraints.

    Expected delivered volume is reliability * ordered quantity. This is a planning
    approximation, not a stochastic service-level guarantee; scenario simulation
    tests discrete outages and lead-time shocks separately.
    """
    skus = sorted(products)
    if not skus:
        raise ValueError("At least one product is required.")
    if horizon_days < 1:
        raise ValueError("horizon_days must be positive.")
    if storage_capacity_units <= 0:
        raise ValueError("storage_capacity_units must be positive.")
    if risk_aversion < 0 or carbon_price_inr_per_kg < 0:
        raise ValueError("Risk aversion and carbon price must be non-negative.")

    for sku in skus:
        if sku not in demand or sku not in inventory:
            raise ValueError(f"Demand and inventory must include SKU {sku}.")
        if float(demand[sku]) < 0 or int(inventory[sku]) < 0:
            raise ValueError(f"Demand and inventory for {sku} must be non-negative.")

    supplier_count = len(suppliers)
    product_count = len(skus)
    order_count = supplier_count * product_count
    variable_count = 2 * order_count + 2 * product_count

    def x_index(i: int, j: int) -> int:
        return i * product_count + j

    def y_index(i: int, j: int) -> int:
        return order_count + x_index(i, j)

    def shortage_index(j: int) -> int:
        return 2 * order_count + j

    def ending_index(j: int) -> int:
        return 2 * order_count + product_count + j

    objective = np.zeros(variable_count, dtype=float)
    lower_bounds = np.zeros(variable_count, dtype=float)
    upper_bounds = np.zeros(variable_count, dtype=float)
    integrality = np.zeros(variable_count, dtype=int)
    integrality[:2 * order_count] = 1

    active: dict[tuple[int, int], dict[str, float]] = {}
    for i, supplier in enumerate(suppliers):
        reliability = float(supplier["reliability"])
        if not 0 <= reliability <= 1:
            raise ValueError(f"Supplier {supplier['supplier_id']} reliability must be between 0 and 1.")
        capacity = max(0, int(supplier["capacity_units"]))
        for j, sku in enumerate(skus):
            idx = x_index(i, j)
            binary_idx = y_index(i, j)
            offered = sku in supplier.get("unit_costs", {})
            lead_ok = int(supplier["lead_time_days"]) <= horizon_days
            max_qty = min(capacity, int(supplier.get("sku_capacity_units", {}).get(sku, capacity)))
            if not offered or not lead_ok or max_qty <= 0:
                upper_bounds[idx] = 0
                upper_bounds[binary_idx] = 0
                continue

            price = float(supplier["unit_costs"][sku])
            emissions = float(supplier.get("emissions_kg_per_unit", {}).get(
                sku, products[sku]["emissions_kg_per_unit"]
            ))
            moq = int(supplier.get("minimum_order_quantities", {}).get(sku, 1))
            if price < 0 or emissions < 0 or moq < 1:
                raise ValueError(f"Supplier {supplier['supplier_id']} has invalid terms for {sku}.")
            upper_bounds[idx] = max_qty
            upper_bounds[binary_idx] = 1
            objective[idx] = (
                price
                + price * risk_aversion * (1 - reliability)
                + emissions * carbon_price_inr_per_kg
            )
            objective[binary_idx] = float(supplier.get("fixed_order_cost", 0))
            active[(i, j)] = {"max_qty": float(max_qty), "moq": float(moq)}

    for j, sku in enumerate(skus):
        upper_bounds[shortage_index(j)] = max(0.0, float(demand[sku]))
        upper_bounds[ending_index(j)] = storage_capacity_units
        objective[shortage_index(j)] = float(products[sku]["stockout_penalty_per_unit"])
        objective[ending_index(j)] = float(products[sku]["holding_cost_per_unit"])

    rows: list[np.ndarray] = []
    row_lower: list[float] = []
    row_upper: list[float] = []

    # Inventory + expected receipts = fulfilled demand + ending inventory.
    # Fulfilled demand is demand - unmet demand.
    for j, sku in enumerate(skus):
        row = np.zeros(variable_count, dtype=float)
        for i, supplier in enumerate(suppliers):
            if (i, j) in active:
                row[x_index(i, j)] = -float(supplier["reliability"])
        row[shortage_index(j)] = -1
        row[ending_index(j)] = 1
        rhs = float(inventory[sku]) - float(demand[sku])
        rows.append(row)
        row_lower.append(rhs)
        row_upper.append(rhs)

    for i, supplier in enumerate(suppliers):
        row = np.zeros(variable_count, dtype=float)
        for j in range(product_count):
            row[x_index(i, j)] = 1
        rows.append(row)
        row_lower.append(-np.inf)
        row_upper.append(float(max(0, int(supplier["capacity_units"]))))

    for (i, j), limits in active.items():
        x_idx = x_index(i, j)
        y_idx = y_index(i, j)
        link = np.zeros(variable_count, dtype=float)
        link[x_idx] = 1
        link[y_idx] = -limits["max_qty"]
        rows.append(link)
        row_lower.append(-np.inf)
        row_upper.append(0)

        minimum = np.zeros(variable_count, dtype=float)
        minimum[x_idx] = 1
        minimum[y_idx] = -limits["moq"]
        rows.append(minimum)
        row_lower.append(0)
        row_upper.append(np.inf)

    storage = np.zeros(variable_count, dtype=float)
    for j in range(product_count):
        storage[ending_index(j)] = 1
    rows.append(storage)
    row_lower.append(-np.inf)
    row_upper.append(float(storage_capacity_units))

    if budget_inr is not None:
        if budget_inr < 0:
            raise ValueError("budget_inr must be non-negative.")
        budget = np.zeros(variable_count, dtype=float)
        for i, supplier in enumerate(suppliers):
            for j, sku in enumerate(skus):
                if (i, j) in active:
                    budget[x_index(i, j)] = float(supplier["unit_costs"][sku])
                    budget[y_index(i, j)] = float(supplier.get("fixed_order_cost", 0))
        rows.append(budget)
        row_lower.append(-np.inf)
        row_upper.append(float(budget_inr))

    matrix = csr_matrix(np.vstack(rows))
    constraints = LinearConstraint(matrix, np.asarray(row_lower), np.asarray(row_upper))
    result = milp(
        c=objective,
        integrality=integrality,
        bounds=Bounds(lower_bounds, upper_bounds),
        constraints=constraints,
        options={"time_limit": float(time_limit_seconds), "presolve": True},
    )
    if not result.success or result.x is None:
        raise OptimizationError(f"Procurement optimizer did not find an optimal plan: {result.message}")

    vector = result.x
    orders = []
    supplier_totals = {supplier["supplier_id"]: 0 for supplier in suppliers}
    purchase_cost = risk_cost = carbon_cost = fixed_cost = 0.0
    expected_receipts = {sku: 0.0 for sku in skus}
    for i, supplier in enumerate(suppliers):
        for j, sku in enumerate(skus):
            if (i, j) not in active:
                continue
            quantity = int(round(vector[x_index(i, j)]))
            if quantity <= 0:
                continue
            reliability = float(supplier["reliability"])
            price = float(supplier["unit_costs"][sku])
            emissions = float(supplier.get("emissions_kg_per_unit", {}).get(
                sku, products[sku]["emissions_kg_per_unit"]
            ))
            fixed = float(supplier.get("fixed_order_cost", 0))
            receipt = quantity * reliability
            supplier_totals[supplier["supplier_id"]] += quantity
            expected_receipts[sku] += receipt
            purchase_cost += quantity * price
            risk_cost += quantity * price * risk_aversion * (1 - reliability)
            carbon_cost += quantity * emissions * carbon_price_inr_per_kg
            fixed_cost += fixed
            orders.append({
                "supplier_id": supplier["supplier_id"],
                "supplier_name": supplier["name"],
                "sku": sku,
                "quantity_units": quantity,
                "expected_receipt_units": round(receipt, 2),
                "lead_time_days": int(supplier["lead_time_days"]),
                "reliability": reliability,
                "unit_cost_inr": round(price, 2),
                "line_purchase_cost_inr": round(quantity * price, 2),
            })

    sku_results = {}
    total_demand = total_shortage = total_fulfilled = 0.0
    holding_cost = shortage_cost = 0.0
    for j, sku in enumerate(skus):
        unmet = max(0.0, float(vector[shortage_index(j)]))
        ending = max(0.0, float(vector[ending_index(j)]))
        required = float(demand[sku])
        fulfilled = max(0.0, required - unmet)
        total_demand += required
        total_shortage += unmet
        total_fulfilled += fulfilled
        holding_cost += ending * float(products[sku]["holding_cost_per_unit"])
        shortage_cost += unmet * float(products[sku]["stockout_penalty_per_unit"])
        sku_results[sku] = {
            "demand_units": round(required, 2),
            "opening_inventory_units": int(inventory[sku]),
            "expected_receipt_units": round(expected_receipts[sku], 2),
            "expected_shortage_units": round(unmet, 2),
            "expected_ending_inventory_units": round(ending, 2),
            "expected_fulfilled_units": round(fulfilled, 2),
            "service_level_percent": round(100 * fulfilled / required, 2) if required else 100.0,
        }

    total_cost = purchase_cost + risk_cost + carbon_cost + fixed_cost + holding_cost + shortage_cost
    return {
        "status": "optimal",
        "solver": "scipy.optimize.milp (HiGHS backend)",
        "currency": "INR",
        "horizon_days": horizon_days,
        "orders": sorted(orders, key=lambda row: (row["sku"], row["supplier_id"])),
        "sku_results": sku_results,
        "supplier_utilization": [
            {
                "supplier_id": supplier["supplier_id"],
                "supplier_name": supplier["name"],
                "capacity_units": int(supplier["capacity_units"]),
                "planned_units": supplier_totals[supplier["supplier_id"]],
                "utilization_percent": round(
                    100 * supplier_totals[supplier["supplier_id"]] / supplier["capacity_units"], 2
                ) if supplier["capacity_units"] else 0.0,
            }
            for supplier in suppliers
        ],
        "kpis": {
            "demand_units": round(total_demand, 2),
            "expected_fulfilled_units": round(total_fulfilled, 2),
            "expected_shortage_units": round(total_shortage, 2),
            "service_level_percent": round(100 * total_fulfilled / total_demand, 2) if total_demand else 100.0,
            "expected_ending_inventory_units": round(sum(
                row["expected_ending_inventory_units"] for row in sku_results.values()
            ), 2),
            "total_cost_inr": round(total_cost, 2),
        },
        "cost_breakdown_inr": {
            "purchase": round(purchase_cost, 2),
            "supplier_reliability_risk_premium": round(risk_cost, 2),
            "carbon": round(carbon_cost, 2),
            "fixed_order": round(fixed_cost, 2),
            "holding": round(holding_cost, 2),
            "shortage": round(shortage_cost, 2),
        },
        "assumptions": [
            "Supplier reliability is modelled as expected delivered quantity, not as a stochastic guarantee.",
            "All quantities are aggregated over the selected planning horizon.",
            "Demand is treated as deterministic within each optimization run; uncertainty is explored through scenarios.",
            "Perishable spoilage and multi-echelon transport allocation are planned extensions, not current optimizer constraints.",
        ],
        "solver_message": str(result.message),
        "objective_value_inr": round(float(result.fun), 2),
    }
