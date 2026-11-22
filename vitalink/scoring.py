from __future__ import annotations

from typing import Any


def supplier_scorecard(
    suppliers: list[dict[str, Any]], products: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Transparent weighted supplier score by SKU; weights are decision-policy inputs."""
    rows = []
    weights = {"reliability": 0.35, "lead_time": 0.25, "price": 0.25, "carbon": 0.15}
    for sku, product in sorted(products.items()):
        candidates = [s for s in suppliers if sku in s.get("unit_costs", {}) and s["capacity_units"] > 0]
        if not candidates:
            continue
        prices = [float(s["unit_costs"][sku]) for s in candidates]
        emissions = [float(s.get("emissions_kg_per_unit", {}).get(sku, product["emissions_kg_per_unit"])) for s in candidates]
        lead_times = [float(s["lead_time_days"]) for s in candidates]
        min_lead, max_lead = min(lead_times), max(lead_times)
        min_price, max_price = min(prices), max(prices)
        min_carbon, max_carbon = min(emissions), max(emissions)
        for supplier in candidates:
            price = float(supplier["unit_costs"][sku])
            carbon = float(supplier.get("emissions_kg_per_unit", {}).get(sku, product["emissions_kg_per_unit"]))
            price_score = 1.0 if max_price == min_price else 1 - (price - min_price) / (max_price - min_price)
            carbon_score = 1.0 if max_carbon == min_carbon else 1 - (carbon - min_carbon) / (max_carbon - min_carbon)
            lead_score = (
                1.0 if max_lead == min_lead
                else (max_lead - float(supplier["lead_time_days"])) / (max_lead - min_lead)
            )
            components = {
                "reliability": float(supplier["reliability"]),
                "lead_time": lead_score,
                "price": price_score,
                "carbon": carbon_score,
            }
            score = 100 * sum(weights[key] * components[key] for key in weights)
            rows.append({
                "sku": sku,
                "supplier_id": supplier["supplier_id"],
                "supplier_name": supplier["name"],
                "score": round(score, 1),
                "components": {key: round(value, 3) for key, value in components.items()},
                "weights": weights,
                "policy_note": "Weighted screening score, not an objective truth; weights should be elicited with procurement stakeholders.",
            })
    return sorted(rows, key=lambda row: (row["sku"], -row["score"]))
