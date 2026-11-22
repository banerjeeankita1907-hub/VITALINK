from __future__ import annotations

from datetime import date, timedelta

from vitalink.forecast import evaluate_forecasts, forecast_series


def history(days: int = 70) -> list[dict]:
    start = date(2025, 1, 1)
    return [
        {"date": start + timedelta(days=index), "demand": 100 + (index % 7) * 5}
        for index in range(days)
    ]


def test_forecast_has_requested_horizon_and_nonnegative_values():
    result = forecast_series(history(), horizon_days=10)
    assert len(result) == 10
    assert all(item["demand_units"] >= 0 for item in result)
    assert result[0]["date"] == "2025-03-12"


def test_forecast_rejects_invalid_horizon_and_empty_history():
    import pytest

    with pytest.raises(ValueError):
        forecast_series(history(), horizon_days=0)
    with pytest.raises(ValueError):
        forecast_series([], horizon_days=7)


def test_rolling_origin_evaluation_reports_model_and_baseline():
    metrics = evaluate_forecasts({"A": history()}, holdout_days=14)
    assert metrics["observations"] == 14
    assert metrics["mae"] is not None
    assert metrics["wape_percent"] is not None
    assert metrics["seasonal_naive_wape_percent"] is not None
    assert "A" in metrics["per_sku"]
