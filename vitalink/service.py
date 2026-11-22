from __future__ import annotations

from typing import Any

from .baselines import cheapest_nominal_greedy
from .config import (
    initial_inventory,
    product_map,
    products_config,
    scenarios_config,
    suppliers_config,
)
from .data import load_demand_history
from .forecast import evaluate_forecasts, forecast_catalog
from .optimizer import solve_procurement
from .scoring import supplier_scorecard
from .simulator import run_scenario_set


def _runtime_config() -> dict[str, Any]:
    return products_config()


def build_forecast(horizon_days: int | None = None) -> dict[str, Any]:
    config = _runtime_config()
    horizon = horizon_days or int(config["planning_horizon_days"])
    histories = load_demand_history()
    forecast = forecast_catalog(histories, horizon)
    return {
        "horizon_days": horizon,
        "forecast_by_sku": forecast,
        "demand_by_sku": {sku: item["total_units"] for sku, item in forecast.items()},
        "evaluation": evaluate_forecasts(histories),
        "data_provenance": {
            "kind": "synthetic",
            "file": "data/daily_demand.csv",
            "observations": sum(len(rows) for rows in histories.values()),
            "first_date": min(row["date"] for rows in histories.values() for row in rows).isoformat(),
            "last_date": max(row["date"] for rows in histories.values() for row in rows).isoformat(),
            "warning": "Generated for reproducible demonstration; not observed company demand.",
        },
    }


def create_plan(
    demand: dict[str, float] | None = None,
    inventory: dict[str, int] | None = None,
    *,
    horizon_days: int | None = None,
    storage_capacity_units: int | None = None,
    budget_inr: float | None = None,
    risk_aversion: float | None = None,
) -> dict[str, Any]:
    config = _runtime_config()
    forecast = build_forecast(horizon_days)
    selected_demand = demand or forecast["demand_by_sku"]
    selected_inventory = inventory or initial_inventory()
    horizon = horizon_days or int(config["planning_horizon_days"])
    return solve_procurement(
        products=product_map(),
        suppliers=suppliers_config(),
        inventory=selected_inventory,
        demand=selected_demand,
        horizon_days=horizon,
        storage_capacity_units=storage_capacity_units or int(config["storage_capacity_units"]),
        budget_inr=budget_inr,
        risk_aversion=float(config["risk_aversion"] if risk_aversion is None else risk_aversion),
        carbon_price_inr_per_kg=float(config["carbon_price_inr_per_kg"]),
    )


def build_overview() -> dict[str, Any]:
    config = _runtime_config()
    forecast = build_forecast()
    products = product_map()
    suppliers = suppliers_config()
    inventory = initial_inventory()
    demand = forecast["demand_by_sku"]
    horizon = int(config["planning_horizon_days"])
    storage = int(config["storage_capacity_units"])
    risk = float(config["risk_aversion"])
    carbon_price = float(config["carbon_price_inr_per_kg"])

    plan = solve_procurement(
        products, suppliers, inventory, demand,
        horizon_days=horizon,
        storage_capacity_units=storage,
        risk_aversion=risk,
        carbon_price_inr_per_kg=carbon_price,
    )
    baseline = cheapest_nominal_greedy(
        products, suppliers, inventory, demand,
        horizon_days=horizon,
        storage_capacity_units=storage,
        risk_aversion=risk,
        carbon_price_inr_per_kg=carbon_price,
    )
    comparison = {
        "optimized_milp": {
            "total_cost_inr": plan["kpis"]["total_cost_inr"],
            "service_level_percent": plan["kpis"]["service_level_percent"],
            "shortage_units": plan["kpis"]["expected_shortage_units"],
        },
        "cheapest_nominal_greedy": {
            "total_cost_inr": baseline["kpis"]["total_cost_inr"],
            "service_level_percent": baseline["kpis"]["service_level_percent"],
            "shortage_units": baseline["kpis"]["expected_shortage_units"],
        },
        "modeled_cost_delta_inr": round(
            baseline["kpis"]["total_cost_inr"] - plan["kpis"]["total_cost_inr"], 2
        ),
        "service_level_delta_pp": round(
            plan["kpis"]["service_level_percent"] - baseline["kpis"]["service_level_percent"], 2
        ),
        "caveat": "One synthetic instance only; repeat across seeds, scenarios and calibrated field data before drawing general conclusions.",
    }
    scenarios = run_scenario_set(
        scenarios_config(),
        products=products,
        suppliers=suppliers,
        inventory=inventory,
        demand=demand,
        horizon_days=horizon,
        storage_capacity_units=storage,
        risk_aversion=risk,
        carbon_price_inr_per_kg=carbon_price,
    )
    scorecard = supplier_scorecard(suppliers, products)
    histories = load_demand_history()
    history_maps = {
        sku: {row["date"]: row["demand"] for row in rows}
        for sku, rows in histories.items()
    }
    all_dates = sorted({row["date"] for rows in histories.values() for row in rows})
    observed = [
        {
            "date": day.isoformat(),
            "demand_units": sum(mapping.get(day, 0) for mapping in history_maps.values()),
        }
        for day in all_dates[-28:]
    ]
    forecast_daily = []
    for offset in range(horizon):
        day = None
        value = 0.0
        for item in forecast["forecast_by_sku"].values():
            value += item["daily"][offset]["demand_units"]
            day = item["daily"][offset]["date"]
        forecast_daily.append({"date": day, "demand_units": round(value, 2)})

    return {
        "project": "VITALINK",
        "subtitle": "Disruption-aware supply-chain digital twin",
        "currency": config["currency"],
        "planning_horizon_days": horizon,
        "data_provenance": forecast["data_provenance"],
        "forecast_evaluation": forecast["evaluation"],
        "forecast_by_sku": forecast["forecast_by_sku"],
        "plan": plan,
        "policy_comparison": comparison,
        "products": list(products.values()),
        "suppliers": suppliers,
        "supplier_scorecard": scorecard,
        "scenarios": scenarios,
        "chart": {"history": observed, "forecast": forecast_daily},
        "research_scope": {
            "current": [
                "Rolling-origin demand forecast baseline",
                "Integer supplier-SKU procurement planning",
                "Supplier capacity, MOQ, lead-time and warehouse constraints",
                "Reliability and carbon cost terms",
                "Greedy nominal-price policy comparator",
                "Deterministic what-if disruption scenarios",
            ],
            "planned": [
                "Perishable inventory age-bucket spoilage model",
                "Multi-warehouse transportation and allocation optimization",
                "Stochastic/robust optimization with service-level guarantees",
                "Calibration against partner-company data and external benchmarks",
            ],
        },
    }
