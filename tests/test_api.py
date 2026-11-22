from fastapi.testclient import TestClient

from vitalink.api import app

client = TestClient(app)


def test_health_and_dashboard_assets():
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/").status_code == 200
    assert client.get("/style.css").status_code == 200
    assert client.get("/app.js").status_code == 200


def test_forecast_endpoint():
    response = client.get("/api/forecast?horizon_days=5")
    assert response.status_code == 200
    payload = response.json()
    assert payload["horizon_days"] == 5
    assert set(payload["demand_by_sku"]) == {"TOMATO", "ONION", "RICE", "MILK"}


def test_overview_contains_plan_and_research_metadata():
    response = client.get("/api/overview")
    assert response.status_code == 200
    payload = response.json()
    assert payload["project"] == "VITALINK"
    assert payload["plan"]["status"] == "optimal"
    assert len(payload["scenarios"]) == 5
    assert payload["data_provenance"]["kind"] == "synthetic"


def test_optimize_endpoint_accepts_policy_controls():
    response = client.post("/api/optimize", json={"risk_aversion": 4.0, "horizon_days": 7})
    assert response.status_code == 200
    assert response.json()["status"] == "optimal"


def test_custom_simulation_rejects_unknown_supplier():
    response = client.post("/api/simulate", json={"supplier_outage": "MISSING"})
    assert response.status_code == 422
