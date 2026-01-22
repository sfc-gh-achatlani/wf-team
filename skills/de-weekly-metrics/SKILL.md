---
name: de-weekly-metrics
description: "Weekly Data Engineering metrics with full category deep dive, L1 commentary, Dynamic Tables, Snowpark, and ingestion focus. Triggers: DE weekly, data engineering metrics, dynamic tables weekly, snowpark metrics, DT analysis, ingestion metrics."
---

# Data Engineering Weekly Metrics

Comprehensive weekly analysis for Data Engineering category with:
- Full use case and feature breakdown (Transformation, Ingestion, Interoperable Storage)
- **L1 Commentary** with narrative insights, QTD vs Plan variance magnitude analysis, and customer callouts
- **Y/Y (Year-over-Year) growth** at category, use case, and feature levels
- **Mix %** (revenue as % of total category) and Growth Contribution analysis
- **Variance Magnitude %** - share of total QTD variance attributed to each use case/feature
- **Concentration Assessment** for each feature (broad-based / moderately concentrated / highly concentrated)
- **Outsized Mover Flag**: When contribution % > mix % + 5%, flag as outsized mover
- Customer movers and concentration analysis
- **Additional Focus: Dynamic Tables** (Revenue + Table Count + Storage)
- **Additional Focus: Snowpark** (DE Revenue + All-Up Snowpark)
- **Additional Focus: TB Ingested** by modality with top customers per modality

## Workflow

### Step 1: Collect Parameters

**Ask user for output format:** Tables or Narrative

**Ask user for date parameters:**

| Parameter | Example |
|-----------|---------|
| Current Week Start | 2026-01-12 |
| Current Week End | 2026-01-18 |
| Prior Week Start | 2026-01-05 |
| Prior Week End | 2026-01-11 |
| QTD Start | 2025-11-01 |

**FY26 Q4:** Nov 1, 2025 - Jan 31, 2026

**⚠️ STOP**: Confirm dates before proceeding.

### Step 2: Data Engineering Overview

1. **Category WoW Summary** - Total DE revenue
2. **Category Y/Y Growth** - Compare current week to same week prior year
3. **QTD vs Plan** - Date-aligned
4. **Full Quarter vs Plan vs Target**

### Step 3: L1 Use Case Commentary

For each use case (Transformation, Ingestion, Interoperable Storage), generate **narrative bullet insights**:

1. **Use Case QTD vs Plan Analysis**:
   - QTD Actual vs QTD Plan with delta and delta %
   - **Variance Magnitude %** = |Use Case Delta| ÷ Sum of |All Use Case Deltas|
   - Identifies which use cases are driving variance to plan

2. **Use Case WoW Performance**:
   - Current week revenue with WoW change and WoW %
   - **Mix %** = Use Case Revenue ÷ Total DE Category Revenue
   - **Contribution %** = |Use Case WoW Change| ÷ Total Absolute WoW Change

3. **Narrative Format** (for each use case):
```
**[Use Case]** is tracking [ahead/behind] QTD plan by [+/-$X.XXM] ([+/-X.X%]), 
accounting for [X.X%] of variance magnitude despite making up [X.X%] of revenue. 
Weekly [grew/declined] [+/-$XXK] ([+/-X.X% WoW]). [Key driver insight].
```

4. **Use Case QTD vs Plan Table**:
| Use Case | QTD Actual | QTD Plan | Delta | Delta % | Mix % | Variance Mag % | Current Week | WoW Change | WoW % |

### Step 4: L1 Feature Commentary

For top features by variance magnitude, generate **narrative bullet insights with customer callouts**:

1. **Feature QTD vs Plan Analysis**:
   - QTD Actual vs QTD Plan with delta and delta %
   - **Variance Magnitude %** = |Feature Delta| ÷ Sum of |All Feature Deltas|
   - Weekly trend (3-week pattern if relevant)

2. **Concentration Assessment** for each material feature:
   - Top 3 and Top 10 customer concentration %
   - Assessment: Broad-based (<30%), Moderately concentrated (30-60%), Highly concentrated (>60%)

3. **Customer Callouts**:
   - Top 5 gainers with $ change, % change, and % of movement
   - Flag new customers or outsized movers

4. **Narrative Format** (for each feature):
```
**[Feature]** is [+/-$X.XXM] [ahead/behind] QTD plan ([+/-X.X%]), accounting for 
[X.X%] of total variance magnitude. Weekly [recovered/grew/declined] ([+/-$XXK], 
[+/-X.X% WoW]). Growth is [broad-based/moderately concentrated/highly concentrated] 
— top 3 customers account for [X.X%] of revenue.
Top gainers: [Customer1] (+$XXK, +XX%), [Customer2] (+$XXK, +XX% — [insight])
```

5. **Feature QTD vs Plan Table**:
| Use Case | Feature | QTD Actual | QTD Plan | Delta | Delta % | Mix % | Var Mag % | WoW % |

6. **Feature Customer Movement Tables** (for top 3-5 features):
| Customer | Prior Week | Current Week | WoW Change | WoW % | % of Movement |

7. **Concentration Assessment Table**:
| Feature | Top 3 % | Top 10 % | Assessment |

### Step 5: Use Case Analysis (Original)

For each use case (Transformation, Ingestion, Interoperable Storage):
1. **Use Case WoW** with Mix % and Growth Contribution %
   - **Mix % = Use Case Revenue ÷ Total DE Category Revenue**
2. **Use Case Y/Y Growth** - Compare to same week prior year
3. **Use Case Variance to Target**
4. **Outsized Mover Flag** - Mark if contribution % > mix % + 5%

### Step 6: Feature Analysis (Original)

1. **Feature Growth Contribution** - Top 10-15 features ranked by contribution %
2. **Feature Y/Y Growth** - Include Y/Y % for top features
3. **Feature Mix %** = Feature Revenue ÷ **Total DE Category Revenue** (NOT use case revenue)
4. **Outsized Mover Flag** - Mark if contribution % > mix % + 5%
5. **Feature Variance to Target** - All features with FQ vs Target %
6. For top moving features:
   - **Top 3 Concentration** assessment
   - **Top 5 Customer Movers** with 4-metric format

### Step 7: Dynamic Tables Deep Dive

1. **DT Refresh Revenue** - WoW + Variance to Target
2. **DT Table Count** - Count on last day of each week
3. **DT Storage (TB)** - Bytes on last day of each week
4. **Top Customer Movers** for DT refresh with concentration

### Step 8: Snowpark Deep Dive

1. **Snowpark DE Revenue** - WoW + Variance to Target (from product category)
2. **All-Up Snowpark Revenue** - WoW (from feature vector query)
3. **Top Customer Movers** for Snowpark DE with concentration

### Step 9: TB Ingested Analysis

1. **Total TB Ingested** - WoW + Y/Y
2. **TB by Modality** - Copy, Snowpipe, Snowpipe Streaming v1/v2, Connectors, Openflow
3. **Top 5 Customers per Modality** - For each ingestion modality, show top 5 customers by TB ingested with WoW change

### Step 10: Anomalous Customer Analysis

1. **Calculate Customer-Feature Mix vs Contribution** for ALL customer-feature combinations:
   - **Customer-Feature Mix %** = (Customer's feature revenue) / (Total DE revenue)
   - **Customer-Feature Contribution %** = |Customer's feature WoW change| / (Total absolute WoW change across all customer-feature combos)
   - **Flag if |Contribution % - Mix %| > 1%** (indicates outsized impact relative to size)

2. **Analyze 8-week historical data** to determine if behavior is EXPECTED or ANOMALOUS:

   **EXPECTED patterns (EXCLUDE from report):**
   - Spike → Crash returning to historical baseline (e.g., month-end batch job)
   - Crash → Spike returning to historical baseline
   - Monthly/weekly cadence patterns (regular spikes at predictable intervals)
   - Volatility within historical normal range (high CV but no trend change)

   **ANOMALOUS patterns (INCLUDE in report):**
   - **NEW WORKLOAD**: Near-zero baseline → sustained new level (not just one-week spike)
   - **MIGRATION/EXPANSION**: Sustained shift to NEW higher baseline (2+ weeks above old average)
   - **UNEXPECTED CRASH**: Drop BELOW historical baseline (not returning to normal after spike)
   - **ACCELERATING TREND**: Consistent week-over-week growth (3+ weeks)
   - **CHURN SIGNAL**: Sustained decline below historical baseline (2+ weeks)
   - **STEP CHANGE**: Sudden jump that holds (new steady state established)

3. **For each flagged customer-feature, calculate:**
   - 8-week average (baseline)
   - 8-week standard deviation
   - Current week vs baseline comparison
   - Trend direction (up/down/flat)
   - **Mix %** = Customer-Feature Revenue / Total DE Revenue
   - **Contribution %** = |Customer-Feature WoW Change| / Total Absolute WoW Change
   - **Gap %** = Contribution % - Mix % (flag ⚠️ if > 0.5%)

4. **Select top 10** truly anomalous customer-feature combinations for AE/SE outreach
5. **Query dim_use_case** for SE comments and use case descriptions

**OUTPUT AS TABLE FORMAT:**
| # | Customer | AE | SE | Feature | 8wk Avg | Current | vs Avg | Mix % | Contrib % | Gap | Pattern | Question |
|---|----------|----|----|---------|---------|---------|--------|-------|-----------|-----|---------|----------|

**REQUIRED: Include 10 customer-feature combinations showing TRUE anomalies (new workloads, migrations, unexpected changes)**
**EXCLUDE: Spike-to-baseline returns, monthly batch patterns, normal volatility**

### Step 11: Generate Report

Compile with:
1. Executive Summary (include Y/Y growth)
2. **L1 Use Case Commentary** - Narrative bullets + QTD vs Plan table with variance magnitude
3. **L1 Feature Commentary** - Narrative bullets with customer callouts + Feature tables + Concentration assessment
4. Use Case breakdown with target variance, Y/Y growth, mix %, and outsized mover flags
5. Feature tables with concentration, customer movers, Y/Y growth, mix %, and outsized mover flags
6. Dynamic Tables section (Revenue + Count + Storage + Y/Y)
7. Snowpark section (DE + All-Up + Y/Y)
8. TB Ingested section with top customers per modality
9. **Anomalous Customers section** with AE/SE, SE comments, use case descriptions, and feature details
10. Key Signals summary

**⚠️ STOP**: Present draft for review.

---

## Data Sources

| Table | Purpose |
|-------|---------|
| `finance.customer.fy26_product_category_revenue` | Revenue actuals by feature/customer |
| `finance.dev_sensitive.achatlani_nov_plan_vf` | QTD plan |
| `finance.customer.product_category_rev_actuals_w_forecast_sfdc` | Actuals + forecast |
| `finance.raw_google_sheets.fy_26_product_category_feature_targets` | Target revenue |
| `snowscience.product.feature_account_revenue_stg` | All-Up Snowpark |
| `finance.customer.snowflake_account_revenue` | Account revenue for joins |
| `snowscience.data_engineering.ingestion` | TB ingested |
| `snowscience.data_engineering.dynamic_tables_tables` | DT table count |
| `snowscience.data_engineering.dynamic_tables_data_under_management` | DT storage |
| `snowscience.dimensions.dim_snowflake_accounts` | Account metadata |
| `finance.customer.PRODUCT_CATEGORY_REVENUE_AE_SPLIT_ACCOUNTS` | AE lookup by customer |
| `finance.customer.PRODUCT_CATEGORY_REVENUE_SE_SPLIT_ACCOUNTS` | SE lookup by customer |
| `mdm.mdm_interfaces.dim_use_case` | **SE comments, use case descriptions, technical details** |

---

## Key Queries

### 1. Use Case WoW with Growth Contribution and Mix %
```sql
WITH current_week AS (
    SELECT use_case, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1
),
prior_week AS (
    SELECT use_case, SUM(revenue) AS prior_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1
),
combined AS (
    SELECT 
        COALESCE(c.use_case, p.use_case) AS use_case,
        COALESCE(c.current_rev, 0) AS current_rev,
        COALESCE(p.prior_rev, 0) AS prior_rev,
        COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS wow_change
    FROM current_week c
    FULL OUTER JOIN prior_week p ON c.use_case = p.use_case
),
totals AS (
    SELECT SUM(ABS(wow_change)) AS total_mag, SUM(current_rev) AS total_current FROM combined
)
SELECT 
    c.use_case,
    c.prior_rev AS prior_week,
    c.current_rev AS current_week,
    c.wow_change,
    100.0 * c.wow_change / NULLIF(c.prior_rev, 0) AS wow_pct,
    100.0 * c.current_rev / NULLIF(t.total_current, 0) AS mix_pct,
    100.0 * ABS(c.wow_change) / NULLIF(t.total_mag, 0) AS contribution_pct,
    CASE WHEN (100.0 * ABS(c.wow_change) / NULLIF(t.total_mag, 0)) > 
              (100.0 * c.current_rev / NULLIF(t.total_current, 0)) + 5 
         THEN '⚠️ OUTSIZED' ELSE '' END AS outsized_flag
FROM combined c
CROSS JOIN totals t
ORDER BY ABS(c.wow_change) DESC
```

### 2. Use Case Variance to Target
```sql
WITH fq_forecast AS (
    SELECT use_case, SUM(revenue) AS full_quarter_revenue
    FROM finance.customer.product_category_rev_actuals_w_forecast_sfdc
    WHERE product_category = 'Data Engineering'
      AND usage_date BETWEEN :qtd_start AND '2026-01-31'
    GROUP BY 1
),
fq_plan AS (
    SELECT use_case, SUM(revenue) AS full_quarter_plan
    FROM finance.dev_sensitive.achatlani_nov_plan_vf
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN :qtd_start AND '2026-01-31'
    GROUP BY 1
),
fq_target AS (
    SELECT use_case, SUM(target_revenue) AS full_quarter_target
    FROM finance.raw_google_sheets.fy_26_product_category_feature_targets
    WHERE fiscal_quarter_fyyyyy_qq = 'FY2026-Q4'
      AND product_category = 'Data Engineering'
    GROUP BY 1
)
SELECT 
    f.use_case,
    f.full_quarter_revenue,
    p.full_quarter_plan,
    (f.full_quarter_revenue / NULLIF(p.full_quarter_plan, 0)) - 1 AS fq_delta_to_plan,
    t.full_quarter_target,
    (f.full_quarter_revenue / NULLIF(t.full_quarter_target, 0)) - 1 AS fq_delta_to_target
FROM fq_forecast f
LEFT JOIN fq_plan p ON f.use_case = p.use_case
LEFT JOIN fq_target t ON f.use_case = t.use_case
ORDER BY f.full_quarter_revenue DESC
```

### 3. Feature Growth Contribution with Mix % and Outsized Flag
```sql
WITH current_week AS (
    SELECT feature, use_case, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1, 2
),
prior_week AS (
    SELECT feature, use_case, SUM(revenue) AS prior_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1, 2
),
prior_year_week AS (
    SELECT feature, use_case, SUM(revenue) AS prior_year_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN DATEADD(year, -1, :current_week_start) AND DATEADD(year, -1, :current_week_end)
    GROUP BY 1, 2
),
combined AS (
    SELECT 
        COALESCE(c.feature, p.feature) AS feature,
        COALESCE(c.use_case, p.use_case) AS use_case,
        COALESCE(c.current_rev, 0) AS current_rev,
        COALESCE(p.prior_rev, 0) AS prior_rev,
        COALESCE(py.prior_year_rev, 0) AS prior_year_rev,
        COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS wow_change
    FROM current_week c
    FULL OUTER JOIN prior_week p ON c.feature = p.feature AND c.use_case = p.use_case
    LEFT JOIN prior_year_week py ON COALESCE(c.feature, p.feature) = py.feature 
        AND COALESCE(c.use_case, p.use_case) = py.use_case
),
totals AS (
    SELECT SUM(ABS(wow_change)) AS total_mag, SUM(current_rev) AS total_current FROM combined
)
SELECT 
    c.use_case,
    c.feature,
    c.prior_rev,
    c.current_rev,
    c.wow_change,
    100.0 * c.wow_change / NULLIF(c.prior_rev, 0) AS wow_pct,
    100.0 * (c.current_rev - c.prior_year_rev) / NULLIF(c.prior_year_rev, 0) AS yoy_pct,
    100.0 * c.current_rev / NULLIF(t.total_current, 0) AS mix_pct,
    100.0 * ABS(c.wow_change) / NULLIF(t.total_mag, 0) AS contribution_pct,
    CASE WHEN (100.0 * ABS(c.wow_change) / NULLIF(t.total_mag, 0)) > 
              (100.0 * c.current_rev / NULLIF(t.total_current, 0)) + 5 
         THEN '⚠️ OUTSIZED' ELSE '' END AS outsized_flag
FROM combined c
CROSS JOIN totals t
ORDER BY ABS(c.wow_change) DESC
LIMIT 15
```

### 4. Feature Variance to Target
```sql
WITH fq_forecast AS (
    SELECT feature, use_case, SUM(revenue) AS full_quarter_revenue
    FROM finance.customer.product_category_rev_actuals_w_forecast_sfdc
    WHERE product_category = 'Data Engineering'
      AND usage_date BETWEEN :qtd_start AND '2026-01-31'
    GROUP BY 1, 2
),
fq_target AS (
    SELECT feature, use_case, SUM(target_revenue) AS full_quarter_target
    FROM finance.raw_google_sheets.fy_26_product_category_feature_targets
    WHERE fiscal_quarter_fyyyyy_qq = 'FY2026-Q4'
      AND product_category = 'Data Engineering'
    GROUP BY 1, 2
)
SELECT 
    f.use_case,
    f.feature,
    f.full_quarter_revenue,
    t.full_quarter_target,
    (f.full_quarter_revenue / NULLIF(t.full_quarter_target, 0)) - 1 AS fq_delta_to_target
FROM fq_forecast f
LEFT JOIN fq_target t ON f.feature = t.feature AND f.use_case = t.use_case
ORDER BY f.full_quarter_revenue DESC
```

### 5. Top Customer Movers (parameterized by feature)
```sql
WITH current_week AS (
    SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE feature = :feature
      AND ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1
),
prior_week AS (
    SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS prior_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE feature = :feature
      AND ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1
),
combined AS (
    SELECT 
        COALESCE(c.customer, p.customer) AS customer,
        COALESCE(c.current_rev, 0) AS current_rev,
        COALESCE(p.prior_rev, 0) AS prior_rev,
        COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS wow_change
    FROM current_week c
    FULL OUTER JOIN prior_week p ON c.customer = p.customer
),
totals AS (
    SELECT SUM(ABS(wow_change)) AS total_mag, SUM(current_rev) AS total_current FROM combined
)
SELECT 
    c.customer,
    c.prior_rev,
    c.current_rev,
    c.wow_change,
    100.0 * c.wow_change / NULLIF(c.prior_rev, 0) AS wow_pct,
    100.0 * c.current_rev / NULLIF(t.total_current, 0) AS mix_pct,
    100.0 * ABS(c.wow_change) / NULLIF(t.total_mag, 0) AS contribution_pct
FROM combined c
CROSS JOIN totals t
ORDER BY ABS(c.wow_change) DESC
LIMIT 10
```

### 6. Top 3 Concentration
```sql
WITH current_week AS (
    SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE feature = :feature
      AND ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1
),
prior_week AS (
    SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS prior_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE feature = :feature
      AND ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1
),
combined AS (
    SELECT 
        COALESCE(c.customer, p.customer) AS customer,
        COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS wow_change
    FROM current_week c
    FULL OUTER JOIN prior_week p ON c.customer = p.customer
),
ranked AS (
    SELECT customer, ABS(wow_change) AS abs_change,
        SUM(ABS(wow_change)) OVER () AS total_magnitude,
        ROW_NUMBER() OVER (ORDER BY ABS(wow_change) DESC) AS rn
    FROM combined
)
SELECT 100.0 * SUM(abs_change) / MAX(total_magnitude) AS top_3_concentration_pct
FROM ranked WHERE rn <= 3
```

### 7. QTD vs Plan (Data Engineering)
```sql
WITH realized_revenue AS (
    SELECT ds, SUM(revenue) AS revenue
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds <= CURRENT_DATE - 2
    GROUP BY 1
),
max_realized_date AS (
    SELECT MAX(ds) AS max_ds FROM realized_revenue
),
qtd_actual AS (
    SELECT SUM(revenue) AS qtd_revenue
    FROM realized_revenue
    WHERE ds >= :qtd_start
),
qtd_plan AS (
    SELECT SUM(revenue) AS qtd_plan
    FROM finance.dev_sensitive.achatlani_nov_plan_vf p
    CROSS JOIN max_realized_date m
    WHERE p.product_category = 'Data Engineering'
      AND p.ds >= :qtd_start 
      AND p.ds <= m.max_ds
)
SELECT 
    a.qtd_revenue,
    p.qtd_plan,
    (a.qtd_revenue / NULLIF(p.qtd_plan, 0)) - 1 AS qtd_pct_delta_to_plan
FROM qtd_actual a, qtd_plan p
```

### 8. Full Quarter Forecast vs Plan vs Target (Data Engineering)
```sql
WITH fq_forecast AS (
    SELECT SUM(revenue) AS full_quarter_revenue
    FROM finance.customer.product_category_rev_actuals_w_forecast_sfdc
    WHERE product_category = 'Data Engineering'
      AND usage_date BETWEEN :qtd_start AND '2026-01-31'
),
fq_plan AS (
    SELECT SUM(revenue) AS full_quarter_plan
    FROM finance.dev_sensitive.achatlani_nov_plan_vf
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN :qtd_start AND '2026-01-31'
),
fq_target AS (
    SELECT SUM(target_revenue) AS full_quarter_target
    FROM finance.raw_google_sheets.fy_26_product_category_feature_targets
    WHERE fiscal_quarter_fyyyyy_qq = 'FY2026-Q4'
      AND product_category = 'Data Engineering'
)
SELECT 
    f.full_quarter_revenue,
    p.full_quarter_plan,
    (f.full_quarter_revenue / NULLIF(p.full_quarter_plan, 0)) - 1 AS fq_delta_to_plan,
    t.full_quarter_target,
    (f.full_quarter_revenue / NULLIF(t.full_quarter_target, 0)) - 1 AS fq_delta_to_target
FROM fq_forecast f, fq_plan p, fq_target t
```

---

## L1 Commentary Queries

### 9. L1 Use Case QTD vs Plan with Variance Magnitude
```sql
WITH qtd_actual AS (
    SELECT use_case, SUM(revenue) AS actual_revenue
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
        AND ds BETWEEN :qtd_start AND :current_week_end
    GROUP BY 1
),
qtd_plan AS (
    SELECT use_case, SUM(revenue) AS plan_revenue
    FROM finance.dev_sensitive.achatlani_nov_plan_vf
    WHERE product_category = 'Data Engineering'
        AND ds BETWEEN :qtd_start AND :current_week_end
    GROUP BY 1
),
wow_current AS (
    SELECT use_case, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
        AND ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1
),
wow_prior AS (
    SELECT use_case, SUM(revenue) AS prior_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
        AND ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1
),
combined AS (
    SELECT
        COALESCE(a.use_case, p.use_case) AS use_case,
        COALESCE(a.actual_revenue, 0) AS qtd_actual,
        COALESCE(p.plan_revenue, 0) AS qtd_plan,
        COALESCE(a.actual_revenue, 0) - COALESCE(p.plan_revenue, 0) AS delta_to_plan,
        COALESCE(wc.current_rev, 0) AS current_week_rev,
        COALESCE(wp.prior_rev, 0) AS prior_week_rev,
        COALESCE(wc.current_rev, 0) - COALESCE(wp.prior_rev, 0) AS wow_change
    FROM qtd_actual a
    FULL OUTER JOIN qtd_plan p ON a.use_case = p.use_case
    LEFT JOIN wow_current wc ON COALESCE(a.use_case, p.use_case) = wc.use_case
    LEFT JOIN wow_prior wp ON COALESCE(a.use_case, p.use_case) = wp.use_case
),
totals AS (
    SELECT SUM(qtd_actual) AS total_actual, SUM(ABS(delta_to_plan)) AS total_magnitude FROM combined
)
SELECT
    c.use_case,
    ROUND(c.qtd_actual, 0) AS qtd_actual,
    ROUND(c.qtd_plan, 0) AS qtd_plan,
    ROUND(c.delta_to_plan, 0) AS delta_to_plan,
    ROUND(c.delta_to_plan / NULLIF(c.qtd_plan, 0) * 100, 2) AS delta_pct,
    ROUND(c.qtd_actual / NULLIF(t.total_actual, 0) * 100, 1) AS mix_pct,
    ROUND(ABS(c.delta_to_plan) / NULLIF(t.total_magnitude, 0) * 100, 1) AS variance_magnitude_pct,
    ROUND(c.current_week_rev, 0) AS current_week,
    ROUND(c.prior_week_rev, 0) AS prior_week,
    ROUND(c.wow_change, 0) AS wow_change,
    ROUND(c.wow_change / NULLIF(c.prior_week_rev, 0) * 100, 2) AS wow_pct
FROM combined c CROSS JOIN totals t
ORDER BY c.qtd_actual DESC
```

### 10. L1 Feature QTD vs Plan with Variance Magnitude
```sql
WITH qtd_actual AS (
    SELECT use_case, feature, SUM(revenue) AS actual_revenue
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
        AND ds BETWEEN :qtd_start AND :current_week_end
    GROUP BY 1, 2
),
qtd_plan AS (
    SELECT use_case, feature, SUM(revenue) AS plan_revenue
    FROM finance.dev_sensitive.achatlani_nov_plan_vf
    WHERE product_category = 'Data Engineering'
        AND ds BETWEEN :qtd_start AND :current_week_end
    GROUP BY 1, 2
),
wow_current AS (
    SELECT feature, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
        AND ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1
),
wow_prior AS (
    SELECT feature, SUM(revenue) AS prior_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
        AND ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1
),
combined AS (
    SELECT
        COALESCE(a.use_case, p.use_case) AS use_case,
        COALESCE(a.feature, p.feature) AS feature,
        COALESCE(a.actual_revenue, 0) AS qtd_actual,
        COALESCE(p.plan_revenue, 0) AS qtd_plan,
        COALESCE(a.actual_revenue, 0) - COALESCE(p.plan_revenue, 0) AS delta_to_plan,
        COALESCE(wc.current_rev, 0) AS current_week,
        COALESCE(wp.prior_rev, 0) AS prior_week,
        COALESCE(wc.current_rev, 0) - COALESCE(wp.prior_rev, 0) AS wow_change
    FROM qtd_actual a
    FULL OUTER JOIN qtd_plan p ON a.feature = p.feature AND a.use_case = p.use_case
    LEFT JOIN wow_current wc ON COALESCE(a.feature, p.feature) = wc.feature
    LEFT JOIN wow_prior wp ON COALESCE(a.feature, p.feature) = wp.feature
),
totals AS (
    SELECT SUM(qtd_actual) AS total_actual, SUM(ABS(delta_to_plan)) AS total_magnitude FROM combined
)
SELECT
    c.use_case,
    c.feature,
    ROUND(c.qtd_actual, 0) AS qtd_actual,
    ROUND(c.qtd_plan, 0) AS qtd_plan,
    ROUND(c.delta_to_plan, 0) AS delta_to_plan,
    ROUND(c.delta_to_plan / NULLIF(c.qtd_plan, 0) * 100, 2) AS delta_pct,
    ROUND(c.qtd_actual / NULLIF(t.total_actual, 0) * 100, 2) AS mix_pct,
    ROUND(ABS(c.delta_to_plan) / NULLIF(t.total_magnitude, 0) * 100, 1) AS variance_magnitude_pct,
    ROUND(c.current_week, 0) AS current_week,
    ROUND(c.wow_change, 0) AS wow_change,
    ROUND(c.wow_change / NULLIF(c.prior_week, 0) * 100, 2) AS wow_pct
FROM combined c CROSS JOIN totals t
WHERE c.qtd_actual > 100000
ORDER BY ABS(c.delta_to_plan) DESC
LIMIT 20
```

### 11. L1 Feature Customer Movers with % of Movement
```sql
WITH current_week AS (
    SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE feature = :feature
      AND ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1
),
prior_week AS (
    SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS prior_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE feature = :feature
      AND ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1
),
combined AS (
    SELECT COALESCE(c.customer, p.customer) AS customer,
        COALESCE(c.current_rev, 0) AS current_rev,
        COALESCE(p.prior_rev, 0) AS prior_rev,
        COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS wow_change
    FROM current_week c FULL OUTER JOIN prior_week p ON c.customer = p.customer
),
totals AS (
    SELECT SUM(CASE WHEN wow_change > 0 THEN wow_change ELSE 0 END) AS total_positive,
           SUM(CASE WHEN wow_change < 0 THEN ABS(wow_change) ELSE 0 END) AS total_negative
    FROM combined
)
SELECT c.customer, 
    ROUND(c.prior_rev, 0) AS prior_rev, 
    ROUND(c.current_rev, 0) AS current_rev, 
    ROUND(c.wow_change, 0) AS wow_change, 
    ROUND(100.0 * c.wow_change / NULLIF(c.prior_rev, 0), 1) AS wow_pct,
    ROUND(CASE WHEN c.wow_change > 0 THEN 100.0 * c.wow_change / NULLIF(t.total_positive, 0)
          ELSE 100.0 * ABS(c.wow_change) / NULLIF(t.total_negative, 0) END, 1) AS pct_of_movement
FROM combined c CROSS JOIN totals t
ORDER BY c.wow_change DESC 
LIMIT 10
```

### 12. L1 Concentration Assessment
```sql
WITH feature_concentration AS (
    SELECT 
        feature,
        SUM(current_rev) AS total_rev,
        SUM(CASE WHEN rn <= 3 THEN current_rev ELSE 0 END) AS top3_rev,
        SUM(CASE WHEN rn <= 10 THEN current_rev ELSE 0 END) AS top10_rev
    FROM (
        SELECT feature, latest_salesforce_account_name AS customer, 
            SUM(revenue) AS current_rev,
            ROW_NUMBER() OVER (PARTITION BY feature ORDER BY SUM(revenue) DESC) AS rn
        FROM finance.customer.fy26_product_category_revenue
        WHERE product_category = 'Data Engineering'
          AND ds BETWEEN :current_week_start AND :current_week_end
        GROUP BY 1, 2
    )
    WHERE feature IN (:feature_list)
    GROUP BY 1
)
SELECT 
    feature,
    ROUND(100.0 * top3_rev / NULLIF(total_rev, 0), 1) AS top3_concentration_pct,
    ROUND(100.0 * top10_rev / NULLIF(total_rev, 0), 1) AS top10_concentration_pct,
    CASE 
        WHEN 100.0 * top3_rev / NULLIF(total_rev, 0) < 30 THEN 'Broad-based'
        WHEN 100.0 * top3_rev / NULLIF(total_rev, 0) < 60 THEN 'Moderately concentrated'
        ELSE 'Highly concentrated'
    END AS assessment
FROM feature_concentration
ORDER BY total_rev DESC
```

### 13. L1 Weekly Trend (3-week pattern)
```sql
WITH weekly_data AS (
    SELECT 
        feature,
        DATE_TRUNC('week', ds)::date AS week_start,
        SUM(revenue) AS revenue
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN DATEADD(week, -2, :current_week_start) AND :current_week_end
      AND feature IN (:feature_list)
    GROUP BY 1, 2
)
SELECT 
    feature,
    week_start,
    ROUND(revenue, 0) AS revenue,
    ROUND(revenue - LAG(revenue) OVER (PARTITION BY feature ORDER BY week_start), 0) AS wow_change,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (PARTITION BY feature ORDER BY week_start)) / 
          NULLIF(LAG(revenue) OVER (PARTITION BY feature ORDER BY week_start), 0), 1) AS wow_pct
FROM weekly_data
ORDER BY feature, week_start
```

---

## Additional Focus Queries

### 14. Dynamic Table Count (last day of week)
```sql
WITH all_tables AS (
    SELECT 
        c._date AS date,
        COUNT(DISTINCT t.deployment, t.table_id) AS table_count
    FROM snowhouse.utils.calendar c
    JOIN snowscience.data_engineering.dynamic_tables_tables t
    JOIN snowscience.dimensions.dim_snowflake_accounts a 
        ON a.snowflake_account_id = t.account_id 
        AND a.snowflake_deployment = t.deployment
    WHERE c._date IN (:current_week_end, :prior_week_end)
      AND ((t.table_removal_time IS NULL AND t.created_on::date <= c._date::date) 
           OR (c._date BETWEEN t.created_on::date AND t.table_removal_time::date))
      AND a.snowflake_account_type IN ('Customer', 'Partner')
      AND IFF(base_table_types IS NULL, 'FDN ONLY', base_table_types) IN 
          ('FDN ONLY', 'MANAGED ICEBERG AND FDN', 'MANAGED ICEBERG AND UNMANAGED ICEBERG', 
           'MANAGED ICEBERG ONLY', 'UNMANAGED ICEBERG AND FDN', 'UNMANAGED ICEBERG ONLY')
    GROUP BY 1
)
SELECT date, table_count AS active_table_count
FROM all_tables
ORDER BY date
```

### 15. Dynamic Table Storage (TB, last day of week)
```sql
SELECT 
    a.ds,
    SUM(IFF(a.active_bytes = 0, a.logical_bytes, a.active_bytes)) / (1024*1024*1024*1024) AS total_tb
FROM snowscience.data_engineering.dynamic_tables_data_under_management a
JOIN snowscience.dimensions.dim_snowflake_accounts da
    ON da.snowflake_deployment = a.deployment 
    AND da.snowflake_account_id = a.account_id
WHERE da.snowflake_account_type IN ('Customer', 'Partner')
  AND a.ds IN (:current_week_end, :prior_week_end)
GROUP BY 1
ORDER BY 1
```

### 16. All-Up Snowpark Revenue
```sql
WITH prep AS (
    SELECT 
        wkld.ds,
        wkld.adjusted_credits * sar.base_price_per_credit AS revenue
    FROM snowscience.product.feature_account_revenue_stg AS wkld
    LEFT JOIN finance.customer.snowflake_account_revenue AS sar
        ON wkld.ds = sar.general_date
        AND wkld.account_id = sar.snowflake_account_id
        AND wkld.deployment = sar.snowflake_deployment
    WHERE wkld.feature_vector['Snowpark'] = TRUE
      AND sar.agreement_type IN ('Capacity', 'On Demand')
),
current_week AS (
    SELECT SUM(revenue) AS current_rev FROM prep
    WHERE ds BETWEEN :current_week_start AND :current_week_end
),
prior_week AS (
    SELECT SUM(revenue) AS prior_rev FROM prep
    WHERE ds BETWEEN :prior_week_start AND :prior_week_end
)
SELECT 
    p.prior_rev AS prior_week,
    c.current_rev AS current_week,
    c.current_rev - p.prior_rev AS wow_change,
    100.0 * (c.current_rev - p.prior_rev) / NULLIF(p.prior_rev, 0) AS wow_pct
FROM current_week c, prior_week p
```

### 17. TB Ingested by Modality (with Y/Y)
```sql
WITH current_week AS (
    SELECT ing.ingestion_type AS modality, SUM(ing.tbytes) AS tb_ingested
    FROM snowscience.data_engineering.ingestion AS ing
    JOIN snowscience.dimensions.dim_snowflake_accounts AS account_meta
        ON account_meta.snowflake_deployment = ing.deployment
        AND account_meta.snowflake_account_id = ing.account_id
    WHERE ing.ds BETWEEN :current_week_start AND :current_week_end
      AND account_meta.snowflake_account_type IN ('Customer', 'Partner')
    GROUP BY 1
),
prior_week AS (
    SELECT ing.ingestion_type AS modality, SUM(ing.tbytes) AS tb_ingested
    FROM snowscience.data_engineering.ingestion AS ing
    JOIN snowscience.dimensions.dim_snowflake_accounts AS account_meta
        ON account_meta.snowflake_deployment = ing.deployment
        AND account_meta.snowflake_account_id = ing.account_id
    WHERE ing.ds BETWEEN :prior_week_start AND :prior_week_end
      AND account_meta.snowflake_account_type IN ('Customer', 'Partner')
    GROUP BY 1
),
prior_year_week AS (
    SELECT ing.ingestion_type AS modality, SUM(ing.tbytes) AS tb_ingested
    FROM snowscience.data_engineering.ingestion AS ing
    JOIN snowscience.dimensions.dim_snowflake_accounts AS account_meta
        ON account_meta.snowflake_deployment = ing.deployment
        AND account_meta.snowflake_account_id = ing.account_id
    WHERE ing.ds BETWEEN DATEADD(year, -1, :current_week_start) AND DATEADD(year, -1, :current_week_end)
      AND account_meta.snowflake_account_type IN ('Customer', 'Partner')
    GROUP BY 1
)
SELECT 
    COALESCE(c.modality, p.modality) AS modality,
    COALESCE(p.tb_ingested, 0) AS prior_week_tb,
    COALESCE(c.tb_ingested, 0) AS current_week_tb,
    COALESCE(c.tb_ingested, 0) - COALESCE(p.tb_ingested, 0) AS wow_change_tb,
    100.0 * (COALESCE(c.tb_ingested, 0) - COALESCE(p.tb_ingested, 0)) / NULLIF(p.tb_ingested, 0) AS wow_pct,
    COALESCE(py.tb_ingested, 0) AS prior_year_tb,
    100.0 * (COALESCE(c.tb_ingested, 0) - COALESCE(py.tb_ingested, 0)) / NULLIF(py.tb_ingested, 0) AS yoy_pct
FROM current_week c
FULL OUTER JOIN prior_week p ON c.modality = p.modality
FULL OUTER JOIN prior_year_week py ON c.modality = py.modality
ORDER BY current_week_tb DESC
```

### 18. Top Customers per Ingestion Modality
```sql
-- Run for each modality: Copy, Snowpipe, Snowpipe Streaming v1, Snowpipe Streaming v2, Connectors, Openflow
-- NOTE: Use `salesforce_account_name` (NOT `latest_salesforce_account_name`) for dim_snowflake_accounts
WITH current_week AS (
    SELECT 
        a.salesforce_account_name AS customer,
        SUM(ing.tbytes) AS current_tb
    FROM snowscience.data_engineering.ingestion AS ing
    JOIN snowscience.dimensions.dim_snowflake_accounts AS a
        ON a.snowflake_deployment = ing.deployment
        AND a.snowflake_account_id = ing.account_id
    WHERE ing.ds BETWEEN :current_week_start AND :current_week_end
      AND a.snowflake_account_type IN ('Customer', 'Partner')
      AND ing.ingestion_type = :modality
    GROUP BY 1
),
prior_week AS (
    SELECT 
        a.salesforce_account_name AS customer,
        SUM(ing.tbytes) AS prior_tb
    FROM snowscience.data_engineering.ingestion AS ing
    JOIN snowscience.dimensions.dim_snowflake_accounts AS a
        ON a.snowflake_deployment = ing.deployment
        AND a.snowflake_account_id = ing.account_id
    WHERE ing.ds BETWEEN :prior_week_start AND :prior_week_end
      AND a.snowflake_account_type IN ('Customer', 'Partner')
      AND ing.ingestion_type = :modality
    GROUP BY 1
),
combined AS (
    SELECT 
        COALESCE(c.customer, p.customer) AS customer,
        COALESCE(c.current_tb, 0) AS current_tb,
        COALESCE(p.prior_tb, 0) AS prior_tb,
        COALESCE(c.current_tb, 0) - COALESCE(p.prior_tb, 0) AS wow_change
    FROM current_week c
    FULL OUTER JOIN prior_week p ON c.customer = p.customer
),
totals AS (
    SELECT SUM(current_tb) AS total_current FROM combined
)
SELECT 
    c.customer,
    c.prior_tb,
    c.current_tb,
    c.wow_change,
    100.0 * c.wow_change / NULLIF(c.prior_tb, 0) AS wow_pct,
    100.0 * c.current_tb / NULLIF(t.total_current, 0) AS mix_pct
FROM combined c
CROSS JOIN totals t
ORDER BY c.current_tb DESC
LIMIT 5
```

### 19. Category Y/Y Growth
```sql
WITH current_week AS (
    SELECT SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN :current_week_start AND :current_week_end
),
prior_year_week AS (
    SELECT SUM(revenue) AS prior_year_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN DATEADD(year, -1, :current_week_start) AND DATEADD(year, -1, :current_week_end)
)
SELECT 
    py.prior_year_rev,
    c.current_rev,
    c.current_rev - py.prior_year_rev AS yoy_change,
    100.0 * (c.current_rev - py.prior_year_rev) / NULLIF(py.prior_year_rev, 0) AS yoy_pct
FROM current_week c, prior_year_week py
```

### 20. Use Case Y/Y Growth
```sql
WITH current_week AS (
    SELECT use_case, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1
),
prior_year_week AS (
    SELECT use_case, SUM(revenue) AS prior_year_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN DATEADD(year, -1, :current_week_start) AND DATEADD(year, -1, :current_week_end)
    GROUP BY 1
)
SELECT 
    COALESCE(c.use_case, py.use_case) AS use_case,
    COALESCE(py.prior_year_rev, 0) AS prior_year_rev,
    COALESCE(c.current_rev, 0) AS current_rev,
    100.0 * (COALESCE(c.current_rev, 0) - COALESCE(py.prior_year_rev, 0)) / NULLIF(py.prior_year_rev, 0) AS yoy_pct
FROM current_week c
FULL OUTER JOIN prior_year_week py ON c.use_case = py.use_case
ORDER BY current_rev DESC
```

### 21. Feature Y/Y Growth (Top 15)
```sql
WITH current_week AS (
    SELECT feature, use_case, SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1, 2
),
prior_year_week AS (
    SELECT feature, use_case, SUM(revenue) AS prior_year_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN DATEADD(year, -1, :current_week_start) AND DATEADD(year, -1, :current_week_end)
    GROUP BY 1, 2
)
SELECT 
    COALESCE(c.use_case, py.use_case) AS use_case,
    COALESCE(c.feature, py.feature) AS feature,
    COALESCE(py.prior_year_rev, 0) AS prior_year_rev,
    COALESCE(c.current_rev, 0) AS current_rev,
    100.0 * (COALESCE(c.current_rev, 0) - COALESCE(py.prior_year_rev, 0)) / NULLIF(py.prior_year_rev, 0) AS yoy_pct
FROM current_week c
FULL OUTER JOIN prior_year_week py ON c.feature = py.feature AND c.use_case = py.use_case
ORDER BY current_rev DESC
LIMIT 15
```

### 22. Customer-Feature Mix vs Contribution (Outsized Mover Detection)
```sql
-- Identifies customer-feature combinations where contribution to WoW change 
-- differs from their share of total DE revenue by more than 1%
WITH current_week AS (
    SELECT 
        latest_salesforce_account_name AS customer,
        feature,
        SUM(revenue) AS current_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN :current_week_start AND :current_week_end
    GROUP BY 1, 2
),
prior_week AS (
    SELECT 
        latest_salesforce_account_name AS customer,
        feature,
        SUM(revenue) AS prior_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds BETWEEN :prior_week_start AND :prior_week_end
    GROUP BY 1, 2
),
combined AS (
    SELECT 
        COALESCE(c.customer, p.customer) AS customer,
        COALESCE(c.feature, p.feature) AS feature,
        COALESCE(c.current_rev, 0) AS current_rev,
        COALESCE(p.prior_rev, 0) AS prior_rev,
        COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS wow_change
    FROM current_week c
    FULL OUTER JOIN prior_week p ON c.customer = p.customer AND c.feature = p.feature
),
totals AS (
    SELECT 
        SUM(ABS(wow_change)) AS total_wow_magnitude,
        SUM(current_rev) AS total_current_rev
    FROM combined
)
SELECT 
    c.customer,
    c.feature,
    c.prior_rev,
    c.current_rev,
    c.wow_change,
    100.0 * c.wow_change / NULLIF(c.prior_rev, 0) AS wow_pct,
    100.0 * c.current_rev / NULLIF(t.total_current_rev, 0) AS mix_pct,
    100.0 * ABS(c.wow_change) / NULLIF(t.total_wow_magnitude, 0) AS contribution_pct,
    (100.0 * ABS(c.wow_change) / NULLIF(t.total_wow_magnitude, 0)) - 
        (100.0 * c.current_rev / NULLIF(t.total_current_rev, 0)) AS gap_pct,
    CASE 
        WHEN ABS((100.0 * ABS(c.wow_change) / NULLIF(t.total_wow_magnitude, 0)) - 
                 (100.0 * c.current_rev / NULLIF(t.total_current_rev, 0))) > 1 
        THEN 'FLAG' ELSE '' 
    END AS outsized_flag
FROM combined c
CROSS JOIN totals t
WHERE ABS(c.wow_change) > 0
ORDER BY ABS((100.0 * ABS(c.wow_change) / NULLIF(t.total_wow_magnitude, 0)) - 
             (100.0 * c.current_rev / NULLIF(t.total_current_rev, 0))) DESC
LIMIT 20
```

### 23. Historical Consumption for Customer Anomaly Analysis
```sql
-- Run for specific feature (e.g., 'DT refresh', 'Openflow', 'Iceberg DML', etc.)
-- Analyze 8 weeks of history
WITH weekly_data AS (
    SELECT 
        latest_salesforce_account_name AS customer,
        DATE_TRUNC('week', ds) AS week_start,
        SUM(revenue) AS weekly_rev
    FROM finance.customer.fy26_product_category_revenue
    WHERE feature = :feature
      AND ds BETWEEN DATEADD(week, -8, :current_week_start) AND :current_week_end
      AND latest_salesforce_account_name IN (:customer_list)
    GROUP BY 1, 2
)
SELECT customer, week_start, weekly_rev
FROM weekly_data
ORDER BY customer, week_start
```

### 24. Historical TB Ingested for Modality Anomaly Analysis
```sql
-- Run for specific modality (e.g., 'Openflow', 'Snowpipe Streaming v2')
WITH weekly_tb AS (
    SELECT 
        a.salesforce_account_name AS customer,
        DATE_TRUNC('week', ing.ds) AS week_start,
        SUM(ing.tbytes) AS weekly_tb
    FROM snowscience.data_engineering.ingestion AS ing
    JOIN snowscience.dimensions.dim_snowflake_accounts AS a
        ON a.snowflake_deployment = ing.deployment
        AND a.snowflake_account_id = ing.account_id
    WHERE ing.ingestion_type = :modality
      AND ing.ds BETWEEN DATEADD(week, -8, :current_week_start) AND :current_week_end
      AND a.snowflake_account_type IN ('Customer', 'Partner')
      AND a.salesforce_account_name IN (:customer_list)
    GROUP BY 1, 2
)
SELECT customer, week_start, weekly_tb
FROM weekly_tb
ORDER BY customer, week_start
```

### 25. AE/SE Lookup for Customers
```sql
-- Get AE for customers
SELECT DISTINCT 
    latest_salesforce_account_name AS customer,
    SPLIT_AE AS ae
FROM finance.customer.PRODUCT_CATEGORY_REVENUE_AE_SPLIT_ACCOUNTS
WHERE latest_salesforce_account_name IN (:customer_list)
AND usage_date >= :current_week_start;

-- Get SE for customers
SELECT DISTINCT 
    latest_salesforce_account_name AS customer,
    SPLIT_OWNER_NAME AS se
FROM finance.customer.PRODUCT_CATEGORY_REVENUE_SE_SPLIT_ACCOUNTS
WHERE latest_salesforce_account_name IN (:customer_list)
AND usage_date >= :current_week_start;
```

### 26. Use Case Details from dim_use_case (SE Comments & Descriptions)
```sql
-- Get SE comments and use case descriptions for anomalous customers
-- Key columns: SE_COMMENTS, USE_CASE_DESCRIPTION, USE_CASE_NAME, USE_CASE_STAGE, TECHNICAL_USE_CASE
SELECT 
    ACCOUNT_NAME,
    USE_CASE_NAME,
    USE_CASE_DESCRIPTION,
    SE_COMMENTS,
    TECHNICAL_USE_CASE,
    USE_CASE_STAGE,
    USE_CASE_EACV,
    ACCOUNT_LEAD_SE_NAME,
    ACCOUNT_OWNER_NAME,
    GO_LIVE_DATE,
    WORKLOADS,
    PRIORITIZED_FEATURES
FROM mdm.mdm_interfaces.dim_use_case
WHERE ACCOUNT_NAME IN (:customer_list)
  AND USE_CASE_STATUS IN ('Production', 'Implementation', 'In Pursuit')
  AND (
      ARRAY_CONTAINS('DE: Ingestion'::VARIANT, TECHNICAL_USE_CASE_ARRAY)
      OR ARRAY_CONTAINS('DE: Transformation'::VARIANT, TECHNICAL_USE_CASE_ARRAY)
      OR ARRAY_CONTAINS('Data Engineering'::VARIANT, PRODUCT_CATEGORY_ARRAY)
      OR WORKLOADS ILIKE '%Data Engineering%'
      OR WORKLOADS ILIKE '%Iceberg%'
      OR WORKLOADS ILIKE '%Dynamic Table%'
  )
ORDER BY ACCOUNT_NAME, LAST_MODIFIED_DATE DESC
```

### 27. TRUE Anomalies with Mix and Contribution (8-Week Baseline)
```sql
-- Identifies TRUE anomalies: new workloads, migrations, unexpected crashes
-- EXCLUDES: spike-to-baseline returns, monthly batches, normal volatility
WITH weekly AS (
    SELECT 
        latest_salesforce_account_name AS customer,
        feature,
        DATE_TRUNC('week', ds)::date AS week_start,
        SUM(revenue) AS revenue
    FROM finance.customer.fy26_product_category_revenue
    WHERE product_category = 'Data Engineering'
      AND ds >= DATEADD(week, -8, :current_week_start)
      AND ds <= :current_week_end
    GROUP BY 1, 2, 3
),
stats AS (
    SELECT 
        customer,
        feature,
        AVG(revenue) AS avg_rev,
        STDDEV(revenue) AS stddev_rev,
        COUNT(*) AS weeks
    FROM weekly
    WHERE week_start < :current_week_start
    GROUP BY 1, 2
    HAVING COUNT(*) >= 4
),
curr_week AS (
    SELECT customer, feature, revenue AS current_rev
    FROM weekly
    WHERE week_start = :current_week_start
),
prior_week AS (
    SELECT customer, feature, revenue AS prior_rev
    FROM weekly
    WHERE week_start = :prior_week_start
),
totals AS (
    SELECT 
        SUM(current_rev) AS total_current_rev,
        SUM(ABS(current_rev - COALESCE(p.prior_rev, 0))) AS total_wow_magnitude
    FROM curr_week c
    LEFT JOIN prior_week p ON c.customer = p.customer AND c.feature = p.feature
)
SELECT 
    c.customer,
    c.feature,
    ROUND(s.avg_rev, 0) AS baseline_avg,
    ROUND(c.current_rev, 0) AS current_rev,
    ROUND(p.prior_rev, 0) AS prior_rev,
    ROUND(c.current_rev - p.prior_rev, 0) AS wow_change,
    ROUND(100.0 * (c.current_rev - s.avg_rev) / NULLIF(s.avg_rev, 0), 1) AS vs_baseline_pct,
    ROUND(100.0 * c.current_rev / NULLIF(t.total_current_rev, 0), 4) AS mix_pct,
    ROUND(100.0 * ABS(c.current_rev - p.prior_rev) / NULLIF(t.total_wow_magnitude, 0), 4) AS contribution_pct,
    ROUND(100.0 * ABS(c.current_rev - p.prior_rev) / NULLIF(t.total_wow_magnitude, 0), 4) - 
        ROUND(100.0 * c.current_rev / NULLIF(t.total_current_rev, 0), 4) AS gap_pct
FROM curr_week c
JOIN stats s ON c.customer = s.customer AND c.feature = s.feature
LEFT JOIN prior_week p ON c.customer = p.customer AND c.feature = p.feature
CROSS JOIN totals t
WHERE ABS(c.current_rev - p.prior_rev) > 5000
  AND (
      -- NEW WORKLOAD: Near-zero baseline -> sustained new level
      (c.current_rev > s.avg_rev * 2 AND p.prior_rev < s.avg_rev * 1.5)
      -- UNEXPECTED CRASH: Drop below historical baseline
      OR (c.current_rev < s.avg_rev * 0.5 AND p.prior_rev < s.avg_rev * 1.5)
      -- ACCELERATING: Sustained above baseline
      OR (c.current_rev > s.avg_rev * 1.5 AND p.prior_rev > s.avg_rev * 1.3)
  )
ORDER BY ABS(c.current_rev - s.avg_rev) DESC
LIMIT 12
```

---

## Output Format (Concise Narrative)

```
# Data Engineering Weekly Metrics
## Week of [DATE RANGE]

### Executive Summary
DE revenue: $X.XXM -> $X.XXM | +$X.XXK (+X.X% WoW) | **+X.X% Y/Y** | QTD: +/-X.X% | FQ vs Target: +/-X.X%

### L1 Use Case Commentary

[Narrative bullet for Transformation]
[Narrative bullet for Ingestion]
[Narrative bullet for Interoperable Storage]

**Use Case QTD vs Plan Table:**
| Use Case | QTD Actual | QTD Plan | Delta | Delta % | Mix % | Variance Mag % | Current Week | WoW Change | WoW % |

### L1 Feature Commentary

[Narrative bullet for top feature 1 with customer callouts]
[Narrative bullet for top feature 2 with customer callouts]
...

**Feature QTD vs Plan Table:**
| Use Case | Feature | QTD Actual | QTD Plan | Delta | Delta % | Mix % | Var Mag % | WoW % |

**Feature Customer Movement Tables:**
[Table for each top feature]

**Concentration Assessment:**
| Feature | Top 3 % | Top 10 % | Assessment |

### Use Cases
| Use Case | WoW Change | WoW % | Y/Y % | Mix % | Contribution % | Flag | FQ vs Target |
|----------|------------|-------|-------|-------|----------------|------|--------------|
[Mark with ⚠️ OUTSIZED if contribution % > mix % + 5%]

### Top Features (by Growth Contribution)
| Feature | WoW Change | WoW % | Y/Y % | Mix % | Contribution % | Flag | FQ vs Target |
|---------|------------|-------|-------|-------|----------------|------|--------------|
[Top 10 features with customer movers for top 3-5]
[Mark with ⚠️ OUTSIZED if contribution % > mix % + 5%]

### Dynamic Tables Focus
- **DT Refresh Revenue:** $X.XXM -> $X.XXM | +/-X.X% WoW | FQ vs Target: +/-X.X%
- **DT Table Count:** X,XXX -> X,XXX (+/-X.X% WoW)
- **DT Storage:** X.XX TB -> X.XX TB (+/-X.X% WoW)
- **Top Movers:** [Customer format]

### Snowpark Focus
- **Snowpark DE:** $X.XXM -> $X.XXM | +/-X.X% WoW | FQ vs Target: +/-X.X%
- **All-Up Snowpark:** $X.XXM -> $X.XXM | +/-X.X% WoW
- **Top Movers:** [Customer format]

### TB Ingested
| Modality | Prior | Current | WoW Change | WoW % | Y/Y % |
|----------|-------|---------|------------|-------|-------|
**Total:** X.XX TB -> X.XX TB (+/-X.X% WoW, +/-X.X% Y/Y)

**Top Customers per Modality:**
- **Copy:** [Top 5 customers with TB and WoW %]
- **Snowpipe:** [Top 5 customers with TB and WoW %]
- **Snowpipe Streaming v1:** [Top 5 customers with TB and WoW %]
- **Snowpipe Streaming v2:** [Top 5 customers with TB and WoW %]
- **Connectors:** [Top 5 customers with TB and WoW %]
- **Openflow:** [Top 5 customers with TB and WoW %]


### Anomalous Customers (10 TRUE Anomalies - New Workloads, Migrations, Unexpected Changes)

**Selection Criteria:** 
1. Large movers (|Contribution - Mix| > 1%) 
2. FILTERED by 8-week historical analysis to exclude expected patterns

**EXCLUDE from report:**
- Spike-to-crash returning to baseline (month-end batch jobs)
- Crash-to-spike returning to baseline
- Monthly/weekly cadence patterns
- Normal volatility within historical range

**INCLUDE in report:**
- NEW WORKLOAD: Near-zero -> sustained new level
- STEP CHANGE: Sudden shift to new steady state
- UNEXPECTED CRASH: Below historical baseline (not post-spike return)
- ACCELERATING: 3+ weeks consistent growth
- CHURN SIGNAL: 2+ weeks below historical baseline

**Table Format (REQUIRED):**
| # | Customer | AE | SE | Feature | 8wk Avg | Current | vs Avg | Mix % | Contrib % | Gap | Pattern | Question |
|---|----------|----|----|---------|---------|---------|--------|-------|-----------|-----|---------|----------|

**Column Definitions:**
- **Mix %** = Customer-Feature Revenue / Total DE Revenue
- **Contrib %** = |Customer-Feature WoW Change| / Total Absolute WoW Change
- **Gap** = Contrib % - Mix % (flag ⚠️ if > 0.5%)

**Example Output:**
| # | Customer | AE | SE | Feature | 8wk Avg | Current | vs Avg | Mix % | Contrib % | Gap | Pattern | Question |
|---|----------|----|----|---------|---------|---------|--------|-------|-----------|-----|---------|----------|
| 1 | Komodo Health | M. Gilgallon | M. Gilgallon | DML | $63K | $135K | +114% | 0.28% | 1.28% | +1.0% ⚠️ | EXPANSION | 2x baseline sustained - analytics expansion? |
| 2 | OpenAI | Dave M | Dave M | DML | $33K | $97K | +190% | 0.20% | 1.14% | +0.9% ⚠️ | EXPANSION | DML 3x baseline - new pipeline? |
| 3 | SailPoint | Jon S | Jon S | Task | $60K | $28K | -54% | 0.06% | 0.64% | +0.6% ⚠️ | CRASH | Below baseline - issue or migration? |
| 4 | ServiceTitan | Sean G | Sean G | DE Tools | $8K | $30K | +251% | 0.06% | 0.38% | +0.3% | NEW WORKLOAD | 3.5x baseline - new workload? |

**NOT included (expected patterns):**
- Elevance Health DML: $344K spike -> $204K crash = returning to $200K baseline (EXPECTED)
- NielsenIQ DML: $513K spike -> $377K crash = returning to $320K baseline (EXPECTED)
- Gong.io: $53K spike -> $21K crash = returning to $26K baseline (EXPECTED)

| Signal | Detail |
|--------|--------|
| Risk | [Features/metrics at risk of missing target] |
| Outperformer | [Features/metrics exceeding target] |
| Outsized Movers | [Features where contribution % > mix % + 5% - indicates disproportionate impact] |
| New Adoption | [New customer signals] |
| Churn Signal | [Large declines] |
```

---

## Outsized Mover Logic

**Definition:** A feature/use case is an "outsized mover" when its contribution to the week's change is disproportionately larger than its share of total revenue.

**Formula:** Flag as ⚠️ OUTSIZED when: `contribution_pct > mix_pct + 5`

**Example:**
- Feature has 2% mix (share of total DE revenue)
- Feature has 15% contribution (share of total WoW change)
- 15% > 2% + 5% = 7% → Flag as ⚠️ OUTSIZED

**Interpretation:**
- Outsized movers are driving disproportionate change relative to their size
- Could indicate emerging growth (positive) or concentrated risk (negative)
- Warrants deeper investigation of customer drivers

---

## Concentration Thresholds

| Top 3 % | Assessment |
|---------|------------|
| < 30% | Broad-based (healthy) |
| 30-60% | Moderately concentrated |
| > 60% | Highly concentrated (risk) |

## Customer Format (4 metrics required)
```
Customer Name (+/-$XXK, +/-XX.X% WoW, X.XX% mix, X.XX% contribution)
```

---

## Stopping Points

- ✋ Step 1: After date parameter collection
- ✋ Step 11: Before finalizing report

## Output

Comprehensive DE weekly report with:
- **L1 Use Case Commentary** with narrative insights and variance magnitude analysis
- **L1 Feature Commentary** with customer callouts and concentration assessment
- Full use case and feature breakdown with target variance, Y/Y growth, mix %, and outsized mover flags
- Customer movers for top features with concentration
- Dynamic Tables: Revenue + Table Count + Storage (with Y/Y)
- Snowpark: DE + All-Up Revenue (with Y/Y)
- TB Ingested by modality with Y/Y and top customers per modality
- **Anomalous Customers** with AE/SE, SE comments from dim_use_case, use case descriptions, and feature-level pattern analysis
- Key signals and risks including outsized movers and concentration risks
