---
name: weekly-metrics-report
description: "Generate weekly HTML report with product category metrics. Triggers: weekly report, weekly metrics, weekly analysis, WoW report, product category weekly."
---

# Weekly Metrics Report Skill

## What This Does

Generates an interactive HTML report showing:
- Executive KPIs (Total Revenue, QTD vs Plan)
- Forecast Evolution Line Chart (dual Y-axis for AI/ML)
- Full Quarter Forecast vs Plan vs Target table
- QTD Variance bar chart
- Product Category drill-down (Category → Use Case → Feature → Customer)
- Top 25 Customers with feature breakdown
- Top 15 Gainers and Top 15 Contractors

---

## Step 1: Ask for Week End Date

**REQUIRED: Ask the user for the week end date.**

Ask: "What is the week end date (Sunday) for this report? Format: YYYY-MM-DD"

Example valid dates:
- 2026-01-19 (Sunday)
- 2026-01-26 (Sunday)

---

## Step 2: Run the Report

Execute this command (replace YYYY-MM-DD with the date from Step 1):

```bash
SNOWFLAKE_CONNECTION_NAME=<your_connection> uv run python run_report.py --week-end YYYY-MM-DD
```

**Example:**
```bash
SNOWFLAKE_CONNECTION_NAME=snowhouse uv run python run_report.py --week-end 2026-01-19
```

---

## Step 3: Open the Report

After the command completes, open the generated HTML file:

```bash
open output/report_YYYY-MM-DD.html
```

---

## Date Calculations (Automatic)

The script automatically calculates:
| Parameter | Calculation |
|-----------|-------------|
| Week Start | week_end - 6 days |
| Prior Week | 7 days before current week |
| QTD Start | From fiscal calendar table |

---

## Snowflake Connection

Set via environment variable in the command:
```
SNOWFLAKE_CONNECTION_NAME=<your_connection>
```

---

## Output Location

Reports are saved to:
```
output/report_YYYY-MM-DD.html
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "connection_name not found" | Ensure SNOWFLAKE_CONNECTION_NAME is set in the command |
| "week-end is required" | Must provide --week-end YYYY-MM-DD parameter |
| Report doesn't open | Check the output path exists |
