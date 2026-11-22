from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .config import WEB_DIR, initial_inventory, suppliers_config
from .optimizer import OptimizationError
from .service import build_forecast, build_overview, create_plan

app = FastAPI(
    title="VITALINK",
    description="Disruption-aware supply-chain digital twin and procurement decision support.",
    version="0.1.0",
)


class OptimizeRequest(BaseModel):
    demand: dict[str, float] | None = None
    inventory: dict[str, int] | None = None
    horizon_days: int = Field(default=7, ge=1, le=30)
    storage_capacity_units: int = Field(default=2600, ge=1)
    budget_inr: float | None = Field(default=None, ge=0)
    risk_aversion: float = Field(default=2.0, ge=0, le=20)


class ScenarioRequest(BaseModel):
    demand_multiplier: float = Field(default=1.25, ge=0.1, le=5)
    supplier_outage: str | None = None
    supplier_delay_id: str | None = None
    extra_lead_days: int = Field(default=0, ge=0, le=30)


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/style.css", include_in_schema=False)
def stylesheet() -> FileResponse:
    return FileResponse(WEB_DIR / "style.css", media_type="text/css")


@app.get("/app.js", include_in_schema=False)
def javascript() -> FileResponse:
    return FileResponse(WEB_DIR / "app.js", media_type="application/javascript")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "vitalink-api", "version": "0.1.0"}


@app.get("/api/overview")
def overview() -> dict[str, Any]:
    try:
        return build_overview()
    except (ValueError, OptimizationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/forecast")
def forecast(horizon_days: int = 7) -> dict[str, Any]:
    if not 1 <= horizon_days <= 30:
        raise HTTPException(status_code=422, detail="horizon_days must be between 1 and 30.")
    return build_forecast(horizon_days)


@app.post("/api/optimize")
def optimize(payload: OptimizeRequest) -> dict[str, Any]:
    try:
        return create_plan(
            payload.demand,
            payload.inventory or initial_inventory(),
            horizon_days=payload.horizon_days,
            storage_capacity_units=payload.storage_capacity_units,
            budget_inr=payload.budget_inr,
            risk_aversion=payload.risk_aversion,
        )
    except (ValueError, OptimizationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/simulate")
def simulate(payload: ScenarioRequest) -> dict[str, Any]:
    from .config import product_map, products_config
    from .simulator import run_scenario

    config = products_config()
    demand = build_forecast()["demand_by_sku"]
    supplier_ids = {supplier["supplier_id"] for supplier in suppliers_config()}
    if payload.supplier_outage and payload.supplier_outage not in supplier_ids:
        raise HTTPException(status_code=422, detail="Unknown supplier_outage id.")
    if payload.supplier_delay_id and payload.supplier_delay_id not in supplier_ids:
        raise HTTPException(status_code=422, detail="Unknown supplier_delay_id.")

    scenario = {
        "scenario_id": "CUSTOM",
        "name": "Custom user scenario",
        "description": "User-specified demand and supplier disruption.",
        "demand_multiplier": payload.demand_multiplier,
        "supplier_outage": payload.supplier_outage,
        "supplier_delay": (
            {"supplier_id": payload.supplier_delay_id, "extra_days": payload.extra_lead_days}
            if payload.supplier_delay_id else None
        ),
    }
    try:
        return run_scenario(
            scenario,
            products=product_map(),
            suppliers=suppliers_config(),
            inventory=initial_inventory(),
            demand=demand,
            horizon_days=int(config["planning_horizon_days"]),
            storage_capacity_units=int(config["storage_capacity_units"]),
            risk_aversion=float(config["risk_aversion"]),
            carbon_price_inr_per_kg=float(config["carbon_price_inr_per_kg"]),
        )
    except (ValueError, OptimizationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
