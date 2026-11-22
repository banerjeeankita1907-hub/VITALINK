from vitalink.config import (
    initial_inventory,
    product_map,
    products_config,
    scenarios_config,
    suppliers_config,
)
from vitalink.forecast import forecast_catalog
from vitalink.data import load_demand_history
from vitalink.simulator import run_scenario_set


def test_scenario_set_includes_baseline_and_disruption_outcomes():
    config = products_config()
    histories = load_demand_history()
    forecasts = forecast_catalog(histories, int(config["planning_horizon_days"]))
    demand = {sku: item["total_units"] for sku, item in forecasts.items()}
    results = run_scenario_set(
        scenarios_config(),
        products=product_map(),
        suppliers=suppliers_config(),
        inventory=initial_inventory(),
        demand=demand,
        horizon_days=int(config["planning_horizon_days"]),
        storage_capacity_units=int(config["storage_capacity_units"]),
        risk_aversion=float(config["risk_aversion"]),
        carbon_price_inr_per_kg=float(config["carbon_price_inr_per_kg"]),
    )
    assert len(results) == 5
    assert results[0]["scenario_id"] == "BASELINE"
    assert all("service_level_percent" in result["kpis"] for result in results)
    assert all("cost_delta_vs_baseline_inr" in result for result in results)


def test_supplier_outage_changes_available_plan():
    config = products_config()
    histories = load_demand_history()
    forecasts = forecast_catalog(histories, int(config["planning_horizon_days"]))
    demand = {sku: item["total_units"] for sku, item in forecasts.items()}
    scenarios = [
        {"scenario_id": "BASELINE", "name": "Baseline", "description": "base", "demand_multiplier": 1},
        {"scenario_id": "OUTAGE", "name": "Outage", "description": "farm outage", "demand_multiplier": 1, "supplier_outage": "FARM_COOP"},
    ]
    results = run_scenario_set(
        scenarios,
        products=product_map(),
        suppliers=suppliers_config(),
        inventory=initial_inventory(),
        demand=demand,
        horizon_days=7,
        storage_capacity_units=2600,
        risk_aversion=2,
        carbon_price_inr_per_kg=0.75,
    )
    assert results[1]["scenario_id"] == "OUTAGE"
    assert results[1]["kpis"]["total_cost_inr"] >= 0
