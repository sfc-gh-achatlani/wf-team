# DCR Weekly Report Skill

## What This Does

Generates an interactive HTML report for Data Clean Room (DCR) metrics including:
- **Executive KPIs**: Weekly revenue, QTD vs Plan, Active accounts, Credits
- **Revenue Trend**: 60-day daily revenue chart
- **DAU/WAU/MAU**: Active account trends (Customers vs All)
- **Credits Analysis**: Daily credits with 7-day moving average
- **Partner Edges**: Provider ↔ Consumer relationships with credits
- **Top Customers**: By revenue and by credits with WoW changes
- **Job Buckets**: Breakdown by job type

---

## Step 1: Run the Report

Execute this command (replace YYYY-MM-DD with the week end date, Sunday):

```bash
SNOWFLAKE_CONNECTION_NAME=<your_connection> uv run python run_dcr_report.py --week-end YYYY-MM-DD
```

**Example:**
```bash
SNOWFLAKE_CONNECTION_NAME=snowhouse uv run python run_dcr_report.py --week-end 2026-01-25
```

---

## Step 2: Open the Report

```bash
open output/dcr_report_YYYY-MM-DD.html
```

---

## Data Sources

| Metric | Source Table |
|--------|--------------|
| DCR Revenue | `finance.customer.fy26_product_category_revenue` (feature='Data Clean Room') |
| Active Accounts | `snowscience.cleanrooms.samooha_consumption_v` |
| Credits (jobs) | `snowscience.cleanrooms.samooha_consumption_v` |
| Credits (SPCS direct) | `snowscience.cleanrooms.samooha_spcs_credits` |
| Credits (SPCS indirect) | `snowscience.snowservices.spcs_credits_indirect_*` |
| Partner Edges | `snowscience.cleanrooms.all_cleanroom_jobs` + `cleanroom_edges` |
| Plans | `finance.customer.temp_product_category_revenue_plan` |

---

## Output Location

Reports saved to:
```
output/dcr_report_YYYY-MM-DD.html
```

---

## Queries Integrated

1. **DAU/WAU/MAU** - Active accounts with rolling windows
2. **Total Credits** - Samooha jobs + SPCS direct + SPCS indirect (deduped)
3. **Partner Edges** - Provider/consumer relationships with stable edge flags
4. **Revenue WoW** - Week-over-week revenue change
5. **QTD vs Plan** - Quarter-to-date actuals vs plan
