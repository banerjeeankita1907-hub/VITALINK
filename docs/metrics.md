# Metric definitions

## Forecasting

For actual demand (y_t) and forecast \(\hat y_t\):

- **MAE:** mean absolute error, \(\frac{1}{n}\sum_t |y_t-\hat y_t|\).
- **WAPE:** total absolute error divided by total actual demand, \(\frac{\sum_t |y_t-\hat y_t|}{\sum_t |y_t|}\times100\%\).
- **Bias:** mean signed error, \(\frac{1}{n}\sum_t(\hat y_t-y_t)\). Positive values indicate over-forecasting.

The current evaluation uses a rolling-origin 14-day holdout for each SKU and compares with a seasonal-naive t-7 value. It is a small synthetic-data diagnostic, not an external validation.

## Inventory and service

- **Expected fulfilled units:** demand units minus expected shortage units.
- **Service level:** expected fulfilled units divided by demand units.
- **Expected shortage:** demand remaining after opening inventory and reliability-adjusted receipts.
- **Expected ending inventory:** opening stock plus expected receipts less fulfilled demand.

## Cost

The optimizer's objective includes:
1. Gross purchase spend.
2. Supplier-reliability risk premium.
3. Carbon-price cost.
4. Fixed order-line charges.
5. Holding cost on expected ending inventory.
6. Shortage penalty.

All values are INR under the illustrative product/supplier parameters in `data/`. Cost is a decision-model proxy, not audited total landed cost or financial accounting.
