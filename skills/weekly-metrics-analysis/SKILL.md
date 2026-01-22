---
name: weekly-metrics-analysis
description: "Generate weekly product category revenue analysis with targets. Use when: weekly metrics report, WoW analysis, product category performance, feature growth contribution, delta to target, catalyst revenue. Triggers: weekly analysis, weekly metrics, WoW report, product category weekly, STAPLES."
---

# Weekly Product Category Metrics Analysis

Generate comprehensive weekly revenue analysis across product categories with WoW change, QTD vs plan, delta to targets, and customer-level insights. Includes catalyst revenue for AI/ML category.

## Workflow

### Step 1: Collect Parameters

**Ask user for output format:**

| Format | Description |
|--------|-------------|
| **Tables** | Structured tables with all metrics - best for data review and copy/paste to spreadsheets |
| **Narrative** | Long-form English paragraphs with detailed analysis - best for executive summaries and presentations |

**Ask user for date parameters:**

| Parameter | Example | Description |
|-----------|---------|-------------|
| Current Week Start | 2026-01-05 | Start of current week |
| Current Week End | 2026-01-11 | End of current week |
| Prior Week Start | 2025-12-29 | Start of prior week |
| Prior Week End | 2026-01-04 | End of prior week |
| QTD Start | 2025-11-01 | First day of quarter |

**Quarterly Reference (FY26):**
| Quarter | Start | End |
|---------|-------|-----|
| Q1 | 2025-02-01 | 2025-04-30 |
| Q2 | 2025-05-01 | 2025-07-31 |
| Q3 | 2025-08-01 | 2025-10-31 |
| Q4 | 2025-11-01 | 2026-01-31 |

**⚠️ STOP**: Confirm dates before proceeding.

### Step 2: Execute All Queries

Run all queries in parallel to gather data for the 8 required tables.

### Step 3: Generate Report

Compile into standard format with 8 tables, each followed by an Executive Summary.

**⚠️ STOP**: Present draft for review.

---

## Data Sources

| Table | Purpose |
|-------|---------|
| `finance.customer.fy26_product_category_revenue` | Actuals (daily revenue by feature/customer) |
| `finance.dev_sensitive.achatlani_nov_plan_vf` | QTD plan targets (legacy) |
| `finance.customer.catalyst_revenue_reporting` | Catalyst revenue actuals |
| `finance.dev_sensitive.catalyst_plan` | Catalyst plan |
| `finance.customer.product_category_rev_actuals_w_forecast_sfdc` | Actuals with forecast |
| `finance.customer.product_category_revenue_forecast_sfdc_temp` | Revenue forecast |
| `finance.raw_google_sheets.fy_26_product_category_feature_targets` | Target revenue by feature |
| `finance.customer.plan_vs_most_recent_estimate` | Plan metadata (max forecast date) |
| `finance.stg_utils.stg_fiscal_calendar` | Fiscal calendar |
| `finance.prep_customer.product_feature_forecast_aligned_view` | **Forecast evolution over time** |

**Key Columns:** `ds`, `product_category`, `use_case`, `feature`, `revenue`, `latest_salesforce_account_name`

---

## Required Tables (FORMAT A: TABLES)

### ⚠️ CRITICAL TABLE FORMATTING RULES ⚠️

**RULE 1: NO ROUNDING** - Show full precision values.
**RULE 2: DISPLAY ALL COLUMNS** - Every table MUST display ALL columns from the query.
**RULE 3: NO COLUMN SHORTCUTS** - Do not combine or skip columns.
**RULE 4: TOTAL ROW REQUIRED** - Every table MUST include a **Total** row **AT THE BOTTOM** summing numeric columns (revenue, changes). For percentage columns, calculate the weighted average or sum as appropriate. The Total row must ALWAYS be the LAST row in every table.
**RULE 5: SORT ORDER** - Sort data rows by absolute WoW change or revenue (descending), then place Total row at the end.
**RULE 6: EXECUTIVE SUMMARY** - Every table MUST be followed by an **Executive Summary** paragraph interpreting the key insights.

---

### Table 1: FQ Y/Y Growth Forecast Evolution (FY2026-Q4)

**Purpose:** Show how the full quarter Y/Y growth forecast has evolved over time by product category. This is the most important table - it shows the trend.

| Run Date | Total | Data Eng | Analytics | Platform | Apps & Collab | AI/ML |
|----------|-------|----------|-----------|----------|---------------|-------|
| Nov 11 | 33.32% | 25.51% | 26.84% | 42.54% | 65.24% | 328.08% |
| Nov 18 | 34.48% | 26.49% | 28.57% | 44.50% | 66.38% | 312.53% |
| ... | ... | ... | ... | ... | ... | ... |
| **Jan 19** | **31.87%** | **24.57%** | **25.25%** | **41.58%** | **64.39%** | **296.58%** |
| **Δ from Start** | **-1.45pp** | **-0.94pp** | **-1.59pp** | **-0.96pp** | **-0.85pp** | **-31.50pp** |

**Executive Summary template:** Total FQ Y/Y growth forecast has [increased/declined] from X% to Y%, a [+/-]Zpp [improvement/deterioration]. [Category] showed the largest [gain/decline] at [+/-]Xpp. The forecast has been trending [up/down] since [date].

---

### Table 2: QTD vs Plan by Category

| Category | QTD Actual | QTD Plan | QTD vs Plan % |
|----------|-----------|----------|---------------|
| Data Engineering | $530,917,360 | $532,963,831 | -0.38% |
| ... | ... | ... | ... |
| **Total** | **$1,072,129,165** | **$1,076,617,336** | **-0.42%** |

**Executive Summary template:** QTD is tracking [+/-]X% vs plan ($Xm [ahead/behind]). [Category] is the primary [contributor/drag] at [+/-]X% ($Xm). [Category] and [Category] are the only categories [ahead of/behind] plan.

---

### Table 3: Product Category Summary (WoW)

| Category | Prior Week | Current Week | WoW Change | WoW % |
|----------|------------|--------------|------------|-------|
| Analytics | $25,833,486 | $26,193,765 | +$360,279 | +1.39% |
| ... | ... | ... | ... | ... |
| **Total** | **$96,486,147** | **$97,379,681** | **+$893,534** | **+0.93%** |

**Executive Summary template:** Total revenue [grew/declined] [+/-]$Xk ([+/-]X% WoW). [Category] led [growth/decline] at [+/-]$Xk ([+/-]X%). [Category] showed the strongest percentage [growth/decline] at [+/-]X%. All [X] categories posted [positive/negative/mixed] WoW growth.

---

### Table 4: Full Quarter Forecast vs Plan vs Target

| Category | FQ Forecast | FQ Plan | FQ vs Plan % | FQ Target | FQ vs Target % |
|----------|-------------|---------|--------------|-----------|----------------|
| Data Engineering | $613,134,500 | $616,129,502 | -0.49% | $620,278,391 | -1.15% |
| ... | ... | ... | ... | ... | ... |
| **Total** | **$1,242,057,545** | **$1,247,070,009** | **-0.40%** | **$1,256,499,578** | **-1.15%** |

**Executive Summary template:** FQ forecast is [+/-]X% vs plan ($Xm gap) and [+/-]X% vs target ($Xm gap). [Category] is the standout at [+/-]X% vs target. [Category] poses the greatest risk at [+/-]X% vs target ($Xm gap). To close the gap, ~$Xm/day additional revenue needed over remaining X days.

---

### Table 5: Top 25 Customers

| Customer | Current Week | Prior Week | WoW Change | WoW % | YoY % | Mix % | Contribution % | Top Feature |
|----------|-------------|------------|------------|-------|-------|-------|----------------|-------------|
| DoorDash, Inc. | $1,377,278 | $1,341,153 | +$36,126 | +2.69% | +28.47% | 1.43% | 0.49% | DML |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
| **Total (Top 25)** | **$18,811,182** | **$18,747,273** | **+$63,909** | **+0.34%** | — | **19.53%** | **11.93%** | — |

**Executive Summary template:** Top 25 customers represent X% of total revenue ($Xm). [Customer] ([+/-]$Xk) and [Customer] ([+/-]$Xk) drove X% of total WoW movement. Notable YoY performers: [Customer] (+X%), [Customer] (+X%). [Feature] is the dominant feature across X of top 25 customers.

---

### Table 6: Top 15 Weekly Gainers

| Customer | Current Week | Prior Week | WoW Change | WoW % | YoY % | Mix % | Contribution % | Top Gaining Feature |
|----------|-------------|------------|------------|-------|-------|-------|----------------|---------------------|
| OpenAI OpCo, LLC | $935,887 | $831,286 | +$104,602 | +12.58% | +74.11% | 0.97% | 1.43% | DML |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
| **Total (Gainers)** | **$6,326,612** | **$5,536,572** | **+$790,041** | **+14.27%** | — | **6.57%** | **10.81%** | — |

**Executive Summary template:** Top 15 gainers added [+]$Xk collectively (X% of total WoW movement). [Feature] drove gains for X of top 15 customers. Notable new/expanding workloads: [Customer] (+X% on [Feature]). AI adoption signal: [Customer] +$Xk on [AI Feature].

---

### Table 7: Top 15 Weekly Contractors

| Customer | Current Week | Prior Week | WoW Change | WoW % | YoY % | Mix % | Contribution % | Top Contracting Feature |
|----------|-------------|------------|------------|-------|-------|-------|----------------|-------------------------|
| NielsenIQ | $1,067,981 | $1,256,174 | -$188,193 | -14.98% | +5.70% | 1.11% | 2.57% | DML |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
| **Total (Contractors)** | **$3,126,794** | **$3,991,136** | **-$864,343** | **-21.66%** | — | **3.25%** | **11.81%** | — |

**Executive Summary template:** Top 15 contractors lost [-]$Xk collectively (X% of total WoW movement). [Customer] ([-]$Xk) and [Customer] ([-]$Xk) alone account for X% of movement—both on [Feature] contraction. Churn signal: [Customer] went to $0 (-100%). Despite WoW declines, most contractors show positive YoY.

---

### Table 8: Product Category Weekly View (incl. Catalyst)

| Category | Prior Week | Current Week | WoW Change | WoW % | Mix % | Contribution % |
|----------|------------|--------------|------------|-------|-------|----------------|
| Data Engineering | $47,227,885 | $47,522,553 | +$294,668 | +0.62% | 48.80% | 32.98% |
| ... | ... | ... | ... | ... | ... | ... |
| **Total** | **$96,486,147** | **$97,379,681** | **+$893,534** | **+0.93%** | **100.00%** | **100.00%** |

**Executive Summary template:** [Category] contributed X% of WoW growth despite only X% mix—a Xx ratio indicating [strong/weak] momentum. [Category] shows the highest growth signal with X% contribution vs X% mix (Xx ratio). Total weekly revenue [crossed/remained below] $Xm.

---

## Key Queries

### Query 1: Forecast Evolution by Product Category (Y/Y Growth Over Time)

```sql
WITH run_dates AS (
    SELECT DISTINCT forecast_run_date AS run_date
    FROM finance.prep_customer.product_feature_forecast_aligned_view
    WHERE forecast_run_date >= '2025-08-01'
),
catalyst_realized AS (
    SELECT usage_day AS ds, 'AI/ML' AS product_category, SUM(catalyst_revenue) AS revenue
    FROM finance.customer.catalyst_revenue_reporting
    WHERE usage_day <= CURRENT_DATE - 2
    GROUP BY 1
),
catalyst_avg AS (
    SELECT AVG(revenue) AS avg_daily_revenue
    FROM catalyst_realized
    WHERE ds > (SELECT MAX(ds) - 14 FROM catalyst_realized)
),
base_actuals AS (
    SELECT rd.run_date, cal.fiscal_quarter_fyyyyy_qq AS fy_fq, product_category, SUM(wkld.revenue) AS revenue
    FROM run_dates AS rd
    JOIN finance.customer.fy26_product_category_revenue AS wkld ON wkld.ds <= rd.run_date
    JOIN finance.stg_utils.stg_fiscal_calendar AS cal ON cal._date = wkld.ds
    GROUP BY ALL
),
catalyst_actuals AS (
    SELECT rd.run_date, cal.fiscal_quarter_fyyyyy_qq AS fy_fq, 'AI/ML' AS product_category, SUM(cr.revenue) AS revenue
    FROM run_dates AS rd
    JOIN catalyst_realized cr ON cr.ds <= rd.run_date
    JOIN finance.stg_utils.stg_fiscal_calendar AS cal ON cal._date = cr.ds
    GROUP BY ALL
),
actuals AS (
    SELECT run_date, fy_fq, product_category, SUM(revenue) AS revenue
    FROM (SELECT * FROM base_actuals UNION ALL SELECT * FROM catalyst_actuals)
    GROUP BY ALL
),
base_forecasts AS (
    SELECT f.forecast_run_date AS run_date, cal.fiscal_quarter_fyyyyy_qq AS fy_fq, product_category, SUM(f.revenue) AS revenue
    FROM finance.prep_customer.product_feature_forecast_aligned_view AS f
    JOIN run_dates AS rd ON f.forecast_run_date = rd.run_date
    JOIN finance.stg_utils.stg_fiscal_calendar AS cal ON cal._date = f.calendar_date
    WHERE f.calendar_date > rd.run_date
    GROUP BY ALL
),
catalyst_forecasts AS (
    SELECT rd.run_date, cal.fiscal_quarter_fyyyyy_qq AS fy_fq, 'AI/ML' AS product_category, COUNT(*) * MAX(ca.avg_daily_revenue) AS revenue
    FROM run_dates AS rd
    CROSS JOIN catalyst_avg ca
    JOIN finance.stg_utils.stg_fiscal_calendar AS cal ON cal._date > rd.run_date AND cal._date <= '2026-01-31'
    GROUP BY rd.run_date, cal.fiscal_quarter_fyyyyy_qq
),
forecasts AS (
    SELECT run_date, fy_fq, product_category, SUM(revenue) AS revenue
    FROM (SELECT * FROM base_forecasts UNION ALL SELECT * FROM catalyst_forecasts)
    GROUP BY ALL
),
blended AS (
    SELECT * FROM actuals
    UNION ALL
    SELECT * FROM forecasts
),
prep AS (
    SELECT run_date, fy_fq, product_category, SUM(revenue) AS total_revenue,
        LAG(total_revenue, 4) OVER (PARTITION BY run_date, product_category ORDER BY fy_fq) AS prev_year_quarter_revenue,
        DIV0(total_revenue, prev_year_quarter_revenue) - 1 AS yoy_growth
    FROM blended
    GROUP BY ALL
),
total_base_actuals AS (
    SELECT rd.run_date, cal.fiscal_quarter_fyyyyy_qq AS fy_fq, SUM(wkld.revenue) AS revenue
    FROM run_dates AS rd
    JOIN finance.customer.fy26_product_category_revenue AS wkld ON wkld.ds <= rd.run_date
    JOIN finance.stg_utils.stg_fiscal_calendar AS cal ON cal._date = wkld.ds
    GROUP BY ALL
),
total_catalyst_actuals AS (
    SELECT rd.run_date, cal.fiscal_quarter_fyyyyy_qq AS fy_fq, SUM(cr.revenue) AS revenue
    FROM run_dates AS rd
    JOIN catalyst_realized cr ON cr.ds <= rd.run_date
    JOIN finance.stg_utils.stg_fiscal_calendar AS cal ON cal._date = cr.ds
    GROUP BY ALL
),
total_actuals AS (
    SELECT run_date, fy_fq, SUM(revenue) AS revenue
    FROM (SELECT * FROM total_base_actuals UNION ALL SELECT * FROM total_catalyst_actuals)
    GROUP BY ALL
),
total_base_forecasts AS (
    SELECT f.forecast_run_date AS run_date, cal.fiscal_quarter_fyyyyy_qq AS fy_fq, SUM(f.revenue) AS revenue
    FROM finance.prep_customer.product_feature_forecast_aligned_view AS f
    JOIN run_dates AS rd ON f.forecast_run_date = rd.run_date
    JOIN finance.stg_utils.stg_fiscal_calendar AS cal ON cal._date = f.calendar_date
    WHERE f.calendar_date > rd.run_date
    GROUP BY ALL
),
total_catalyst_forecasts AS (
    SELECT rd.run_date, cal.fiscal_quarter_fyyyyy_qq AS fy_fq, COUNT(*) * MAX(ca.avg_daily_revenue) AS revenue
    FROM run_dates AS rd
    CROSS JOIN catalyst_avg ca
    JOIN finance.stg_utils.stg_fiscal_calendar AS cal ON cal._date > rd.run_date AND cal._date <= '2026-01-31'
    GROUP BY rd.run_date, cal.fiscal_quarter_fyyyyy_qq
),
total_forecasts AS (
    SELECT run_date, fy_fq, SUM(revenue) AS revenue
    FROM (SELECT * FROM total_base_forecasts UNION ALL SELECT * FROM total_catalyst_forecasts)
    GROUP BY ALL
),
total_blended AS (
    SELECT * FROM total_actuals
    UNION ALL
    SELECT * FROM total_forecasts
),
total_prep AS (
    SELECT run_date, fy_fq, SUM(revenue) AS total_revenue,
        LAG(total_revenue, 4) OVER (PARTITION BY run_date ORDER BY fy_fq) AS prev_year_quarter_revenue,
        DIV0(total_revenue, prev_year_quarter_revenue) - 1 AS yoy_growth
    FROM total_blended
    GROUP BY ALL
)
SELECT run_date, product_category, ROUND(yoy_growth * 100, 2) AS yoy_growth_pct FROM prep WHERE fy_fq = 'FY2026-Q4'
UNION ALL
SELECT run_date, 'Total' AS product_category, ROUND(yoy_growth * 100, 2) AS yoy_growth_pct FROM total_prep WHERE fy_fq = 'FY2026-Q4'
ORDER BY 1, 2
```

### Query 2: QTD vs Plan (Date-Aligned)

```sql
WITH catalyst_realized AS (
    SELECT usage_day, 'AI/ML' AS product_category, SUM(catalyst_revenue) AS revenue
    FROM finance.customer.catalyst_revenue_reporting
    WHERE usage_day <= CURRENT_DATE - 2
    GROUP BY ALL
),
realized_revenue AS (
    SELECT ds, product_category, SUM(revenue) AS revenue
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds <= CURRENT_DATE - 2
    GROUP BY ALL
    UNION ALL
    SELECT usage_day AS ds, product_category, SUM(revenue) AS revenue
    FROM catalyst_realized
    GROUP BY ALL
),
max_realized_date AS (
    SELECT MAX(ds) AS max_ds FROM realized_revenue
),
qtd_actual AS (
    SELECT product_category, SUM(revenue) AS qtd_revenue
    FROM realized_revenue
    WHERE ds >= :qtd_start
    GROUP BY 1
),
plan_data AS (
    SELECT ds, product_category, SUM(revenue) AS revenue
    FROM finance.dev_sensitive.achatlani_nov_plan_vf
    GROUP BY ALL
    UNION ALL
    SELECT ds, product_category, SUM(revenue) AS revenue
    FROM finance.dev_sensitive.catalyst_plan
    GROUP BY ALL
),
qtd_plan AS (
    SELECT p.product_category, SUM(p.revenue) AS qtd_plan
    FROM plan_data p
    CROSS JOIN max_realized_date m
    WHERE p.ds >= :qtd_start 
      AND p.ds <= m.max_ds
    GROUP BY 1
)
SELECT 
    COALESCE(a.product_category, p.product_category) AS product_category,
    a.qtd_revenue,
    p.qtd_plan,
    (a.qtd_revenue / NULLIF(p.qtd_plan, 0)) - 1 AS qtd_pct_delta_to_plan,
    (SELECT max_ds FROM max_realized_date) AS qtd_end_date
FROM qtd_actual a
FULL OUTER JOIN qtd_plan p ON a.product_category = p.product_category
ORDER BY a.qtd_revenue DESC NULLS LAST
```

### Query 3: Product Category WoW Summary (with Catalyst)

```sql
WITH catalyst_realized AS (
    SELECT usage_day AS ds, 'AI/ML' AS product_category, SUM(catalyst_revenue) AS revenue
    FROM finance.customer.catalyst_revenue_reporting
    WHERE usage_day <= CURRENT_DATE - 2
    GROUP BY 1
),
base_current AS (
    SELECT product_category, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1
),
catalyst_current AS (
    SELECT product_category, SUM(revenue) AS current_rev
    FROM catalyst_realized
    WHERE ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1
),
current_week AS (
    SELECT product_category, SUM(current_rev) AS current_rev
    FROM (SELECT * FROM base_current UNION ALL SELECT * FROM catalyst_current)
    GROUP BY 1
),
base_prior AS (
    SELECT product_category, SUM(revenue) AS prior_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1
),
catalyst_prior AS (
    SELECT product_category, SUM(revenue) AS prior_rev
    FROM catalyst_realized
    WHERE ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1
),
prior_week AS (
    SELECT product_category, SUM(prior_rev) AS prior_rev
    FROM (SELECT * FROM base_prior UNION ALL SELECT * FROM catalyst_prior)
    GROUP BY 1
)
SELECT 
    COALESCE(c.product_category, p.product_category) AS product_category,
    COALESCE(p.prior_rev, 0) AS prior_week_rev,
    COALESCE(c.current_rev, 0) AS current_week_rev,
    COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS wow_change,
    100.0 * (COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0)) / NULLIF(p.prior_rev, 0) AS wow_pct
FROM current_week c
FULL OUTER JOIN prior_week p ON c.product_category = p.product_category
ORDER BY ABS(COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0)) DESC
```

### Query 4: Full Quarter Forecast vs Plan vs Target

```sql
WITH catalyst_realized AS (
    SELECT usage_day, 'AI/ML' AS product_category, SUM(catalyst_revenue) AS revenue
    FROM finance.customer.catalyst_revenue_reporting
    WHERE usage_day <= CURRENT_DATE - 2
    GROUP BY ALL
),
avg_daily_catalyst AS (
    SELECT AVG(revenue) AS avg_revenue
    FROM catalyst_realized
    WHERE usage_day > (SELECT MAX(usage_day) - 14 FROM catalyst_realized)
),
future_dates AS (
    SELECT DATEADD(day, seq4(), (SELECT MAX(usage_day) + 1 FROM catalyst_realized)) AS usage_day
    FROM TABLE(GENERATOR(ROWCOUNT => 100))
    WHERE usage_day <= '2026-01-31'
),
catalyst_forecast AS (
    SELECT fd.usage_day, 'AI/ML' AS product_category, adr.avg_revenue AS revenue
    FROM future_dates fd
    CROSS JOIN avg_daily_catalyst adr
),
catalyst_cte AS (
    SELECT * FROM catalyst_realized
    UNION ALL
    SELECT * FROM catalyst_forecast
),
fq_forecast AS (
    SELECT product_category, SUM(revenue) AS fq_revenue
    FROM finance.customer.product_category_rev_actuals_w_forecast_sfdc
    WHERE usage_date BETWEEN :qtd_start AND '2026-01-31'
    GROUP BY 1
    UNION ALL
    SELECT product_category, SUM(revenue) AS fq_revenue
    FROM catalyst_cte
    WHERE usage_day BETWEEN :qtd_start AND '2026-01-31'
    GROUP BY 1
),
fq_forecast_agg AS (
    SELECT product_category, SUM(fq_revenue) AS full_quarter_revenue
    FROM fq_forecast
    GROUP BY 1
),
fq_plan AS (
    SELECT product_category, SUM(revenue) AS full_quarter_plan
    FROM finance.dev_sensitive.achatlani_nov_plan_vf
    WHERE ds BETWEEN :qtd_start AND '2026-01-31'
    GROUP BY 1
    UNION ALL
    SELECT product_category, SUM(revenue) AS full_quarter_plan
    FROM finance.dev_sensitive.catalyst_plan
    WHERE ds BETWEEN :qtd_start AND '2026-01-31'
    GROUP BY 1
),
fq_plan_agg AS (
    SELECT product_category, SUM(full_quarter_plan) AS full_quarter_plan
    FROM fq_plan
    GROUP BY 1
),
fq_target AS (
    SELECT product_category, SUM(target_revenue) AS full_quarter_target
    FROM finance.raw_google_sheets.fy_26_product_category_feature_targets
    WHERE fiscal_quarter_fyyyyy_qq = 'FY2026-Q4'
    GROUP BY 1
)
SELECT 
    f.product_category,
    f.full_quarter_revenue,
    p.full_quarter_plan,
    (f.full_quarter_revenue / NULLIF(p.full_quarter_plan, 0)) - 1 AS fq_delta_to_plan,
    t.full_quarter_target,
    (f.full_quarter_revenue / NULLIF(t.full_quarter_target, 0)) - 1 AS fq_delta_to_target
FROM fq_forecast_agg f
LEFT JOIN fq_plan_agg p ON f.product_category = p.product_category
LEFT JOIN fq_target t ON f.product_category = t.product_category
ORDER BY f.full_quarter_revenue DESC NULLS LAST
```

### Query 5: Top 25 Customers

```sql
WITH current_week AS (
    SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1
),
prior_week AS (
    SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS prior_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1
),
prior_year AS (
    SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS py_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN DATEADD(year, -1, :current_week_start) AND DATEADD(year, -1, :current_week_end)
    GROUP BY 1
),
combined AS (
    SELECT COALESCE(c.customer, p.customer, py.customer) AS customer,
        COALESCE(c.current_rev, 0) AS current_rev,
        COALESCE(p.prior_rev, 0) AS prior_rev,
        COALESCE(py.py_rev, 0) AS py_rev,
        COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS wow_change
    FROM current_week c
    FULL OUTER JOIN prior_week p ON c.customer = p.customer
    FULL OUTER JOIN prior_year py ON COALESCE(c.customer, p.customer) = py.customer
),
totals AS (
    SELECT SUM(ABS(wow_change)) AS total_mag, SUM(current_rev) AS total_current FROM combined
),
top_feature AS (
    SELECT latest_salesforce_account_name AS customer, feature, SUM(revenue) AS feature_rev,
        ROW_NUMBER() OVER (PARTITION BY customer ORDER BY SUM(revenue) DESC) AS rn
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1, 2
)
SELECT c.customer, c.current_rev, c.prior_rev, c.wow_change,
    100.0 * c.wow_change / NULLIF(c.prior_rev, 0) AS wow_pct,
    100.0 * (c.current_rev - c.py_rev) / NULLIF(c.py_rev, 0) AS yoy_pct,
    100.0 * c.current_rev / NULLIF(t.total_current, 0) AS mix_pct,
    100.0 * ABS(c.wow_change) / NULLIF(t.total_mag, 0) AS contribution_pct,
    tf.feature AS top_feature
FROM combined c
CROSS JOIN totals t
LEFT JOIN top_feature tf ON c.customer = tf.customer AND tf.rn = 1
ORDER BY c.current_rev DESC
LIMIT 25
```

### Query 6: Top 15 Weekly Gainers (with Top Gaining Feature)

```sql
WITH current_week AS (
    SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1
),
prior_week AS (
    SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS prior_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1
),
prior_year AS (
    SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS py_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN DATEADD(year, -1, :current_week_start) AND DATEADD(year, -1, :current_week_end)
    GROUP BY 1
),
combined AS (
    SELECT COALESCE(c.customer, p.customer, py.customer) AS customer,
        COALESCE(c.current_rev, 0) AS current_rev,
        COALESCE(p.prior_rev, 0) AS prior_rev,
        COALESCE(py.py_rev, 0) AS py_rev,
        COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS wow_change
    FROM current_week c
    FULL OUTER JOIN prior_week p ON c.customer = p.customer
    FULL OUTER JOIN prior_year py ON COALESCE(c.customer, p.customer) = py.customer
),
totals AS (
    SELECT SUM(ABS(wow_change)) AS total_mag, SUM(current_rev) AS total_current FROM combined
),
feature_current AS (
    SELECT latest_salesforce_account_name AS customer, feature, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1, 2
),
feature_prior AS (
    SELECT latest_salesforce_account_name AS customer, feature, SUM(revenue) AS prior_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1, 2
),
feature_change AS (
    SELECT COALESCE(c.customer, p.customer) AS customer,
        COALESCE(c.feature, p.feature) AS feature,
        COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS feature_wow_change
    FROM feature_current c
    FULL OUTER JOIN feature_prior p ON c.customer = p.customer AND c.feature = p.feature
),
top_gaining_feature AS (
    SELECT customer, feature, feature_wow_change,
        ROW_NUMBER() OVER (PARTITION BY customer ORDER BY feature_wow_change DESC) AS rn
    FROM feature_change
)
SELECT c.customer, c.current_rev, c.prior_rev, c.wow_change,
    100.0 * c.wow_change / NULLIF(c.prior_rev, 0) AS wow_pct,
    100.0 * (c.current_rev - c.py_rev) / NULLIF(c.py_rev, 0) AS yoy_pct,
    100.0 * c.current_rev / NULLIF(t.total_current, 0) AS mix_pct,
    100.0 * ABS(c.wow_change) / NULLIF(t.total_mag, 0) AS contribution_pct,
    tgf.feature AS top_gaining_feature
FROM combined c
CROSS JOIN totals t
LEFT JOIN top_gaining_feature tgf ON c.customer = tgf.customer AND tgf.rn = 1
WHERE c.wow_change > 0
ORDER BY c.wow_change DESC
LIMIT 15
```

### Query 7: Top 15 Weekly Contractors (with Top Contracting Feature)

```sql
WITH current_week AS (
    SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1
),
prior_week AS (
    SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS prior_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1
),
prior_year AS (
    SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS py_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN DATEADD(year, -1, :current_week_start) AND DATEADD(year, -1, :current_week_end)
    GROUP BY 1
),
combined AS (
    SELECT COALESCE(c.customer, p.customer, py.customer) AS customer,
        COALESCE(c.current_rev, 0) AS current_rev,
        COALESCE(p.prior_rev, 0) AS prior_rev,
        COALESCE(py.py_rev, 0) AS py_rev,
        COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS wow_change
    FROM current_week c
    FULL OUTER JOIN prior_week p ON c.customer = p.customer
    FULL OUTER JOIN prior_year py ON COALESCE(c.customer, p.customer) = py.customer
),
totals AS (
    SELECT SUM(ABS(wow_change)) AS total_mag, SUM(current_rev) AS total_current FROM combined
),
feature_current AS (
    SELECT latest_salesforce_account_name AS customer, feature, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1, 2
),
feature_prior AS (
    SELECT latest_salesforce_account_name AS customer, feature, SUM(revenue) AS prior_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1, 2
),
feature_change AS (
    SELECT COALESCE(c.customer, p.customer) AS customer,
        COALESCE(c.feature, p.feature) AS feature,
        COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS feature_wow_change
    FROM feature_current c
    FULL OUTER JOIN feature_prior p ON c.customer = p.customer AND c.feature = p.feature
),
top_contracting_feature AS (
    SELECT customer, feature, feature_wow_change,
        ROW_NUMBER() OVER (PARTITION BY customer ORDER BY feature_wow_change ASC) AS rn
    FROM feature_change
)
SELECT c.customer, c.current_rev, c.prior_rev, c.wow_change,
    100.0 * c.wow_change / NULLIF(c.prior_rev, 0) AS wow_pct,
    100.0 * (c.current_rev - c.py_rev) / NULLIF(c.py_rev, 0) AS yoy_pct,
    100.0 * c.current_rev / NULLIF(t.total_current, 0) AS mix_pct,
    100.0 * ABS(c.wow_change) / NULLIF(t.total_mag, 0) AS contribution_pct,
    tcf.feature AS top_contracting_feature
FROM combined c
CROSS JOIN totals t
LEFT JOIN top_contracting_feature tcf ON c.customer = tcf.customer AND tcf.rn = 1
WHERE c.wow_change < 0
ORDER BY c.wow_change ASC
LIMIT 15
```

### Query 8: Product Category Weekly View with Mix and Contribution

```sql
WITH catalyst_realized AS (
    SELECT usage_day AS ds, 'AI/ML' AS product_category, SUM(catalyst_revenue) AS revenue
    FROM finance.customer.catalyst_revenue_reporting
    WHERE usage_day <= CURRENT_DATE - 2
    GROUP BY 1
),
base_current AS (
    SELECT product_category, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1
),
catalyst_current AS (
    SELECT product_category, SUM(revenue) AS current_rev
    FROM catalyst_realized
    WHERE ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1
),
current_week AS (
    SELECT product_category, SUM(current_rev) AS current_rev
    FROM (SELECT * FROM base_current UNION ALL SELECT * FROM catalyst_current)
    GROUP BY 1
),
base_prior AS (
    SELECT product_category, SUM(revenue) AS prior_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1
),
catalyst_prior AS (
    SELECT product_category, SUM(revenue) AS prior_rev
    FROM catalyst_realized
    WHERE ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1
),
prior_week AS (
    SELECT product_category, SUM(prior_rev) AS prior_rev
    FROM (SELECT * FROM base_prior UNION ALL SELECT * FROM catalyst_prior)
    GROUP BY 1
),
combined AS (
    SELECT COALESCE(c.product_category, p.product_category) AS product_category,
        COALESCE(c.current_rev, 0) AS current_rev,
        COALESCE(p.prior_rev, 0) AS prior_rev,
        COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS wow_change
    FROM current_week c
    FULL OUTER JOIN prior_week p ON c.product_category = p.product_category
),
totals AS (
    SELECT SUM(ABS(wow_change)) AS total_mag, SUM(current_rev) AS total_current FROM combined
)
SELECT c.product_category, c.prior_rev AS prior_week, c.current_rev AS current_week, c.wow_change,
    100.0 * c.wow_change / NULLIF(c.prior_rev, 0) AS wow_pct,
    100.0 * c.current_rev / NULLIF(t.total_current, 0) AS mix_pct,
    100.0 * ABS(c.wow_change) / NULLIF(t.total_mag, 0) AS contribution_pct
FROM combined c
CROSS JOIN totals t
ORDER BY c.current_rev DESC
```

---

## FORMAT B: NARRATIVE

Follow the same 8-section structure but present as prose paragraphs instead of tables. Each section should include the same data points with specific numbers.

### Customer Format (ALL 4 METRICS REQUIRED)
```
Customer Name (+/-$XX,XXX, +/-XX.XX% WoW, X.XX% mix, X.XX% contribution)
```

---

## Metrics Definitions

| Metric | Formula |
|--------|---------|
| WoW Change | Current Week - Prior Week |
| WoW % | (Current - Prior) / Prior × 100 |
| Growth Contribution | ABS(delta) / SUM(ABS(all deltas)) × 100 |
| Mix % | Current Period Revenue / Total Current Period Revenue × 100 |
| QTD vs Plan % | (QTD Actual / QTD Plan) - 1 |
| FQ vs Plan % | (FQ Forecast / FQ Plan) - 1 |
| FQ vs Target % | (FQ Forecast / FQ Target) - 1 |
| YoY % | (Current Year - Prior Year) / Prior Year × 100 |

---

## Product Categories

| Category | Use Cases |
|----------|-----------|
| Data Engineering | Transformation, Ingestion, Data Sharing |
| Analytics | Business Intelligence, Interactive Analytics |
| AI/ML | ML, Unstructured Data, Conversational Assistants |
| Applications & Collaboration | Internal/External Collaboration, Marketplace |
| Platform | Storage, Compute, Observability, Security |

**Note:** AI/ML Conversational Assistants includes catalyst revenue (Cortex LLM REST) from `finance.customer.catalyst_revenue_reporting`.

---

## Stopping Points

- ✋ Step 1: After date parameter collection
- ✋ Step 3: Before finalizing report

## Output

Complete weekly report with 8 tables:
1. Forecast Evolution (with trend over time)
2. QTD vs Plan
3. Product Category Summary (WoW)
4. Full Quarter Forecast vs Plan vs Target
5. Top 25 Customers
6. Top 15 Weekly Gainers
7. Top 15 Weekly Contractors
8. Product Category Weekly View (with Mix & Contribution)

Each table followed by an Executive Summary paragraph.

---

## Step 4: Deep Dive Prompt (REQUIRED)

**After presenting the complete report, you MUST prompt the user with the following question using `ask_user_question` tool:**

Ask: "Which product category would you like to dive deeper on?"

Options:
| Option | Description |
|--------|-------------|
| Data Engineering | Deep dive into DE metrics, ingestion, transformation |
| Analytics | Deep dive into BI, interactive analytics |
| AI/ML | Deep dive into ML, unstructured data, conversational assistants |
| Platform | Deep dive into storage, compute, observability |
| Apps & Collab | Deep dive into collaboration, marketplace |

**Based on user selection, invoke the corresponding skill:**

| Selection | Action |
|-----------|--------|
| Data Engineering | Invoke skill: `de-weekly-metrics` |
| Analytics | Say: "Analytics deep dive skill not developed yet" |
| AI/ML | Say: "AI/ML deep dive skill not developed yet" |
| Platform | Say: "Platform deep dive skill not developed yet" |
| Apps & Collab | Say: "Apps & Collab deep dive skill not developed yet" |

**Important:** If the selected skill does not exist or fails to load, inform the user: "Skill not developed yet"

---

## Step 5: Continue or Exit Loop (REQUIRED)

**After the deep dive skill completes (or after informing user skill is not developed), you MUST prompt the user:**

Ask: "Would you like to deep dive into another product category?"

Options:
| Option | Description |
|--------|-------------|
| Yes - Another Category | Select a different product category for deep dive |
| No - Exit | End the weekly metrics analysis |

**Based on user selection:**

| Selection | Action |
|-----------|--------|
| Yes - Another Category | Return to **Step 4** and show the product category dropdown again |
| No - Exit | End the session with: "Weekly metrics analysis complete. Let me know if you need anything else!" |

**This creates a loop allowing users to explore multiple categories before exiting.**
