---
name: l1-commentary
description: "L1 financial commentary for product categories. Triggers: L1 commentary, revenue analysis, feature performance, use case rollups."
---


# L1 Commentary Generator (v3)


Generate L1 financial commentary for product categories with use case and feature-level analysis.


---


## CRITICAL: Fiscal Calendar Integration


**NEVER guess fiscal quarter dates.** Always query the fiscal calendar table first:


```sql
-- Get fiscal quarter for a given month
SELECT
   fiscal_quarter_fyyyyy_qq,
   MIN(_date) AS quarter_start,
   MAX(_date) AS quarter_end
FROM finance.stg_utils.stg_fiscal_calendar
WHERE fiscal_quarter_fyyyyy_qq = (
   SELECT DISTINCT fiscal_quarter_fyyyyy_qq
   FROM finance.stg_utils.stg_fiscal_calendar
   WHERE _date = '{{analysis_month_start}}'
)
GROUP BY 1
```


**Snowflake Fiscal Year Structure:**
- Fiscal year ends January 31
- Q1: Feb-Apr, Q2: May-Jul, Q3: Aug-Oct, Q4: Nov-Jan
- Example: December 2025 is in **FY2026-Q4** (Nov 1, 2025 - Jan 31, 2026)


---


## Output Format


### Section 1: Use Case Bullet Insights


High-level summary bullets for each use case/feature within the product category:


```
Platform landed in-line with Q4 QTD plan (+$87K, essentially flat) keeping it on track to hit Q4 plan, and grew +3.0% MoM ($1.8M incremental) in December.


Storage small QTD miss (-$30K vs Q4 QTD plan), accounting for 2.3% of variance magnitude despite making up 69% of revenue. Storage incremental dollars have been declining: Oct (+$1.5M) → Nov (+$945K) → Dec (+$908K)


Observability (Log jobs) continues strong Y/Y growth (+182% Q4 QTD) and added +$278K incremental in December, recovering from a weak November (-$34K). However, Log jobs missed Q4 QTD plan by -$129K, accounting for 10.2% of variance magnitude.


CSDG beat Q4 QTD plan by 1.6% (+$201K) accounting for 28.5% of variance magnitude despite only making up 6.7% of revenue — outsized positive contributor.
```


### Section 2: Use Case Tables


Show the data backing the use case bullets:


| Feature | QTD Actual | QTD Plan | Delta | Delta % | Mix % | Variance Magnitude % |
|---------|-----------|----------|-------|---------|-------|---------------------|
| Storage | $86.0M | $86.0M | -$30K | 0.0% | 68.9% | 2.3% |
| Log jobs | $12.9M | $13.0M | -$129K | -1.0% | 10.3% | 10.2% |
| ... | ... | ... | ... | ... | ... | ... |


### Section 3: Feature-Level Bullet Points


Detailed analysis for each material feature with customer callouts:


```
Log jobs recovered in December (+$278K MoM) after November's weakness. Growth was moderately broad-based — top 10 customers contributed 27% of gross positive movement.


Top growers: UNITY (+$45K, +47% MoM), Booking.com (+$38K, +226% MoM), Juniper Networks (+$25K, essentially new), Centene (+$23K), BNY Mellon (+$21K)


DTCC (largest observability customer) did not recover — continued declining from -8.7% in November to flat/slightly down


Logging framework event table access grew +$18K (+21% MoM) with moderately concentrated growth — top 10 customers contributed 64% of growth ($21K of $33K gross positive)


First Data Corporation drove 32% of all growth (+$10.6K, grew from $26K to $37K, +40% MoM). This single customer accounts for nearly a third of the feature's incremental.


Org Usage Views hit $392K and grew +13.5% MoM (vs $345K and +10% MoM last month) — continued healthy growth


Broad based top gainers are LSEG Business Services (+$7K, new customer), Elevance Health (+$5K, new), and BlackRock (+$3K expansion).


Cost Governance declined -18% MoM ($111K vs $135K November). Driven by decrease in SLP


DQ monitoring gains driven by errant usage from Enstar who misconfigured over the holidays for ~$300K driving 80% of growth ***[Need context]***
```


### Section 4: Feature Tables


Show the data backing each feature's analysis:


**Log jobs - Customer MoM Movement**
| Customer | Nov Rev | Dec Rev | Incremental | % of Movement |
|----------|---------|---------|-------------|---------------|
| UNITY | $96K | $141K | +$45K | 5.2% |
| Booking.com | $17K | $54K | +$38K | 4.3% |
| ... | ... | ... | ... | ... |


**Log jobs - Top Decliners**
| Customer | Nov Rev | Dec Rev | Incremental | % of Decline |
|----------|---------|---------|-------------|--------------|
| Reinsurance Group | $61K | $2K | -$59K | 9.8% |
| ... | ... | ... | ... | ... |


---


## Interactive Selection Flow


```
Step 1: Select Product Category
      ↓
Step 2: Select Analysis Month (e.g., December 2025)
      ↓
Step 3: Query Fiscal Calendar for Quarter Dates (MANDATORY)
      ↓
Step 4: Run Period Completeness Check
      ↓
Step 5: Execute Use Case Analysis Queries
      ↓
Step 6: Execute Feature-Level Queries
      ↓
Step 7: Output Use Case Bullets + Tables
      ↓
Step 8: Output Feature Bullets + Tables
```


---


## Step 1: Derive All Date Parameters from Fiscal Calendar


After user selects the analysis month, run this query to get ALL required date parameters:


```sql
WITH analysis_month AS (
   SELECT
       DATE_TRUNC('month', '{{analysis_date}}'::DATE) AS month_start,
       LAST_DAY('{{analysis_date}}'::DATE) AS month_end
),
fiscal_info AS (
   SELECT
       fiscal_quarter_fyyyyy_qq,
       MIN(_date) AS quarter_start,
       MAX(_date) AS quarter_end
   FROM finance.stg_utils.stg_fiscal_calendar
   WHERE fiscal_quarter_fyyyyy_qq = (
       SELECT DISTINCT fiscal_quarter_fyyyyy_qq
       FROM finance.stg_utils.stg_fiscal_calendar
       WHERE _date = (SELECT month_start FROM analysis_month)
   )
   GROUP BY 1
),
prior_month AS (
   SELECT
       DATE_TRUNC('month', DATEADD('month', -1, (SELECT month_start FROM analysis_month))) AS prior_month_start,
       LAST_DAY(DATEADD('month', -1, (SELECT month_start FROM analysis_month))) AS prior_month_end
),
prior_year AS (
   SELECT
       DATEADD('year', -1, (SELECT month_start FROM analysis_month)) AS py_month_start,
       DATEADD('year', -1, (SELECT month_end FROM analysis_month)) AS py_month_end
)
SELECT
   am.month_start AS current_month_start,
   am.month_end AS current_month_end,
   fi.fiscal_quarter_fyyyyy_qq AS fiscal_quarter,
   fi.quarter_start,
   fi.quarter_end,
   -- QTD is from quarter start to current month end
   fi.quarter_start AS qtd_start,
   am.month_end AS qtd_end,
   pm.prior_month_start,
   pm.prior_month_end,
   py.py_month_start AS prior_year_start,
   py.py_month_end AS prior_year_end,
   CASE WHEN am.month_end >= CURRENT_DATE() THEN 'INCOMPLETE' ELSE 'COMPLETE' END AS period_status
FROM analysis_month am
CROSS JOIN fiscal_info fi
CROSS JOIN prior_month pm
CROSS JOIN prior_year py
```


---


## Key Queries


### Use Case Level: Feature Mix with Variance Magnitude


```sql
WITH qtd_actual AS (
   SELECT feature, SUM(revenue) AS actual_revenue
   FROM finance.customer.fy26_product_category_revenue
   WHERE product_category = '{{product_category}}'
       AND ds BETWEEN '{{qtd_start}}' AND '{{qtd_end}}'
   GROUP BY 1
),
qtd_plan AS (
   SELECT feature, SUM(revenue) AS plan_revenue
   FROM finance.dev_sensitive.achatlani_nov_plan_vf
   WHERE product_category = '{{product_category}}'
       AND ds BETWEEN '{{qtd_start}}' AND '{{qtd_end}}'
   GROUP BY 1
),
mom_current AS (
   SELECT feature, SUM(revenue) AS current_rev
   FROM finance.customer.fy26_product_category_revenue
   WHERE product_category = '{{product_category}}'
       AND ds BETWEEN '{{current_month_start}}' AND '{{current_month_end}}'
   GROUP BY 1
),
mom_prior AS (
   SELECT feature, SUM(revenue) AS prior_rev
   FROM finance.customer.fy26_product_category_revenue
   WHERE product_category = '{{product_category}}'
       AND ds BETWEEN '{{prior_month_start}}' AND '{{prior_month_end}}'
   GROUP BY 1
),
combined AS (
   SELECT
       COALESCE(a.feature, p.feature) AS feature,
       COALESCE(a.actual_revenue, 0) AS qtd_actual,
       COALESCE(p.plan_revenue, 0) AS qtd_plan,
       COALESCE(a.actual_revenue, 0) - COALESCE(p.plan_revenue, 0) AS delta_to_plan,
       COALESCE(mc.current_rev, 0) AS current_month_rev,
       COALESCE(mp.prior_rev, 0) AS prior_month_rev,
       COALESCE(mc.current_rev, 0) - COALESCE(mp.prior_rev, 0) AS mom_change
   FROM qtd_actual a
   FULL OUTER JOIN qtd_plan p ON a.feature = p.feature
   LEFT JOIN mom_current mc ON COALESCE(a.feature, p.feature) = mc.feature
   LEFT JOIN mom_prior mp ON COALESCE(a.feature, p.feature) = mp.feature
),
totals AS (
   SELECT
       SUM(qtd_actual) AS total_actual,
       SUM(ABS(delta_to_plan)) AS total_magnitude
   FROM combined
)
SELECT
   c.feature,
   ROUND(c.qtd_actual, 0) AS qtd_actual,
   ROUND(c.qtd_plan, 0) AS qtd_plan,
   ROUND(c.delta_to_plan, 0) AS delta_to_plan,
   ROUND(c.delta_to_plan / NULLIF(c.qtd_plan, 0) * 100, 1) AS delta_pct,
   ROUND(c.qtd_actual / NULLIF(t.total_actual, 0) * 100, 1) AS mix_pct,
   ROUND(ABS(c.delta_to_plan) / NULLIF(t.total_magnitude, 0) * 100, 1) AS variance_magnitude_pct,
   ROUND(c.current_month_rev, 0) AS current_month_rev,
   ROUND(c.prior_month_rev, 0) AS prior_month_rev,
   ROUND(c.mom_change, 0) AS mom_change,
   ROUND(c.mom_change / NULLIF(c.prior_month_rev, 0) * 100, 1) AS mom_pct
FROM combined c
CROSS JOIN totals t
ORDER BY ABS(c.delta_to_plan) DESC
```


### Feature Level: Customer MoM Movement


```sql
WITH nov_revenue AS (
   SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS nov_rev
   FROM finance.customer.fy26_product_category_revenue
   WHERE product_category = '{{product_category}}' AND feature = '{{feature}}'
       AND ds BETWEEN '{{prior_month_start}}' AND '{{prior_month_end}}'
   GROUP BY 1
),
dec_revenue AS (
   SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS dec_rev
   FROM finance.customer.fy26_product_category_revenue
   WHERE product_category = '{{product_category}}' AND feature = '{{feature}}'
       AND ds BETWEEN '{{current_month_start}}' AND '{{current_month_end}}'
   GROUP BY 1
),
combined AS (
   SELECT COALESCE(n.customer, d.customer) AS customer,
       COALESCE(n.nov_rev, 0) AS prior_rev,
       COALESCE(d.dec_rev, 0) AS current_rev,
       COALESCE(d.dec_rev, 0) - COALESCE(n.nov_rev, 0) AS incremental
   FROM nov_revenue n FULL OUTER JOIN dec_revenue d ON n.customer = d.customer
),
totals AS (
   SELECT
       SUM(CASE WHEN incremental > 0 THEN incremental ELSE 0 END) AS total_positive,
       SUM(CASE WHEN incremental < 0 THEN ABS(incremental) ELSE 0 END) AS total_negative
   FROM combined
)
SELECT
   c.customer,
   ROUND(c.prior_rev, 0) AS prior_rev,
   ROUND(c.current_rev, 0) AS current_rev,
   ROUND(c.incremental, 0) AS incremental,
   ROUND(CASE
       WHEN c.incremental > 0 THEN c.incremental / NULLIF(t.total_positive, 0)
       ELSE ABS(c.incremental) / NULLIF(t.total_negative, 0)
   END * 100, 1) AS pct_of_movement,
   ROUND(c.incremental / NULLIF(c.prior_rev, 0) * 100, 1) AS mom_pct
FROM combined c CROSS JOIN totals t
ORDER BY c.incremental DESC
LIMIT 15
```


### Feature Level: Concentration Check


```sql
WITH customer_rev AS (
   SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS rev
   FROM finance.customer.fy26_product_category_revenue
   WHERE product_category = '{{product_category}}' AND feature = '{{feature}}'
       AND ds BETWEEN '{{current_month_start}}' AND '{{current_month_end}}'
   GROUP BY 1
),
ranked AS (
   SELECT customer, rev,
       ROW_NUMBER() OVER (ORDER BY rev DESC) AS rnk,
       SUM(rev) OVER () AS total_rev
   FROM customer_rev
),
movement AS (
   SELECT
       SUM(CASE WHEN incremental > 0 THEN incremental ELSE 0 END) AS gross_positive,
       SUM(CASE WHEN rnk <= 10 AND incremental > 0 THEN incremental ELSE 0 END) AS top10_positive
   FROM (
       SELECT r.rnk,
           COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS incremental
       FROM ranked r
       LEFT JOIN (
           SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS current_rev
           FROM finance.customer.fy26_product_category_revenue
           WHERE product_category = '{{product_category}}' AND feature = '{{feature}}'
               AND ds BETWEEN '{{current_month_start}}' AND '{{current_month_end}}'
           GROUP BY 1
       ) c ON r.customer = c.customer
       LEFT JOIN (
           SELECT latest_salesforce_account_name AS customer, SUM(revenue) AS prior_rev
           FROM finance.customer.fy26_product_category_revenue
           WHERE product_category = '{{product_category}}' AND feature = '{{feature}}'
               AND ds BETWEEN '{{prior_month_start}}' AND '{{prior_month_end}}'
           GROUP BY 1
       ) p ON r.customer = p.customer
   )
)
SELECT
   ROUND(top10_positive / NULLIF(gross_positive, 0) * 100, 1) AS top10_pct_of_growth,
   CASE
       WHEN top10_positive / NULLIF(gross_positive, 0) < 0.30 THEN 'Broad-based'
       WHEN top10_positive / NULLIF(gross_positive, 0) < 0.60 THEN 'Moderately concentrated'
       ELSE 'Highly concentrated'
   END AS concentration_assessment
FROM movement
```


### Monthly Trend (for Oct → Nov → Dec patterns)


```sql
SELECT
   DATE_TRUNC('month', ds) AS month,
   SUM(revenue) AS revenue,
   SUM(revenue) - LAG(SUM(revenue)) OVER (ORDER BY DATE_TRUNC('month', ds)) AS incremental
FROM finance.customer.fy26_product_category_revenue
WHERE product_category = '{{product_category}}' AND feature = '{{feature}}'
   AND ds >= DATEADD('month', -3, '{{current_month_start}}')
GROUP BY 1
ORDER BY 1
```


---


## Data Sources


| Table | Purpose |
|-------|---------|
| `finance.customer.fy26_product_category_revenue` | Actuals revenue data |
| `finance.dev_sensitive.achatlani_nov_plan_vf` | Plan/budget data |
| `finance.stg_utils.stg_fiscal_calendar` | **Fiscal calendar mapping (ALWAYS USE)** |


**Key Columns:**
- Actuals: `ds`, `product_category`, `use_case`, `feature`, `revenue`, `latest_salesforce_account_name`
- Plan: `ds`, `product_category`, `use_case`, `feature`, `revenue`, `salesforce_account_name`
- Calendar: `_date`, `fiscal_quarter_fyyyyy_qq`


---


## Snowflake Connection


- **Connection**: `snowhouse`
- **Role**: FINANCE_DEVELOPMENT_MODELING_RL


---


## Validation Checklist


- [ ] **Fiscal calendar queried first** - never guess quarter dates
- [ ] **Period completeness checked** - mark incomplete periods with `*`
- [ ] **Variance magnitude % sums to 100%** across all features
- [ ] **Concentration assessed** for each feature (broad-based / moderately concentrated / highly concentrated)
- [ ] **Monthly trend included** where relevant (Oct → Nov → Dec)
- [ ] **All tables shown** backing each set of bullets
- [ ] **`***[Need context]***` flags** for unexplained anomalies


---


## Version History


| Date | Version | Change |
|------|---------|--------|
| 2025-12-31 | v1 | Initial single-feature L1 process |
| 2026-01-14 | v2 | Added use case rollup, multi-feature support |
| 2026-01-21 | v3 | **Mandatory fiscal calendar integration**, new output format with Use Case Bullets → Use Case Tables → Feature Bullets → Feature Tables |




