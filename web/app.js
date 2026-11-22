const money = value => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value || 0);
const number = value => new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(value || 0);
const pct = value => `${Number(value || 0).toFixed(1)}%`;
let overview = null;

function setText(id, value) {
  const node = document.getElementById(id);
  if (node) node.textContent = value;
}
function cell(value, className = "") {
  const td = document.createElement("td");
  td.textContent = value;
  if (className) td.className = className;
  return td;
}
function drawDemandChart(chart) {
  const canvas = document.getElementById("demand-chart");
  const ctx = canvas.getContext("2d");
  const ratio = window.devicePixelRatio || 1;
  const width = canvas.clientWidth || 700;
  const height = 255;
  canvas.width = width * ratio;
  canvas.height = height * ratio;
  ctx.scale(ratio, ratio);
  ctx.clearRect(0, 0, width, height);
  const history = chart.history || [];
  const forecast = chart.forecast || [];
  const rows = [...history, ...forecast];
  const values = rows.map(item => item.demand_units);
  const max = Math.max(1, ...values) * 1.18;
  const pad = { left: 34, right: 12, top: 15, bottom: 27 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;
  const x = i => pad.left + (rows.length <= 1 ? 0 : (i / (rows.length - 1)) * plotW);
  const y = value => pad.top + plotH - (value / max) * plotH;
  ctx.font = "10px monospace";
  ctx.fillStyle = "#8297ad";
  ctx.strokeStyle = "#25384b";
  ctx.lineWidth = 1;
  for (let tick = 0; tick <= 4; tick += 1) {
    const v = max * tick / 4;
    const yy = y(v);
    ctx.beginPath(); ctx.moveTo(pad.left, yy); ctx.lineTo(width - pad.right, yy); ctx.stroke();
    ctx.fillText(number(v), 0, yy + 3);
  }
  const valuesLine = (points, color, dashed = false) => {
    if (!points.length) return;
    ctx.beginPath();
    points.forEach((item, i) => {
      const xi = x(i + (dashed ? history.length - 1 : 0));
      const yi = y(item.demand_units);
      if (i === 0) ctx.moveTo(xi, yi); else ctx.lineTo(xi, yi);
    });
    ctx.strokeStyle = color; ctx.lineWidth = 2.2; ctx.setLineDash(dashed ? [5, 4] : []);
    ctx.stroke(); ctx.setLineDash([]);
  };
  valuesLine(history, "#6abaff");
  valuesLine([...(history.length ? [history.at(-1)] : []), ...forecast], "#59dfb2", true);
  ctx.fillStyle = "#8297ad";
  const labels = [rows[0], rows[Math.floor(rows.length / 2)], rows.at(-1)].filter(Boolean);
  labels.forEach((item, i) => ctx.fillText(item.date, pad.left + i * (plotW / 2), height - 6));
  const splitX = x(Math.max(0, history.length - 1));
  ctx.strokeStyle = "#547168"; ctx.setLineDash([3, 5]); ctx.beginPath(); ctx.moveTo(splitX, pad.top); ctx.lineTo(splitX, pad.top + plotH); ctx.stroke(); ctx.setLineDash([]);
}

function renderOrders(plan) {
  const body = document.getElementById("orders-body");
  body.replaceChildren();
  for (const order of plan.orders) {
    const tr = document.createElement("tr");
    tr.append(cell(order.supplier_name));
    tr.append(cell(order.sku));
    tr.append(cell(number(order.quantity_units), "qty"));
    tr.append(cell(`${order.lead_time_days} d`));
    tr.append(cell(number(order.expected_receipt_units)));
    body.append(tr);
  }
  if (!plan.orders.length) body.append(cell("No procurement required for this horizon.")); 
  setText("order-count", `${plan.orders.length} LINES`);
}

function renderSku(plan) {
  const body = document.getElementById("sku-body");
  body.replaceChildren();
  for (const [sku, row] of Object.entries(plan.sku_results)) {
    const tr = document.createElement("tr");
    tr.append(cell(sku));
    tr.append(cell(number(row.demand_units)));
    tr.append(cell(number(row.expected_shortage_units), row.expected_shortage_units > 0 ? "service-warn" : ""));
    tr.append(cell(number(row.expected_ending_inventory_units)));
    tr.append(cell(pct(row.service_level_percent), row.service_level_percent >= 98 ? "service-good" : "service-warn"));
    body.append(tr);
  }
}

function renderSuppliers(scorecard, suppliers) {
  const body = document.getElementById("supplier-body");
  body.replaceChildren();
  const map = new Map(suppliers.map(s => [s.supplier_id, s]));
  for (const row of scorecard) {
    const supplier = map.get(row.supplier_id);
    const tr = document.createElement("tr");
    tr.append(cell(row.supplier_name));
    tr.append(cell(row.sku));
    tr.append(cell(row.score.toFixed(1), "qty"));
    tr.append(cell(pct(supplier.reliability * 100)));
    tr.append(cell(`${supplier.lead_time_days} d`));
    body.append(tr);
  }
}

function renderScenarios(scenarios) {
  const grid = document.getElementById("scenario-grid");
  grid.replaceChildren();
  for (const scenario of scenarios) {
    const card = document.createElement("article");
    card.className = "scenario-card" + (scenario.scenario_id === "BASELINE" ? " baseline" : "");
    const title = document.createElement("h3"); title.textContent = scenario.name;
    const desc = document.createElement("p"); desc.textContent = scenario.description;
    const metric = document.createElement("div"); metric.className = "scenario-metric"; metric.textContent = pct(scenario.kpis.service_level_percent);
    const label = document.createElement("span"); label.className = "scenario-label"; label.textContent = "EXPECTED SERVICE LEVEL";
    const delta = document.createElement("div"); delta.className = "delta";
    delta.textContent = scenario.cost_delta_vs_baseline_inr === 0 ? "Baseline reference" : `${scenario.cost_delta_vs_baseline_inr > 0 ? "+" : "−"}${money(Math.abs(scenario.cost_delta_vs_baseline_inr))} vs baseline`;
    card.append(title, desc, metric, label, delta);
    grid.append(card);
  }
}

function renderOverview(data) {
  overview = data;
  const kpis = data.plan.kpis;
  setText("kpi-demand", number(kpis.demand_units));
  setText("kpi-service", pct(kpis.service_level_percent));
  setText("kpi-cost", money(kpis.total_cost_inr));
  setText("kpi-shortage", number(kpis.expected_shortage_units));
  setText("horizon-label", `${data.planning_horizon_days}-DAY`);
  setText("last-updated", `UPDATED ${new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})}`);
  setText("data-range", `${data.data_provenance.first_date} — ${data.data_provenance.last_date}`);
  setText("forecast-wape", data.forecast_evaluation.wape_percent === null ? "—" : pct(data.forecast_evaluation.wape_percent));
  setText("forecast-mae", data.forecast_evaluation.mae === null ? "—" : data.forecast_evaluation.mae.toFixed(2) + " units");
  setText("forecast-baseline", data.forecast_evaluation.seasonal_naive_wape_percent === null ? "—" : pct(data.forecast_evaluation.seasonal_naive_wape_percent));
  setText("forecast-note", `Rolling-origin holdout: ${data.forecast_evaluation.observations} observations. ${data.forecast_evaluation.interpretation}`);
  renderOrders(data.plan);
  renderSku(data.plan);
  renderSuppliers(data.supplier_scorecard, data.suppliers);
  renderScenarios(data.scenarios);
  drawDemandChart(data.chart);
}

async function loadOverview() {
  setText("optimizer-status", "Loading forecast, supplier network and optimization…");
  const response = await fetch("/api/overview");
  if (!response.ok) throw new Error(await response.text());
  renderOverview(await response.json());
  setText("optimizer-status", "Optimizer ready. Change risk aversion or add a budget cap to rerun.");
}

async function optimize() {
  if (!overview) return;
  const button = document.getElementById("optimize-button");
  button.disabled = true;
  button.textContent = "Solving model…";
  setText("optimizer-status", "Solving mixed-integer procurement model…");
  try {
    const budgetRaw = document.getElementById("budget-input").value;
    const payload = {
      demand: Object.fromEntries(Object.entries(overview.forecast_by_sku).map(([sku, item]) => [sku, item.total_units])),
      horizon_days: overview.planning_horizon_days,
      storage_capacity_units: 2600,
      risk_aversion: Number(document.getElementById("risk-slider").value)
    };
    if (budgetRaw !== "") payload.budget_inr = Number(budgetRaw);
    const response = await fetch("/api/optimize", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || "Optimization failed");
    overview.plan = result;
    const kpis = result.kpis;
    setText("kpi-demand", number(kpis.demand_units));
    setText("kpi-service", pct(kpis.service_level_percent));
    setText("kpi-cost", money(kpis.total_cost_inr));
    setText("kpi-shortage", number(kpis.expected_shortage_units));
    renderOrders(result); renderSku(result);
    setText("optimizer-status", `Optimal plan found. Objective: ${money(result.objective_value_inr)}. ${result.solver_message}`);
  } catch (error) {
    setText("optimizer-status", error.message);
  } finally {
    button.disabled = false;
    button.innerHTML = 'Re-optimize procurement <span>↗</span>';
  }
}

document.getElementById("risk-slider").addEventListener("input", event => setText("risk-value", Number(event.target.value).toFixed(1) + "×"));
document.getElementById("optimize-button").addEventListener("click", optimize);
window.addEventListener("resize", () => { if (overview) drawDemandChart(overview.chart); });
loadOverview().catch(error => {
  setText("optimizer-status", error.message);
  setText("last-updated", "API UNAVAILABLE");
});
