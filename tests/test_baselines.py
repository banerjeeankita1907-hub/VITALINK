from vitalink.baselines import cheapest_nominal_greedy
from vitalink.config import initial_inventory, product_map, products_config, suppliers_config
from vitalink.forecast import forecast_catalog
from vitalink.data import load_demand_history
from vitalink.optimizer import solve_procurement


def test_greedy_baseline_respects_capacity_and_reports_cost_and_service():
    products = {
        "A": {
            "name": "A",
            "unit_cost_reference": 10,
            "emissions_kg_per_unit": 0,
            "holding_cost_per_unit": 0,
            "stockout_penalty_per_unit": 100,
        }
    }
    suppliers = [
        {
            "supplier_id": "CHEAP",
            "name": "Cheap",
            "capacity_units": 30,
            "lead_time_days": 1,
            "reliability": 1,
            "fixed_order_cost": 0,
            "unit_costs": {"A": 5},
            "minimum_order_quantities": {"A": 10},
            "emissions_kg_per_unit": {"A": 0},
        },
        {
            "supplier_id": "SLOW",
            "name": "Slow",
            "capacity_units": 100,
            "lead_time_days": 9,
            "reliability": 1,
            "fixed_order_cost": 0,
            "unit_costs": {"A": 1},
            "minimum_order_quantities": {"A": 1},
            "emissions_kg_per_unit": {"A": 0},
        },
    ]
    result = cheapest_nominal_greedy(
        products, suppliers, {"A": 0}, {"A": 50},
        horizon_days=7, storage_capacity_units=100,
        risk_aversion=0, carbon_price_inr_per_kg=0,
    )
    assert len(result["orders"]) == 1
    assert result["orders"][0]["supplier_id"] == "CHEAP"
    assert result["orders"][0]["quantity_units"] == 30
    assert result["kpis"]["expected_shortage_units"] == 20


def test_default_instance_comparator_uses_same_forecast_inputs():
    config = products_config()
    demand = {
        sku: row["total_units"]
        for sku, row in forecast_catalog(
            load_demand_history(), int(config["planning_horizon_days"])
        ).items()
    }
    milp = solve_procurement(
        product_map(), suppliers_config(), initial_inventory(), demand,
        horizon_days=7,
        storage_capacity_units=int(config["storage_capacity_units"]),
        risk_aversion=float(config["risk_aversion"]),
        carbon_price_inr_per_kg=float(config["carbon_price_inr_per_kg"]),
    )
    baseline = cheapest_nominal_greedy(
        product_map(), suppliers_config(), initial_inventory(), demand,
        horizon_days=7,
        storage_capacity_units=int(config["storage_capacity_units"]),
        risk_aversion=float(config["risk_aversion"]),
        carbon_price_inr_per_kg=float(config["carbon_price_inr_per_kg"]),
    )
    assert milp["kpis"]["service_level_percent"] >= 0
    assert baseline["kpis"]["service_level_percent"] >= 0
    assert milp["kpis"]["total_cost_inr"] >= 0
    assert baseline["kpis"]["total_cost_inr"] >= 0
