from vitalink.config import product_map, suppliers_config
from vitalink.data import load_demand_history
from vitalink.scoring import supplier_scorecard


def test_committed_synthetic_dataset_has_four_complete_series():
    histories = load_demand_history()
    assert set(histories) == {"TOMATO", "ONION", "RICE", "MILK"}
    assert all(len(rows) == 120 for rows in histories.values())
    assert all(row["demand"] > 0 for rows in histories.values() for row in rows)


def test_supplier_scorecard_is_transparent_and_sorted():
    scorecard = supplier_scorecard(suppliers_config(), product_map())
    assert scorecard
    for sku in product_map():
        rows = [row for row in scorecard if row["sku"] == sku]
        assert rows
        assert all(0 <= row["score"] <= 100 for row in rows)
        assert rows == sorted(rows, key=lambda row: -row["score"])
        assert all(sum(item["weights"].values()) == 1.0 for item in rows)


def test_identical_lead_times_receive_equal_nonzero_lead_component():
    suppliers = [
        {
            "supplier_id": "A",
            "name": "Supplier A",
            "capacity_units": 100,
            "lead_time_days": 2,
            "reliability": 0.9,
            "unit_costs": {"SKU": 10},
            "emissions_kg_per_unit": {"SKU": 0.2},
        },
        {
            "supplier_id": "B",
            "name": "Supplier B",
            "capacity_units": 100,
            "lead_time_days": 2,
            "reliability": 0.95,
            "unit_costs": {"SKU": 11},
            "emissions_kg_per_unit": {"SKU": 0.15},
        },
    ]
    products = {"SKU": {"emissions_kg_per_unit": 0.2}}
    rows = supplier_scorecard(suppliers, products)
    assert all(row["components"]["lead_time"] == 1.0 for row in rows)
