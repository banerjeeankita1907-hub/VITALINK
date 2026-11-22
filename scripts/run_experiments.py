#!/usr/bin/env python3
"""Run the deterministic demo experiment and export machine-readable results."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import scipy

from vitalink.service import build_overview


def main() -> None:
    payload = build_overview()
    artifact = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "software": {
            "vitalink": "0.1.0",
            "scipy": scipy.__version__,
        },
        "data_provenance": payload["data_provenance"],
        "forecast_evaluation": payload["forecast_evaluation"],
        "policy_comparison": payload["policy_comparison"],
        "optimized_plan": payload["plan"],
        "scenarios": payload["scenarios"],
        "note": (
            "Deterministic model outputs on synthetic demand and illustrative supplier data. "
            "Not field evidence or an operational purchase recommendation."
        ),
    }
    destination = Path("reports")
    destination.mkdir(exist_ok=True)
    output_path = destination / "vitalink-demo-results.json"
    output_path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote reproducible demo summary to {output_path}")
    print(json.dumps(payload["policy_comparison"], indent=2))


if __name__ == "__main__":
    main()
