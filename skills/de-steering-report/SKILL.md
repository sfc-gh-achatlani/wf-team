---
name: de-steering-report
description: "Generate HTML DE Steering Report with hierarchical drill-down tables for Storage Under Management, TB Ingested by Modality, and DE Revenue. Outputs interactive HTML with expand/collapse functionality. Triggers: DE steering report, steering report, DE storage report, generate steering report, DE HTML report."
---

# DE Steering Report Generator

Generates an interactive HTML steering report for Data Engineering with three main sections:
1. **Storage Under Management** - Hierarchical breakdown by storage modality
2. **TB Ingested by Modality** - Ingestion volumes with customer drilldowns
3. **DE Revenue** - Revenue by use case/feature with Δ Plan QTD and Δ Target FQ

## Output Format
- **HTML file** with interactive expand/collapse tables
- Spreadsheet-style layout, Arial font
- Financial formatting: negatives in parentheses `(X.X%)`
- Green/red backgrounds for gainers/contractors
- Collapsible hierarchies: Click to expand Top 5 Customers, Gainers, Contractors
- Footnotes section for excluded accounts and methodology notes

## Account Exclusions

**ALWAYS exclude the following accounts from metrics:**

| Account | Excluded From | Reason |
|---------|---------------|--------|
| Palo Alto Networks Inc. | TB Ingested (all modalities), Snowpipe Streaming v2 | Large POC in November 2024 that is not continuing. Volume was large enough to meaningfully skew metrics. |

**Implementation:** Add `AND a.salesforce_account_name NOT IN ('Palo Alto Networks Inc.')` filter to TB Ingested queries.

## Workflow

### Step 1: Collect Parameters

**Ask user for date parameters:**

| Parameter | Description | Example |
|-----------|-------------|---------|
| Report Date | Data as of date | 2026-01-21 |
| QTD Start | Current quarter start | 2025-11-01 |
| QTD End | Current quarter end | 2026-01-31 |
| Prior QTD Start | Prior quarter start | 2025-08-01 |
| Prior QTD End | Prior quarter end | 2025-10-31 |

**FY26 Quarter Reference:**
- Q1: Feb 1 - Apr 30
- Q2: May 1 - Jul 31
- Q3: Aug 1 - Oct 31
- Q4: Nov 1 - Jan 31

### Step 2: Calculate QTD Normalization

Use `day_of_fiscal_quarter` from fiscal calendar to ensure Q/Q comparisons are apples-to-apples:

```sql
WITH current_qtd_day AS (
    SELECT day_of_fiscal_quarter 
    FROM snowhouse.utils.fiscal_calendar 
    WHERE _date = CURRENT_DATE - 2
),
prior_qtd_end AS (
    SELECT _date AS prior_qtd_date
    FROM snowhouse.utils.fiscal_calendar
    WHERE fiscal_quarter_fyyyyqq = 'FY2026-Q3'
      AND day_of_fiscal_quarter = (SELECT day_of_fiscal_quarter FROM current_qtd_day)
)
SELECT * FROM prior_qtd_end
```

### Step 3: Storage Under Management Data

**CRITICAL: Storage is calculated as AVERAGE daily TiB over the quarter, NOT a sum or point-in-time snapshot.**
- Use `power(1024,4)` for TiB conversion (NOT 1e12 for TB)
- Use `dim_accounts_history` with `general_date` join
- Calculate AVG per customer per quarter, then SUM across all customers
- Use `day_of_fiscal_quarter` normalization for Q/Q comparisons
- Include Block storage in "Stored by Snow"

**Hierarchy:**
```
QTD Under Management
├── Stored by Snow (FDN + Failsafe + Stage + Hybrid + Block)
│   ├── FDN
│   ├── Failsafe
│   ├── Stage
│   ├── Hybrid Tables
│   └── Block
├── Managed by Snow (Directory + Managed Iceberg)
│   ├── Directory Tables
│   └── Snowflake Managed Iceberg
└── Serviceable by Snow (External + Unmanaged Iceberg)
    ├── External Tables
    └── Externally Managed Iceberg
```

**Query Pattern for Storage (AVERAGE over quarter):**
```sql
with qtd as (
    select day_of_fiscal_quarter as day_q
    from finance.stg_utils.stg_fiscal_calendar
    where _date = current_date - 3  -- report_date
),
storage_rollups as (
    select ds, salesforce_account_name,
        sum(fdn_storage_bytes) / power(1024,4) as fdn,
        sum(managed_iceberg_table_bytes) / power(1024,4) as managed_iceberg,
        sum(unmanaged_iceberg_table_bytes) / power(1024,4) as unmanaged_iceberg,
        sum(hybrid_storage_bytes) / power(1024,4) as hybrid,
        sum(failsafe_storage_bytes) / power(1024,4) as failsafe,
        sum(stage_bytes) / power(1024,4) as stage,
        sum(block_storage_bytes) / power(1024,4) as block,
        sum(directory_table_bytes) / power(1024,4) as directory,
        sum(external_table_bytes) / power(1024,4) as external_table
    from snowscience.data_engineering.storage as storage
    left join snowscience.dimensions.dim_accounts_history as account_meta
        on storage.deployment = account_meta.snowflake_deployment 
        and storage.account_id = account_meta.snowflake_account_id    
        and storage.ds = account_meta.general_date
    where account_meta.snowflake_account_type in ('Customer', 'Partner') 
    group by all
),
-- For each quarter: AVG per customer, then SUM across customers
q4_totals as (
    select sum(avg_fdn) as fdn, sum(avg_failsafe) as failsafe, sum(avg_stage) as stage,
        sum(avg_hybrid) as hybrid, sum(avg_block) as block, sum(avg_directory) as directory,
        sum(avg_managed_iceberg) as managed_iceberg, sum(avg_external) as external_table,
        sum(avg_unmanaged_iceberg) as unmanaged_iceberg
    from (
        select salesforce_account_name, 
            avg(fdn) as avg_fdn, avg(failsafe) as avg_failsafe, avg(stage) as avg_stage, 
            avg(hybrid) as avg_hybrid, avg(block) as avg_block, avg(directory) as avg_directory, 
            avg(managed_iceberg) as avg_managed_iceberg, avg(external_table) as avg_external, 
            avg(unmanaged_iceberg) as avg_unmanaged_iceberg
        from storage_rollups
        join snowhouse.utils.fiscal_calendar as cal on cal._date = storage_rollups.ds
        where fiscal_quarter_fyyyyy_qq = 'FY2026-Q4' 
          and day_of_fiscal_quarter <= (select day_q from qtd)
        group by salesforce_account_name
    )
),
-- Repeat for prior quarter (FY2026-Q3) and prior year (FY2025-Q4)
...
```

**For each modality, extract:**
- Total QTD TB
- Q/Q % change
- Y/Y % change
- Top 5 Customers by TB
- Top 5 Gainers Q/Q (positive Q/Q change, ranked by absolute TB gain)
- Top 5 Contractors Q/Q (negative Q/Q change, ranked by absolute TB loss)

### Step 4: TB Ingested Data

**Modalities:**
- Copy
- Snowpipe
- Snowpipe Streaming v2
- Snowpipe Streaming v1
- Connectors
- Openflow

**IMPORTANT: Apply account exclusions (see Account Exclusions section above)**

**Query Pattern:**
```sql
WITH current_qtd AS (
    SELECT 
        ing.ingestion_type AS modality,
        a.salesforce_account_name AS customer,
        SUM(ing.tbytes) AS current_tb
    FROM snowscience.data_engineering.ingestion ing
    JOIN snowscience.dimensions.dim_snowflake_accounts a
        ON a.snowflake_deployment = ing.deployment
        AND a.snowflake_account_id = ing.account_id
    WHERE ing.ds BETWEEN :qtd_start AND :report_date
      AND a.snowflake_account_type IN ('Customer', 'Partner')
      AND a.salesforce_account_name NOT IN ('Palo Alto Networks Inc.')  -- Exclude POC accounts
    GROUP BY 1, 2
),
prior_qtd AS (
    SELECT 
        ing.ingestion_type AS modality,
        a.salesforce_account_name AS customer,
        SUM(ing.tbytes) AS prior_tb
    FROM snowscience.data_engineering.ingestion ing
    JOIN snowscience.dimensions.dim_snowflake_accounts a
        ON a.snowflake_deployment = ing.deployment
        AND a.snowflake_account_id = ing.account_id
    WHERE ing.ds BETWEEN :prior_qtd_start AND :prior_qtd_normalized_end
      AND a.snowflake_account_type IN ('Customer', 'Partner')
      AND a.salesforce_account_name NOT IN ('Palo Alto Networks Inc.')  -- Exclude POC accounts
    GROUP BY 1, 2
)
SELECT 
    COALESCE(c.modality, p.modality) AS modality,
    COALESCE(c.customer, p.customer) AS customer,
    COALESCE(c.current_tb, 0) AS current_tb,
    COALESCE(p.prior_tb, 0) AS prior_tb,
    ROUND((COALESCE(c.current_tb, 0) - COALESCE(p.prior_tb, 0)) / NULLIF(p.prior_tb, 0), 4) AS qq_change
FROM current_qtd c
FULL OUTER JOIN prior_qtd p ON c.modality = p.modality AND c.customer = p.customer
ORDER BY current_tb DESC
```

### Step 5: DE Revenue Data

**Hierarchy:**
```
All Up DE Revenue
├── Transformation
│   ├── DML
│   ├── Task
│   ├── Snowpark DE
│   ├── DT Refresh
│   └── Stream Access
├── Ingestion
│   ├── COPY
│   ├── Snowpipe
│   ├── Openflow
│   ├── Spark Connector
│   └── UNLOAD
└── Interoperable Storage
    └── Iceberg DML
```

**Revenue Query with Δ Plan QTD and Δ Target FQ:**
```sql
WITH plan_revenue AS (
    SELECT ds, product_category, use_case, feature, SUM(revenue) AS revenue
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds <= (SELECT MAX(forecast_run_date) FROM finance.customer.plan_vs_most_recent_estimate WHERE is_plan = TRUE)
      AND ds >= :qtd_start
      AND product_category = 'Data Engineering'
    GROUP BY ALL
    UNION ALL
    SELECT general_date AS ds, product_category, use_case, feature, SUM(revenue) AS revenue
    FROM finance.customer.product_category_revenue_forecast_sfdc_temp
    WHERE forecast_run_date = (SELECT MAX(forecast_run_date) FROM finance.customer.plan_vs_most_recent_estimate WHERE is_plan = TRUE)
      AND general_date >= :qtd_start
      AND product_category = 'Data Engineering'
    GROUP BY ALL
),
realized_revenue AS (
    SELECT ds, use_case, feature, latest_salesforce_account_name AS customer, SUM(revenue) AS revenue
    FROM finance.customer.fy26_product_category_revenue
    WHERE ds >= :qtd_start AND ds <= :report_date
      AND product_category = 'Data Engineering'
    GROUP BY ALL
),
last_actual_date AS (
    SELECT MAX(ds) AS max_ds FROM realized_revenue
),
qtd_plan AS (
    SELECT use_case, feature, SUM(revenue) AS plan_revenue
    FROM plan_revenue
    WHERE ds <= (SELECT max_ds FROM last_actual_date)
    GROUP BY 1, 2
),
fq_forecast AS (
    SELECT use_case, feature, SUM(revenue) AS fq_revenue
    FROM finance.customer.product_category_rev_actuals_w_forecast_sfdc
    WHERE product_category = 'Data Engineering'
      AND usage_date BETWEEN :qtd_start AND :qtd_end
    GROUP BY 1, 2
),
fq_target AS (
    SELECT use_case, feature, SUM(target_revenue) AS target_revenue
    FROM finance.raw_google_sheets.fy_26_product_category_feature_targets
    WHERE fiscal_quarter_fyyyyy_qq = 'FY2026-Q4'
      AND product_category = 'Data Engineering'
    GROUP BY 1, 2
)
SELECT 
    r.use_case,
    r.feature,
    SUM(r.revenue) AS qtd_actual,
    p.plan_revenue AS qtd_plan,
    ROUND((SUM(r.revenue) / NULLIF(p.plan_revenue, 0)) - 1, 4) AS delta_plan_qtd,
    f.fq_revenue,
    t.target_revenue AS fq_target,
    ROUND((f.fq_revenue / NULLIF(t.target_revenue, 0)) - 1, 4) AS delta_target_fq
FROM realized_revenue r
LEFT JOIN qtd_plan p ON r.use_case = p.use_case AND r.feature = p.feature
LEFT JOIN fq_forecast f ON r.use_case = f.use_case AND r.feature = f.feature
LEFT JOIN fq_target t ON r.use_case = t.use_case AND r.feature = t.feature
GROUP BY r.use_case, r.feature, p.plan_revenue, f.fq_revenue, t.target_revenue
ORDER BY SUM(r.revenue) DESC
```

**For each feature, extract:**
- QTD Revenue
- Q/Q % change
- Y/Y % change
- Δ Plan QTD = `(qtd_actual / qtd_plan) - 1`
- Δ Target FQ = `(fq_forecast / fq_target) - 1`
- Top 5 Customers by revenue
- Top 5 Gainers Q/Q
- Top 5 Contractors Q/Q

### Step 6: Generate HTML Report

**HTML Structure:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DE Steering Report - FY2026-Q4</title>
    <style>
        /* Styles for hierarchical tables */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, Helvetica, sans-serif; background: #f8f9fa; font-size: 13px; }
        .container { max-width: 1400px; margin: 0 auto; padding: 32px 24px; }
        
        /* Row levels for hierarchy */
        .row-l0 { background: linear-gradient(90deg, #1a73e8 0%, #1a73e8 4px, #e8f0fe 4px); font-weight: 600; }
        .row-l1 { background: #f8f9fa; font-weight: 600; }
        .row-l1 td:first-child { padding-left: 28px; }
        .row-l2 { background: #fff; font-weight: 500; }
        .row-l2 td:first-child { padding-left: 48px; }
        .row-l3 { background: #fafbfc; font-size: 11px; font-weight: 600; text-transform: uppercase; }
        .row-l3 td:first-child { padding-left: 68px; }
        .row-l4 { font-size: 12px; }
        .row-l4 td:first-child { padding-left: 84px; }
        
        /* Gainers/Contractors styling */
        .row-gainer { background: linear-gradient(90deg, rgba(52, 168, 83, 0.12) 0%, rgba(52, 168, 83, 0.03) 100%); border-left: 3px solid #34a853; }
        .row-contractor { background: linear-gradient(90deg, rgba(234, 67, 53, 0.12) 0%, rgba(234, 67, 53, 0.03) 100%); border-left: 3px solid #ea4335; }
        
        /* Expand/collapse */
        .toggle { cursor: pointer; }
        .toggle td:first-child::before { content: '▸'; display: inline-block; width: 16px; }
        .toggle.expanded td:first-child::before { transform: rotate(90deg); }
        .hidden { display: none; }
        
        /* Positive/Negative colors */
        .positive { color: #137333; }
        .negative { color: #c5221f; }
        
        /* NEW badge */
        .badge-new { background: #e6f4ea; color: #137333; padding: 2px 6px; border-radius: 4px; font-size: 9px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Engineering Steering Report</h1>
        <p class="subtitle">FY2026-Q4 QTD (Day XX) • Data as of [DATE]</p>
        
        <!-- Section 1: Storage Under Management -->
        <h2>Storage Under Management</h2>
        <table class="tbl-storage">
            <thead><tr><th>Storage Modality</th><th>QTD TB</th><th>Q/Q</th><th>Y/Y</th></tr></thead>
            <tbody>
                <!-- Hierarchical rows with toggle functionality -->
            </tbody>
        </table>
        
        <!-- Section 2: TB Ingested by Modality -->
        <h2>TB Ingested by Modality</h2>
        <table class="tbl-storage">
            <!-- Similar structure -->
        </table>
        
        <!-- Section 3: DE Revenue -->
        <h2>DE Revenue</h2>
        <table class="tbl-rev">
            <thead><tr><th>Use Case / Feature</th><th>QTD Revenue</th><th>Q/Q</th><th>Y/Y</th><th>Δ Plan QTD</th><th>Δ Target FQ</th></tr></thead>
            <tbody>
                <!-- Revenue hierarchy -->
            </tbody>
        </table>
    </div>
    
    <script>
        // Toggle expand/collapse functionality
        document.querySelectorAll('.toggle').forEach(row => {
            row.addEventListener('click', function() {
                const target = this.dataset.target;
                if (!target) return;
                this.classList.toggle('expanded');
                document.querySelectorAll('.' + target).forEach(child => {
                    child.classList.toggle('hidden');
                    if (child.classList.contains('hidden')) {
                        child.classList.remove('expanded');
                        const childTarget = child.dataset.target;
                        if (childTarget) {
                            document.querySelectorAll('.' + childTarget).forEach(gc => gc.classList.add('hidden'));
                        }
                    }
                });
            });
        });
    </script>
</body>
</html>
```

### Step 7: Format Numbers

**Formatting Rules:**
- TB values: Comma-separated with no decimals (e.g., `3,395,596`)
- Revenue: Dollar sign with commas (e.g., `$538,089,745`)
- Percentages: One decimal, positive with class `positive`, negative in parentheses with class `negative`
  - Positive: `<td class="positive">10.1%</td>`
  - Negative: `<td class="negative">(4.6%)</td>`
- New items: `<span class="badge badge-new">NEW</span>`

### Step 8: Add Footnotes

**Always include a footnotes section at the bottom of the HTML report:**

```html
<div class="footnotes">
    <h3>Notes</h3>
    <ol>
        <li><strong>Palo Alto Networks Inc.</strong> has been excluded from TB Ingested and Snowpipe Streaming v2 metrics. 
            This account had a large POC in November that is not continuing; the volume was large enough to meaningfully skew data.</li>
    </ol>
</div>
```

**CSS for footnotes:**
```css
.footnotes { margin-top: 32px; padding: 16px; background: #fff8e1; border-left: 4px solid #ffc107; border-radius: 4px; }
.footnotes h3 { font-size: 14px; margin-bottom: 8px; color: #5f6368; }
.footnotes ol { margin-left: 20px; font-size: 12px; color: #5f6368; }
.footnotes li { margin-bottom: 8px; }
```

### Step 9: Save and Present

1. Save HTML file to user's directory: `/Users/achatlani/de_steering_report.html`
2. Provide path to user
3. Report can be opened in any browser

---

## Data Sources

| Table | Purpose |
|-------|---------|
| `snowscience.data_engineering.storage` | Storage TB by modality |
| `snowscience.data_engineering.ingestion` | TB ingested by modality |
| `snowscience.dimensions.dim_snowflake_accounts` | Account metadata |
| `snowscience.dimensions.dim_accounts_history` | Historical account mapping |
| `snowhouse.utils.fiscal_calendar` | Fiscal quarter normalization |
| `finance.customer.fy26_product_category_revenue` | Revenue actuals |
| `finance.customer.product_category_revenue_forecast_sfdc_temp` | Plan forecast |
| `finance.customer.product_category_rev_actuals_w_forecast_sfdc` | Actuals + forecast |
| `finance.raw_google_sheets.fy_26_product_category_feature_targets` | FQ targets |
| `finance.customer.plan_vs_most_recent_estimate` | Plan run date |

---

## Key Calculations

### Δ Plan QTD (CORRECTED)
```sql
delta_plan_qtd = (qtd_actual / qtd_plan) - 1
-- WHERE qtd_plan is filtered to ds <= max(actual_ds) for proper date alignment
```

### Δ Target FQ
```sql
delta_target_fq = (fq_forecast / fq_target) - 1
```

### Q/Q Change (Normalized)
```sql
qq_change = (current_qtd - prior_qtd_normalized) / prior_qtd_normalized
-- Use day_of_fiscal_quarter to align comparison periods
```

---

## Triggers
DE steering report, steering report, DE storage report, generate steering report, DE HTML report, storage under management, TB ingested report

## Output
Interactive HTML file at `/Users/achatlani/de_steering_report.html` with:
- Expandable/collapsible hierarchy
- Top 5 Customers per modality/feature
- Top 5 Gainers Q/Q (green highlight)
- Top 5 Contractors Q/Q (red highlight)
- Δ Plan QTD and Δ Target FQ columns in Revenue section
- Footnotes section documenting excluded accounts and methodology notes
