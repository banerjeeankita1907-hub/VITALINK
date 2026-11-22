#!/usr/bin/env python3
"""Regenerate the illustrative 120-day dataset using a deterministic LCG seed."""

from __future__ import annotations

import csv
import math
from datetime import date, timedelta
from pathlib import Path

SEED = 73191
PRODUCTS = [
    ("TOMATO", 88, 0.09, 0.025, 13),
    ("ONION", 72, 0.06, 0.012, 10),
    ("RICE", 48, 0.025, 0.018, 5),
    ("MILK", 138, 0.035, 0.01, 12),
]
WEEKLY = [0.94, 0.97, 0.99, 1.02, 1.07, 1.11, 1.04]


def main() -> None:
    seed = SEED

    def random_value() -> float:
        nonlocal seed
        seed = (1664525 * seed + 1013904223) & 0xFFFFFFFF
        return seed / 4294967296

    path = Path(__file__).resolve().parents[1] / "data" / "daily_demand.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    start = date(2025, 1, 1)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["date", "sku", "demand_units"])
        for offset in range(120):
            day = start + timedelta(days=offset)
            for sku, base, amplitude, trend, noise in PRODUCTS:
                # Match JavaScript Date.getUTCDay() used for the original dataset:
                # Python weekday() is Monday=0, while the synthetic weekly array is Sunday=0.
                weekday_index = (day.weekday() + 1) % 7
                seasonal = 1 + amplitude * math.sin((offset / 30) * math.pi * 2)
                growth = 1 + trend * offset / 120
                jitter = (random_value() * 2 - 1) * noise
                raw_demand = base * WEEKLY[weekday_index] * seasonal * growth + jitter
                demand = max(1, math.floor(raw_demand + 0.5))
                writer.writerow([day.isoformat(), sku, demand])


if __name__ == "__main__":
    main()
