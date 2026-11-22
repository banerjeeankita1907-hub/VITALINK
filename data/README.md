# Dataset provenance

`daily_demand.csv` contains 480 rows: 120 consecutive daily observations for each of four product categories (tomato, onion, rice and milk), from 2025-01-01 to 2025-04-30.

**All observations are synthetic.** They are generated from fixed category-level demand levels, weekly patterns, a small smooth trend and deterministic pseudo-random noise. They are not records from a retailer, farm, supplier, government agency or market.

Regenerate the file with:

```bash
python scripts/generate_synthetic_data.py
```

The deterministic seed is 73191. Synthetic data is suitable for software tests and reproducible demonstrations, not external claims about Indian food demand. Replace it with licensed, consented, cleaned field data before making business recommendations.
