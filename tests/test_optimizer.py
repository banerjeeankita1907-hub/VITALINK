from __future__ import annotations

from vitalink.optimizer import solve_procurement


PRODUCTS = {
    "A": {
        "name": "Test item",
        "emissions_kg_per_unit": 0.0,
        "holding_cost_per_unit": 0.1,
        "stockout_penalty_per_unit": 100.0,
    }
}


def supplier(
    supplier_id: str,
    *,
    price: float,
    capacity: int = 100,
    lead: int = 1,
    reliability: float = 1.0,
    moq: int = 10,
) -> dict:
    return {
        "supplier_id": supplier_id,
        "name": supplier_id,
        "capacity_units": capacity,
        "lead_time_days": lead,
        "reliability": reliability,
        "fixed_order_cost": 0.0,
        "unit_costs": {"A": price},
        "minimum_order_quantities": {"A": moq},
        "emissions_kg_per_unit": {"A": 0.0},
    }


def plan(suppliers: list[dict], *, demand: float = 100, budget: float | None = None, risk: float = 0):
    return solve_procurement(
        PRODUCTS,
        suppliers,
        {"A": 0},
        {"A": demand},
        horizon_days=7,
        storage_capacity_units=500,
        budget_inr=budget,
        risk_aversion=risk,
        carbon_price_inr_per_kg=0,
    )


def test_supplier_capacity_caps_orders_and_shortage_is_reported():
    result = plan([supplier("FAST", price=10, capacity=60)], demand=100)
    assert result["status"] == "optimal"
    assert sum(order["quantity_units"] for order in result["orders"]) == 60
    assert result["sku_results"]["A"]["expected_shortage_units"] == 40
    assert result["kpis"]["service_level_percent"] == 60


def test_supplier_beyond_horizon_is_excluded():
    result = plan([
        supplier("TOO_SLOW", price=1, capacity=100, lead=8),
        supplier("FAST", price=20, capacity=40, lead=2),
    ])
    assert {order["supplier_id"] for order in result["orders"]} == {"FAST"}
    assert sum(order["quantity_units"] for order in result["orders"]) == 40


def test_moq_is_enforced_and_model_can_choose_no_order():
    result = plan(
        [supplier("MOQ_SUPPLIER", price=100, capacity=100, moq=40)],
        demand=20,
    )
    assert result["orders"] == []
    assert result["sku_results"]["A"]["expected_shortage_units"] == 20


def test_budget_constraint_can_force_zero_procurement():
    result = plan([supplier("SUPPLIER", price=10)], demand=80, budget=0)
    assert result["orders"] == []
    assert result["sku_results"]["A"]["expected_shortage_units"] == 80


def test_reliability_risk_premium_can_change_supplier_choice():
    result = plan(
        [
            supplier("UNRELIABLE_CHEAP", price=10, reliability=0.5),
            supplier("RELIABLE", price=16, reliability=1.0),
        ],
        demand=50,
        risk=2,
    )
    assert {order["supplier_id"] for order in result["orders"]} == {"RELIABLE"}
    assert result["sku_results"]["A"]["expected_shortage_units"] == 0


def test_shortage_balance_does_not_artificially_discard_available_inventory():
    result = solve_procurement(
        PRODUCTS,
        [],
        {"A": 100},
        {"A": 60},
        horizon_days=7,
        storage_capacity_units=200,
        carbon_price_inr_per_kg=0,
    )
    assert result["sku_results"]["A"]["expected_shortage_units"] == 0
    assert result["sku_results"]["A"]["expected_ending_inventory_units"] == 40
