from __future__ import annotations

from math import ceil, floor
from typing import Any


def cheapest_nominal_greedy(
    products: dict[str, dict[str, Any]],
    suppliers: list[dict[str, Any]],
    inventory: dict[str, int],
    demand: dict[str, float],
    *,
    horizon_days: int,
    storage_capacity_units: int,
    risk_aversion: float = 2.0,
    carbon_price_inr_per_kg: float = 0.75,
) -> dict[str, Any]:
    """A deliberately simple benchmark: cheapest nominal offers, one-pass greedy fill.

    It observes lead times, supplier capacity, MOQs and storage, but it does not
    co-optimize supplier reliability, fixed ordering trade-offs, carbon, or all
    SKU allocations simultaneously. It exists as a transparent baseline.
    """
    remaining_capacity = {
        supplier["supplier_id"]: int(supplier["capacity_units"])
        for supplier in suppliers
    }
    ordered_suppliers = {supplier["supplier_id"]: supplier for supplier in suppliers}
    sku_order = sorted(
        products,
        key=lambda sku: (
            -float(products[sku]["stockout_penalty_per_unit"])
            / max(0.01, float(products[sku]["unit_cost_reference"]))
        ),
    )
    ending_by_sku: dict[str, float] = {}
    shortage_by_sku: dict[str, float] = {}
    receipts_by_sku: dict[str, float] = {}
    orders = []
    ending_total = 0.0
    purchase = risk = carbon = fixed = holding = shortage_cost = 0.0

    for sku in sku_order:
        product = products[sku]
        required = float(demand[sku])
        opening = float(inventory[sku])
        residual = max(0.0, required - opening)
        receipts = 0.0
        candidates = [
            supplier for supplier in suppliers
            if sku in supplier.get("unit_costs", {})
            and int(supplier["lead_time_days"]) <= horizon_days
            and float(supplier["reliability"]) > 0
        ]
        candidates.sort(key=lambda supplier: (
            float(supplier["unit_costs"][sku]),
            int(supplier["lead_time_days"]),
            -float(supplier["reliability"]),
            supplier["supplier_id"],
        ))

        for supplier in candidates:
            if residual <= 1e-9:
                break
            supplier_id = supplier["supplier_id"]
            available = remaining_capacity[supplier_id]
            reliability = float(supplier["reliability"])
            minimum = int(supplier.get("minimum_order_quantities", {}).get(sku, 1))
            if available < minimum:
                continue
            needed = ceil(residual / reliability)
            max_ending_receipt = max(
                0.0, float(storage_capacity_units) - ending_total - max(0.0, opening - required)
            )
            storage_limited = floor(max_ending_receipt / reliability + 1e-9)
            quantity = min(available, max(needed, minimum), storage_limited)
            if quantity < minimum:
                continue

            expected = quantity * reliability
            remaining_capacity[supplier_id] -= quantity
            receipts += expected
            residual = max(0.0, residual - expected)
            price = float(supplier["unit_costs"][sku])
            emissions = float(supplier.get("emissions_kg_per_unit", {}).get(
                sku, product["emissions_kg_per_unit"]
            ))
            fixed_line = float(supplier.get("fixed_order_cost", 0))
            purchase += quantity * price
            risk += quantity * price * risk_aversion * (1 - reliability)
            carbon += quantity * emissions * carbon_price_inr_per_kg
            fixed += fixed_line
            orders.append({
                "supplier_id": supplier_id,
                "supplier_name": supplier["name"],
                "sku": sku,
                "quantity_units": quantity,
                "expected_receipt_units": round(expected, 2),
                "lead_time_days": int(supplier["lead_time_days"]),
                "reliability": reliability,
                "unit_cost_inr": round(price, 2),
                "line_purchase_cost_inr": round(quantity * price, 2),
            })

        ending = max(0.0, opening + receipts - required)
        unmet = max(0.0, required - opening - receipts)
        ending_by_sku[sku] = ending
        shortage_by_sku[sku] = unmet
        receipts_by_sku[sku] = receipts
        ending_total += ending
        holding += ending * float(product["holding_cost_per_unit"])
        shortage_cost += unmet * float(product["stockout_penalty_per_unit"])

    total_demand = sum(float(value) for value in demand.values())
    total_shortage = sum(shortage_by_sku.values())
    fulfilled = total_demand - total_shortage
    total_cost = purchase + risk + carbon + fixed + holding + shortage_cost
    sku_results = {
        sku: {
            "demand_units": round(float(demand[sku]), 2),
            "opening_inventory_units": int(inventory[sku]),
            "expected_receipt_units": round(receipts_by_sku[sku], 2),
            "expected_shortage_units": round(shortage_by_sku[sku], 2),
            "expected_ending_inventory_units": round(ending_by_sku[sku], 2),
            "expected_fulfilled_units": round(float(demand[sku]) - shortage_by_sku[sku], 2),
            "service_level_percent": round(
                100 * (float(demand[sku]) - shortage_by_sku[sku]) / float(demand[sku]), 2
            ) if float(demand[sku]) else 100.0,
        }
        for sku in products
    }
    utilization = [
        {
            "supplier_id": supplier["supplier_id"],
            "supplier_name": supplier["name"],
            "capacity_units": int(supplier["capacity_units"]),
            "planned_units": int(supplier["capacity_units"]) - remaining_capacity[supplier["supplier_id"]],
            "utilization_percent": round(
                100 * (int(supplier["capacity_units"]) - remaining_capacity[supplier["supplier_id"]])
                / int(supplier["capacity_units"]), 2
            ) if int(supplier["capacity_units"]) else 0.0,
        }
        for supplier in suppliers
    ]
    return {
        "method": "cheapest nominal supplier, greedy SKU fill",
        "status": "heuristic",
        "orders": sorted(orders, key=lambda row: (row["sku"], row["supplier_id"])),
        "sku_results": sku_results,
        "supplier_utilization": utilization,
        "kpis": {
            "demand_units": round(total_demand, 2),
            "expected_fulfilled_units": round(fulfilled, 2),
            "expected_shortage_units": round(total_shortage, 2),
            "service_level_percent": round(100 * fulfilled / total_demand, 2) if total_demand else 100.0,
            "expected_ending_inventory_units": round(ending_total, 2),
            "total_cost_inr": round(total_cost, 2),
        },
        "cost_breakdown_inr": {
            "purchase": round(purchase, 2),
            "supplier_reliability_risk_premium": round(risk, 2),
            "carbon": round(carbon, 2),
            "fixed_order": round(fixed, 2),
            "holding": round(holding, 2),
            "shortage": round(shortage_cost, 2),
        },
        "assumptions": [
            "Nominal price is the primary supplier-selection rule; reliability and carbon are costed after allocation.",
            "Capacity, minimum order quantity, lead-time and aggregate ending-stock capacity are respected.",
            "This greedy rule is a benchmark heuristic, not a mathematically optimal policy.",
        ],
    }


def compare_policy_plans(
    optimized: dict[str, Any], baseline: dict[str, Any]
) -> dict[str, Any]:
    optimized_cost = optimized["kpis"]["total_cost_inr"]
    baseline_cost = baseline["kpis"]["total_cost_inr"]
    return {
        "optimized_milp": optimized,
        "cheapest_nominal_greedy": baseline,
        "comparison": {
            "modeled_cost_delta_inr": round(baseline_cost - optimized_cost, 2),
            "optimized_service_level_percent": optimized["kpis"]["service_level_percent"],
            "baseline_service_level_percent": baseline["kpis"]["service_level_percent"],
            "service_level_delta_pp": round(
                optimized["kpis"]["service_level_percent"]
                - baseline["kpis"]["service_level_percent"], 2
            ),
            "interpretation": (
                "Positive modeled cost delta means the MILP objective is lower for this input."
                " A fair research comparison must report service level alongside cost."
            ),
        },
        "caveat": "A single synthetic instance is not evidence of general superiority. Repeat across seeds, scenarios and calibrated field data.",
    }
