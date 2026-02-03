---
name: l1-commentary
description: "L1 financial commentary for product categories. Triggers: L1 commentary, revenue analysis, feature performance, use case rollups."
---

# L1 Commentary Generator (v5) - Hierarchical Quarterly Analysis

**Consistent analysis framework at every level of the hierarchy.**

```
Category → Use Case → Feature → Customer
    ↓          ↓          ↓          ↓
 [Same Analysis Set at Each Level]
```

---

## Quick Start

```bash
SNOWFLAKE_CONNECTION_NAME=snowhouse uv run python run_report.py --fiscal-quarter FY2026-Q4
```

---

## Hierarchical Structure

Click-to-expand navigation where **every level** shows the same analysis:

| Level | Example | Drill Into |
|-------|---------|------------|
| **Total** | All Categories | Categories |
| **Category** | Analytics, Platform | Use Cases |
| **Use Case** | BI Reporting, Data Science | Features |
| **Feature** | Dashboards, Notebooks | Customers |
| **Customer** | Acme Corp, TechCo | (leaf) |

---

## Standard Analysis Set (at EVERY level)

Each entity in the hierarchy shows:

| # | Analysis | Description |
|---|----------|-------------|
| 1 | **Summary KPIs** | QTD Revenue, vs Plan ($ and %), YoY %, QoQ % |
| 2 | **Monthly Trends** | Oct → Nov → Dec → Jan progression with MoM delta |
| 3 | **Top 20 vs Long Tail** | Revenue concentration by child entities |
| 4 | **Industry Performance** | Breakdown by industry_rollup with YoY/QoQ |
| 5 | **New vs Existing** | NEW, EXISTING (Growing >+5% / Stagnant / Shrinking <-5%), CHURNED |
| 6 | **Top Gainers** | Top 10 growing child entities by delta |
| 7 | **Top Contractors** | Top 10 declining child entities by delta |
| 8 | **Concentration Trend** | Top 10/20 customer share over months |
| 9 | **Children Breakdown** | Full breakdown of child entities vs plan |

---

## Output Files

```
output/
├── l1_report_{quarter}.html    # Interactive click-to-expand
├── l1_report_{quarter}.md      # Markdown summary
└── l1_data_{quarter}.json      # Raw hierarchical data
```

---

## HTML Report Features

- **Click-to-Expand**: Click any entity header to show its analysis
- **Consistent Layout**: Same 9 analysis cards at every level
- **Control Buttons**: Expand All, Collapse All, Expand to Level
- **Color-Coded**: Level depth shown by header color
- **Performance Indicators**: Green/red for positive/negative metrics

---

## Customer Segmentation (at every level)

| Segment | Definition |
|---------|------------|
| **NEW** | No revenue in prior quarter, revenue this quarter |
| **EXISTING - GROWING** | QoQ Growth > +5% |
| **EXISTING - STAGNANT** | QoQ Growth between -5% and +5% |
| **EXISTING - SHRINKING** | QoQ Growth < -5% |
| **CHURNED** | Revenue in prior quarter, none this quarter |

---

## Fiscal Calendar

| Quarter | Period |
|---------|--------|
| FY2026-Q1 | Feb 1 - Apr 30, 2025 |
| FY2026-Q2 | May 1 - Jul 31, 2025 |
| FY2026-Q3 | Aug 1 - Oct 31, 2025 |
| FY2026-Q4 | Nov 1, 2025 - Jan 31, 2026 |

---

## Data Sources

| Table | Purpose |
|-------|---------|
| `finance.customer.fy26_product_category_revenue` | Actuals (revenue + product_led_revenue) |
| `finance.customer.temp_product_category_revenue_plan` | Plan at feature level |
| `finance.stg_utils.stg_fiscal_calendar` | Fiscal calendar dates |

---

## Snowflake Connection

- **Connection**: `snowhouse`
- **Role**: FINANCE_DEVELOPMENT_MODELING_RL

---

## Version History

| Date | Version | Change |
|------|---------|--------|
| 2025-12-31 | v1 | Initial single-feature process |
| 2026-01-14 | v2 | Multi-feature support |
| 2026-01-21 | v3 | Fiscal calendar integration |
| 2026-02-02 | v4 | 15 sections, dual output |
| 2026-02-02 | v5 | **Hierarchical restructure**: Same analysis at every level (Category→Use Case→Feature→Customer), click-to-expand navigation |
