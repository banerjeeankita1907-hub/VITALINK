from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date
from typing import Any

from .config import DATA_DIR


def load_demand_history() -> dict[str, list[dict[str, Any]]]:
    history: dict[str, list[dict[str, Any]]] = defaultdict(list)
    path = DATA_DIR / "daily_demand.csv"
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        expected = {"date", "sku", "demand_units"}
        if not expected.issubset(set(reader.fieldnames or [])):
            raise ValueError("Demand CSV must contain date, sku and demand_units columns.")
        for row in reader:
            parsed_date = date.fromisoformat(row["date"])
            demand = int(row["demand_units"])
            if demand < 0:
                raise ValueError("Demand observations must be non-negative.")
            history[row["sku"]].append({"date": parsed_date, "demand": demand})
    for sku, records in history.items():
        records.sort(key=lambda item: item["date"])
        if len({item["date"] for item in records}) != len(records):
            raise ValueError(f"Duplicate daily demand observation for {sku}.")
    return dict(history)
