from __future__ import annotations

from copy import deepcopy
from typing import Any

from .optimizer import solve_procurement


def run_scenario(
    scenario: dict[str, Any],
    *,
    products: dict[str, dict[str, Any]],
    suppliers: list[dict[str, Any]],
    inventory: dict[str, int],
    demand: dict[str, float],
    horizon_days: int,
    storage_capacity_units: int,
    risk_aversion: float,
    carbon_price_inr_per_kg: float,
) -> dict[str, Any]:
    adjusted_suppliers = deepcopy(suppliers)
    outage = scenario.get("supplier_outage")
    delay = scenario.get("supplier_delay")
    for supplier in adjusted_suppliers:
        if supplier["supplier_id"] == outage:
            supplier["capacity_units"] = 0
        if delay and supplier["supplier_id"] == delay["supplier_id"]:
            supplier["lead_time_days"] += int(delay["extra_days"])

    multiplier = float(scenario.get("demand_multiplier", 1.0))
    adjusted_demand = {sku: float(value) * multiplier for sku, value in demand.items()}
    plan = solve_procurement(
        products,
        adjusted_suppliers,
        inventory,
        adjusted_demand,
        horizon_days=horizon_days,
        storage_capacity_units=storage_capacity_units,
        risk_aversion=risk_aversion,
        carbon_price_inr_per_kg=carbon_price_inr_per_kg,
    )
    return {
        "scenario_id": scenario["scenario_id"],
        "name": scenario["name"],
        "description": scenario["description"],
        "demand_multiplier": multiplier,
        "supplier_outage": outage,
        "supplier_delay": delay,
        "kpis": plan["kpis"],
        "cost_breakdown_inr": plan["cost_breakdown_inr"],
        "orders": plan["orders"],
        "sku_results": plan["sku_results"],
    }


def run_scenario_set(
    scenarios: list[dict[str, Any]],
    *,
    products: dict[str, dict[str, Any]],
    suppliers: list[dict[str, Any]],
    inventory: dict[str, int],
    demand: dict[str, float],
    horizon_days: int,
    storage_capacity_units: int,
    risk_aversion: float,
    carbon_price_inr_per_kg: float,
) -> list[dict[str, Any]]:
    outcomes = [
        run_scenario(
            scenario,
            products=products,
            suppliers=suppliers,
            inventory=inventory,
            demand=demand,
            horizon_days=horizon_days,
            storage_capacity_units=storage_capacity_units,
            risk_aversion=risk_aversion,
            carbon_price_inr_per_kg=carbon_price_inr_per_kg,
        )
        for scenario in scenarios
    ]
    baseline_cost = next(
        item["kpis"]["total_cost_inr"]
        for item in outcomes
        if item["scenario_id"] == "BASELINE"
    )
    for item in outcomes:
        cost = item["kpis"]["total_cost_inr"]
        item["cost_delta_vs_baseline_inr"] = round(cost - baseline_cost, 2)
        item["service_level_change_pp"] = round(
            item["kpis"]["service_level_percent"]
            - next(
                base["kpis"]["service_level_percent"]
                for base in outcomes
                if base["scenario_id"] == "BASELINE"
            ),
            2,
        )
    return outcomes
