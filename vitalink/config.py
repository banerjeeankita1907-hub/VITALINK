from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
WEB_DIR = ROOT / "web"


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def products_config() -> dict[str, Any]:
    return _read_json(DATA_DIR / "products.json")


@lru_cache(maxsize=1)
def suppliers_config() -> list[dict[str, Any]]:
    return _read_json(DATA_DIR / "suppliers.json")["suppliers"]


@lru_cache(maxsize=1)
def scenarios_config() -> list[dict[str, Any]]:
    return _read_json(DATA_DIR / "scenarios.json")


def product_map() -> dict[str, dict[str, Any]]:
    return {item["sku"]: item for item in products_config()["products"]}


def initial_inventory() -> dict[str, int]:
    return {sku: int(item["initial_inventory"]) for sku, item in product_map().items()}
