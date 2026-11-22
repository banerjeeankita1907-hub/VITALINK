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
        assert sum(row["weights"].values()) == 1.0
