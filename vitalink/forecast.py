from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def forecast_series(
    history: list[dict[str, Any]], horizon_days: int = 7
) -> list[dict[str, Any]]:
    """A transparent weekly-seasonal + recent-level forecast baseline.

    This is an explainable benchmark model, not a claim of state-of-the-art accuracy.
    """
    if horizon_days < 1 or horizon_days > 90:
        raise ValueError("horizon_days must be between 1 and 90.")
    if not history:
        raise ValueError("At least one historical observation is required.")

    ordered = sorted(history, key=lambda row: row["date"])
    values = [float(row["demand"]) for row in ordered]
    last_date = ordered[-1]["date"]
    recent_7 = values[-7:]
    prior_7 = values[-14:-7]
    recent_28 = values[-28:]
    weekday_buckets: dict[int, list[float]] = {day: [] for day in range(7)}
    for row in ordered[-56:]:
        weekday_buckets[row["date"].weekday()].append(float(row["demand"]))

    level = 0.45 * _mean(recent_7) + 0.20 * _mean(recent_28)
    trend_per_day = (_mean(recent_7) - _mean(prior_7)) / 7 if prior_7 else 0.0
    trend_cap = max(1.0, level * 0.05)
    trend_per_day = max(-trend_cap, min(trend_cap, trend_per_day))
    predictions = []
    for step in range(1, horizon_days + 1):
        target_date = last_date + timedelta(days=step)
        seasonal_values = weekday_buckets[target_date.weekday()]
        seasonal = _mean(seasonal_values) if seasonal_values else level
        raw = 0.45 * seasonal + 0.35 * _mean(recent_7) + 0.20 * _mean(recent_28)
        prediction = max(0.0, raw + trend_per_day * min(step, 7))
        predictions.append({
            "date": target_date.isoformat(),
            "demand_units": round(prediction, 2),
        })
    return predictions


def forecast_catalog(
    histories: dict[str, list[dict[str, Any]]], horizon_days: int = 7
) -> dict[str, dict[str, Any]]:
    output = {}
    for sku, records in sorted(histories.items()):
        predictions = forecast_series(records, horizon_days)
        output[sku] = {
            "daily": predictions,
            "total_units": round(sum(item["demand_units"] for item in predictions), 2),
            "average_daily_units": round(
                sum(item["demand_units"] for item in predictions) / horizon_days, 2
            ),
        }
    return output


def _one_step(history: list[dict[str, Any]]) -> float:
    return forecast_series(history, 1)[0]["demand_units"]


def evaluate_forecasts(
    histories: dict[str, list[dict[str, Any]]], holdout_days: int = 14
) -> dict[str, Any]:
    """Rolling-origin comparison against a seasonal-naive (t-7) baseline."""
    model_errors: list[float] = []
    baseline_errors: list[float] = []
    actual_total = 0.0
    model_signed = 0.0
    baseline_signed = 0.0
    per_sku = {}

    for sku, records in sorted(histories.items()):
        ordered = sorted(records, key=lambda row: row["date"])
        start = max(14, len(ordered) - holdout_days)
        actuals: list[float] = []
        predictions: list[float] = []
        baselines: list[float] = []
        for index in range(start, len(ordered)):
            history = ordered[:index]
            actual = float(ordered[index]["demand"])
            prediction = _one_step(history)
            baseline = float(ordered[index - 7]["demand"])
            actuals.append(actual)
            predictions.append(prediction)
            baselines.append(baseline)

        if not actuals:
            continue
        errors = [prediction - actual for prediction, actual in zip(predictions, actuals)]
        base_errors = [prediction - actual for prediction, actual in zip(baselines, actuals)]
        abs_error = sum(abs(error) for error in errors)
        base_abs_error = sum(abs(error) for error in base_errors)
        demand_sum = sum(actuals)
        model_errors.extend(abs(error) for error in errors)
        baseline_errors.extend(abs(error) for error in base_errors)
        actual_total += demand_sum
        model_signed += sum(errors)
        baseline_signed += sum(base_errors)
        per_sku[sku] = {
            "observations": len(actuals),
            "mae": round(abs_error / len(actuals), 2),
            "wape_percent": round(100 * abs_error / demand_sum, 2) if demand_sum else 0.0,
            "seasonal_naive_wape_percent": (
                round(100 * base_abs_error / demand_sum, 2) if demand_sum else 0.0
            ),
        }

    count = len(model_errors)
    model_abs = sum(model_errors)
    base_abs = sum(baseline_errors)
    return {
        "method": "weekly-seasonal blended level baseline",
        "holdout_days": holdout_days,
        "observations": count,
        "mae": round(model_abs / count, 2) if count else None,
        "wape_percent": round(100 * model_abs / actual_total, 2) if actual_total else None,
        "bias_units": round(model_signed / count, 2) if count else None,
        "seasonal_naive_wape_percent": (
            round(100 * base_abs / actual_total, 2) if actual_total else None
        ),
        "per_sku": per_sku,
        "interpretation": "Synthetic-data rolling-origin baseline; replace with field data before operational use.",
    }
