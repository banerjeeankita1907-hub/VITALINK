# Supply-chain management methodology

## Case setting

The first demonstration is a simplified food distribution network serving a single consolidation warehouse from a small set of supplier archetypes in eastern India. The product mix is tomatoes, onions, rice and milk. Perishability matters to the business context, but the first optimizer does **not yet** model age-bucket spoilage; shelf-life attributes are retained in the product master for the next model stage.

## SCM concepts represented

- **Procurement:** supplier-specific purchase prices, minimum order quantities (MOQs), fixed order costs and supplier capacity.
- **Lead-time feasibility:** an offer is unavailable when its quoted lead time exceeds the planning window.
- **Inventory planning:** opening inventory, forecast demand, expected receipts, ending inventory and unmet demand are reconciled per SKU.
- **Service level:** expected fulfilled units divided by demand units, reported by SKU and for the whole planning window.
- **Supplier risk:** reliability is modelled as an expected delivery yield, while an explicit risk premium discourages fragile supply.
- **Sustainability:** supplier/product emissions are monetized with a configurable carbon price to make the trade-off visible.
- **Disruption management:** the what-if engine tests demand shocks, supplier outages and lead-time delays.

## Supplier evaluation scorecard

The screening score combines normalized reliability (35%), lead-time score (25%), relative price score (25%) and relative carbon score (15%). The weights are policy choices, not universal SCM constants. The score is shown separately from the optimizer's objective so a stakeholder can challenge the policy transparently.

For actual procurement, weights should be elicited from decision-makers and validated against late deliveries, defects, quality rejections, payment terms, geographic constraints and supplier concentration.

## Inventory assumptions

The initial model works over a single aggregate planning horizon and uses expected supplier receipts. It does not yet represent daily inventory ageing, batch-level expiry, minimum presentation stock, order calendars, backorders, or store-level demand allocation. The presence of `shelf_life_days` in the SKU master must not be mistaken for an implemented spoilage constraint.

## Working-capital and operational interpretation

The optimizer reports gross purchase spend, fixed ordering costs, reliability risk premium, carbon cost, holding cost and shortage penalty separately. These are decision-model components, not audited accounting costs. The shortage penalty is a proxy for lost margin, customer impact and emergency replenishment; it must be calibrated with a business partner before use.
