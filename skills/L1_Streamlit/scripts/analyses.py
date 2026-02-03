"""
analyses.py - Individual Analysis Functions

Each function implements one type of analysis that can be applied at
different hierarchy levels. Functions return empty results gracefully
rather than failing on edge cases.

NAMING CONVENTION:
    get_<analysis_name>(conn, dates, run_date, **filters) -> List[Dict] or Dict

All functions accept:
    - conn: Snowflake connection
    - dates: FiscalDates object
    - run_date: Snapshot date to filter actuals data
    - category, use_case, feature, customer: Optional filters
"""

from typing import Any, Dict, List, Optional
from datetime import date

from .db import execute_query
from .config import (
    ACTUALS_TABLE, PLAN_TABLE, HIERARCHY, RUN_DATE_COLUMN,
    GROWTH_THRESHOLD, SHRINK_THRESHOLD,
    MAX_GAINERS, MAX_CONTRACTORS, MAX_INDUSTRIES,
    EXTENDED_TREND_MONTHS, MAX_TOP_CUSTOMERS,
)
from .filters import build_actuals_filter, build_plan_filter
from .fiscal import FiscalDates


def _run_date_filter(run_date: date) -> str:
    """Build run_date filter clause for actuals queries."""
    return f"{RUN_DATE_COLUMN} = '{run_date}'"


# =============================================================================
# SUMMARY KPIs
# =============================================================================

def get_summary_kpis(
    conn,
    dates: FiscalDates,
    run_date: date,
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get high-level KPIs: QTD Revenue, vs Plan, YoY%, QoQ%.
    """
    actuals_filter = build_actuals_filter(category, use_case, feature, customer)
    plan_filter = build_plan_filter(category, use_case, feature, customer)
    rd_filter = _run_date_filter(run_date)
    
    query = f"""
    WITH cq_revenue AS (
        SELECT COALESCE(SUM(revenue + product_led_revenue), 0) AS cq_rev
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {actuals_filter}
    ),
    pq_revenue AS (
        SELECT COALESCE(SUM(revenue + product_led_revenue), 0) AS pq_rev
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.pq_start}' AND '{dates.pq_end}'
            AND {actuals_filter}
    ),
    py_revenue AS (
        SELECT COALESCE(SUM(revenue + product_led_revenue), 0) AS py_rev
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.py_start}' AND '{dates.py_end}'
            AND {actuals_filter}
    ),
    plan_revenue AS (
        SELECT COALESCE(SUM(revenue), 0) AS plan_rev
        FROM {PLAN_TABLE}
        WHERE ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {plan_filter}
    )
    SELECT 
        ROUND(cq.cq_rev, 0) AS qtd_revenue,
        ROUND(p.plan_rev, 0) AS qtd_plan,
        ROUND(cq.cq_rev - p.plan_rev, 0) AS delta_to_plan,
        ROUND(100.0 * (cq.cq_rev - p.plan_rev) / NULLIF(p.plan_rev, 0), 2) AS pct_vs_plan,
        ROUND(100.0 * (cq.cq_rev - py.py_rev) / NULLIF(py.py_rev, 0), 2) AS yoy_growth_pct,
        ROUND(100.0 * (cq.cq_rev - pq.pq_rev) / NULLIF(pq.pq_rev, 0), 2) AS qoq_growth_pct,
        ROUND(pq.pq_rev, 0) AS prior_q_revenue,
        ROUND(py.py_rev, 0) AS prior_year_revenue
    FROM cq_revenue cq
    CROSS JOIN pq_revenue pq
    CROSS JOIN py_revenue py
    CROSS JOIN plan_revenue p
    """
    
    results = execute_query(conn, query, "Summary KPIs")
    return results[0] if results else {}


# =============================================================================
# DAILY TRENDS (CURRENT QUARTER)
# =============================================================================

def get_monthly_trends(
    conn,
    dates: FiscalDates,
    run_date: date,
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
    extended_months: int = EXTENDED_TREND_MONTHS,
) -> List[Dict[str, Any]]:
    """
    Get daily revenue vs plan for the current quarter.
    Shows cumulative actuals vs cumulative plan by day.
    """
    actuals_filter = build_actuals_filter(category, use_case, feature, customer)
    plan_filter = build_plan_filter(category, use_case, feature, customer)
    rd_filter = _run_date_filter(run_date)
    
    query = f"""
    WITH actuals AS (
        SELECT 
            ds AS day,
            SUM(revenue + product_led_revenue) AS daily_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    plan AS (
        SELECT 
            ds AS day,
            SUM(revenue) AS daily_plan
        FROM {PLAN_TABLE}
        WHERE ds BETWEEN '{dates.q_start}' AND '{dates.q_end}'
            AND {plan_filter}
        GROUP BY 1
    ),
    combined AS (
        SELECT 
            COALESCE(a.day, p.day) AS day,
            COALESCE(a.daily_revenue, 0) AS daily_revenue,
            COALESCE(p.daily_plan, 0) AS daily_plan
        FROM actuals a
        FULL OUTER JOIN plan p ON a.day = p.day
    )
    SELECT 
        day,
        ROUND(daily_revenue, 0) AS revenue,
        ROUND(daily_plan, 0) AS plan_revenue,
        ROUND(SUM(daily_revenue) OVER (ORDER BY day), 0) AS cumulative_revenue,
        ROUND(SUM(daily_plan) OVER (ORDER BY day), 0) AS cumulative_plan
    FROM combined
    WHERE day <= '{dates.effective_end}'
    ORDER BY day
    """
    
    results = execute_query(conn, query, "Daily trends (current quarter)")
    
    for row in results:
        if row.get('cumulative_plan'):
            row['vs_plan'] = row['cumulative_revenue'] - row['cumulative_plan']
            row['vs_plan_pct'] = round(100.0 * row['vs_plan'] / row['cumulative_plan'], 2) if row['cumulative_plan'] else None
    
    return results


# =============================================================================
# CHILDREN BREAKDOWN
# =============================================================================

def get_children_breakdown(
    conn,
    dates: FiscalDates,
    run_date: date,
    level: str,
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get breakdown of child entities with revenue and growth metrics.
    """
    hierarchy_level = HIERARCHY.get(level)
    if not hierarchy_level or not hierarchy_level.child_level:
        return []
    
    child_config = HIERARCHY[hierarchy_level.child_level]
    child_column = child_config.column
    plan_child_column = "salesforce_account_name" if child_column == "latest_salesforce_account_name" else child_column
    
    actuals_filter = build_actuals_filter(category, use_case, feature, customer)
    plan_filter = build_plan_filter(category, use_case, feature, customer)
    rd_filter = _run_date_filter(run_date)
    
    query = f"""
    WITH current_q AS (
        SELECT 
            {child_column} AS entity, 
            SUM(revenue + product_led_revenue) AS cq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    prior_q AS (
        SELECT 
            {child_column} AS entity, 
            SUM(revenue + product_led_revenue) AS pq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.pq_start}' AND '{dates.pq_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    plan_q AS (
        SELECT 
            {plan_child_column} AS entity, 
            SUM(revenue) AS plan_revenue
        FROM {PLAN_TABLE}
        WHERE ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {plan_filter}
        GROUP BY 1
    ),
    prior_year AS (
        SELECT 
            {child_column} AS entity, 
            SUM(revenue + product_led_revenue) AS py_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.py_start}' AND '{dates.py_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    combined AS (
        SELECT 
            COALESCE(c.entity, p.entity, pl.entity, py.entity) AS entity,
            COALESCE(c.cq_revenue, 0) AS cq_revenue,
            COALESCE(p.pq_revenue, 0) AS pq_revenue,
            COALESCE(pl.plan_revenue, 0) AS plan_revenue,
            COALESCE(py.py_revenue, 0) AS py_revenue
        FROM current_q c
        FULL OUTER JOIN prior_q p ON c.entity = p.entity
        FULL OUTER JOIN plan_q pl ON COALESCE(c.entity, p.entity) = pl.entity
        FULL OUTER JOIN prior_year py ON COALESCE(c.entity, p.entity, pl.entity) = py.entity
    ),
    totals AS (
        SELECT 
            SUM(cq_revenue) AS total_revenue,
            NULLIF(SUM(ABS(cq_revenue - plan_revenue)), 0) AS total_variance_magnitude,
            NULLIF(SUM(ABS(cq_revenue - pq_revenue)), 0) AS total_qoq_delta_magnitude,
            NULLIF(SUM(ABS(cq_revenue - py_revenue)), 0) AS total_yoy_delta_magnitude
        FROM combined
    )
    SELECT 
        c.entity,
        ROUND(c.cq_revenue, 0) AS qtd_revenue,
        ROUND(c.pq_revenue, 0) AS prior_q_revenue,
        ROUND(c.cq_revenue - c.pq_revenue, 0) AS qoq_delta,
        ROUND(100.0 * (c.cq_revenue - c.pq_revenue) / NULLIF(c.pq_revenue, 0), 2) AS qoq_growth_pct,
        ROUND(100.0 * ABS(c.cq_revenue - c.pq_revenue) / t.total_qoq_delta_magnitude, 2) AS contribution_to_growth_pct,
        ROUND(c.plan_revenue, 0) AS qtd_plan,
        ROUND(c.cq_revenue - c.plan_revenue, 0) AS delta_to_plan,
        ROUND(100.0 * (c.cq_revenue - c.plan_revenue) / NULLIF(c.plan_revenue, 0), 2) AS pct_vs_plan,
        ROUND(100.0 * ABS(c.cq_revenue - c.plan_revenue) / t.total_variance_magnitude, 2) AS variance_magnitude_pct,
        ROUND(c.py_revenue, 0) AS prior_year_revenue,
        ROUND(c.cq_revenue - c.py_revenue, 0) AS yoy_delta,
        ROUND(100.0 * (c.cq_revenue - c.py_revenue) / NULLIF(c.py_revenue, 0), 2) AS yoy_growth_pct,
        ROUND(100.0 * ABS(c.cq_revenue - c.py_revenue) / t.total_yoy_delta_magnitude, 2) AS yoy_contribution_to_growth_pct,
        ROUND(100.0 * c.cq_revenue / NULLIF(t.total_revenue, 0), 2) AS mix_pct
    FROM combined c
    CROSS JOIN totals t
    WHERE c.entity IS NOT NULL
    ORDER BY c.cq_revenue DESC
    """
    
    return execute_query(conn, query, f"Children breakdown for {level}")


# =============================================================================
# TOP 20 VS LONG TAIL (CUSTOMERS)
# =============================================================================

def get_top20_vs_longtail(
    conn,
    dates: FiscalDates,
    run_date: date,
    level: str,
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Analyze customer revenue concentration: Top 20 customers vs rest (Long Tail).
    Includes all standard columns: QoQ, Plan, YoY, Mix.
    """
    if customer is not None:
        return []
    
    actuals_filter = build_actuals_filter(category, use_case, feature)
    plan_filter = build_plan_filter(category, use_case, feature)
    rd_filter = _run_date_filter(run_date)
    
    query = f"""
    WITH current_q AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS cq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {actuals_filter}
            AND agreement_type = 'Capacity'
        GROUP BY 1
    ),
    prior_q AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS pq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.pq_start}' AND '{dates.pq_end}'
            AND {actuals_filter}
            AND agreement_type = 'Capacity'
        GROUP BY 1
    ),
    prior_year AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS py_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.py_start}' AND '{dates.py_end}'
            AND {actuals_filter}
            AND agreement_type = 'Capacity'
        GROUP BY 1
    ),
    plan_q AS (
        SELECT 
            salesforce_account_name AS customer,
            SUM(revenue) AS plan_revenue
        FROM {PLAN_TABLE}
        WHERE ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {plan_filter}
        GROUP BY 1
    ),
    combined AS (
        SELECT 
            c.customer,
            c.cq_revenue,
            COALESCE(p.pq_revenue, 0) AS pq_revenue,
            COALESCE(py.py_revenue, 0) AS py_revenue,
            COALESCE(pl.plan_revenue, 0) AS plan_revenue
        FROM current_q c
        LEFT JOIN prior_q p ON c.customer = p.customer
        LEFT JOIN prior_year py ON c.customer = py.customer
        LEFT JOIN plan_q pl ON c.customer = pl.customer
        WHERE c.customer IS NOT NULL
    ),
    ranked AS (
        SELECT 
            customer, cq_revenue, pq_revenue, py_revenue, plan_revenue,
            ROW_NUMBER() OVER (ORDER BY cq_revenue DESC) AS rnk,
            SUM(cq_revenue) OVER () AS total_revenue
        FROM combined
    ),
    totals AS (
        SELECT 
            NULLIF(SUM(ABS(cq_revenue - pq_revenue)), 0) AS total_qoq_magnitude,
            NULLIF(SUM(ABS(cq_revenue - plan_revenue)), 0) AS total_plan_magnitude,
            NULLIF(SUM(ABS(cq_revenue - py_revenue)), 0) AS total_yoy_magnitude
        FROM combined
    ),
    aggregated AS (
        SELECT 
            CASE WHEN rnk <= 20 THEN 'Top 20 Customers' ELSE 'Long Tail' END AS segment,
            COUNT(*) AS customer_count,
            SUM(cq_revenue) AS cq_revenue,
            SUM(pq_revenue) AS pq_revenue,
            SUM(py_revenue) AS py_revenue,
            SUM(plan_revenue) AS plan_revenue,
            MAX(total_revenue) AS total_revenue,
            SUM(ABS(cq_revenue - pq_revenue)) AS qoq_magnitude,
            SUM(ABS(cq_revenue - plan_revenue)) AS plan_magnitude,
            SUM(ABS(cq_revenue - py_revenue)) AS yoy_magnitude
        FROM ranked
        GROUP BY 1
    )
    SELECT 
        a.segment,
        a.customer_count,
        ROUND(a.cq_revenue, 0) AS qtd_revenue,
        ROUND(a.pq_revenue, 0) AS prior_q_revenue,
        ROUND(a.cq_revenue - a.pq_revenue, 0) AS qoq_delta,
        ROUND(100.0 * (a.cq_revenue - a.pq_revenue) / NULLIF(a.pq_revenue, 0), 2) AS qoq_growth_pct,
        ROUND(100.0 * a.qoq_magnitude / t.total_qoq_magnitude, 2) AS contribution_to_growth_pct,
        ROUND(a.plan_revenue, 0) AS qtd_plan,
        ROUND(a.cq_revenue - a.plan_revenue, 0) AS delta_to_plan,
        ROUND(100.0 * (a.cq_revenue - a.plan_revenue) / NULLIF(a.plan_revenue, 0), 2) AS pct_vs_plan,
        ROUND(100.0 * a.plan_magnitude / t.total_plan_magnitude, 2) AS variance_magnitude_pct,
        ROUND(a.py_revenue, 0) AS prior_year_revenue,
        ROUND(a.cq_revenue - a.py_revenue, 0) AS yoy_delta,
        ROUND(100.0 * (a.cq_revenue - a.py_revenue) / NULLIF(a.py_revenue, 0), 2) AS yoy_growth_pct,
        ROUND(100.0 * a.yoy_magnitude / t.total_yoy_magnitude, 2) AS yoy_contribution_to_growth_pct,
        ROUND(100.0 * a.cq_revenue / NULLIF(a.total_revenue, 0), 2) AS mix_pct
    FROM aggregated a
    CROSS JOIN totals t
    ORDER BY a.cq_revenue DESC
    """
    
    return execute_query(conn, query, f"Top 20 vs Long Tail customers for {level}")


# =============================================================================
# INDUSTRY PERFORMANCE
# =============================================================================

def get_industry_performance(
    conn,
    dates: FiscalDates,
    run_date: date,
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Break down performance by industry vertical.
    """
    actuals_filter = build_actuals_filter(category, use_case, feature, customer)
    plan_filter = build_plan_filter(category, use_case, feature, customer)
    rd_filter = _run_date_filter(run_date)
    
    query = f"""
    WITH current_q AS (
        SELECT 
            COALESCE(industry_rollup, 'Unknown') AS industry,
            SUM(revenue + product_led_revenue) AS cq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    prior_q AS (
        SELECT 
            COALESCE(industry_rollup, 'Unknown') AS industry,
            SUM(revenue + product_led_revenue) AS pq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.pq_start}' AND '{dates.pq_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    prior_year AS (
        SELECT 
            COALESCE(industry_rollup, 'Unknown') AS industry,
            SUM(revenue + product_led_revenue) AS py_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.py_start}' AND '{dates.py_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    plan_q AS (
        SELECT 
            COALESCE(industry_rollup, 'Unknown') AS industry,
            SUM(revenue) AS plan_revenue
        FROM {PLAN_TABLE}
        WHERE ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {plan_filter}
        GROUP BY 1
    ),
    combined AS (
        SELECT 
            COALESCE(c.industry, pl.industry) AS industry,
            COALESCE(c.cq_revenue, 0) AS cq_revenue,
            COALESCE(p.pq_revenue, 0) AS pq_revenue,
            COALESCE(py.py_revenue, 0) AS py_revenue,
            COALESCE(pl.plan_revenue, 0) AS plan_revenue
        FROM current_q c
        LEFT JOIN prior_q p ON c.industry = p.industry
        LEFT JOIN prior_year py ON c.industry = py.industry
        FULL OUTER JOIN plan_q pl ON c.industry = pl.industry
    ),
    totals AS (
        SELECT 
            SUM(cq_revenue) AS total_revenue,
            NULLIF(SUM(ABS(cq_revenue - pq_revenue)), 0) AS total_qoq_delta_magnitude,
            NULLIF(SUM(ABS(cq_revenue - py_revenue)), 0) AS total_yoy_delta_magnitude,
            NULLIF(SUM(ABS(cq_revenue - plan_revenue)), 0) AS total_variance_magnitude
        FROM combined
    )
    SELECT 
        c.industry,
        ROUND(c.cq_revenue, 0) AS qtd_revenue,
        ROUND(c.pq_revenue, 0) AS prior_q_revenue,
        ROUND(c.cq_revenue - c.pq_revenue, 0) AS qoq_delta,
        ROUND(100.0 * (c.cq_revenue - c.pq_revenue) / NULLIF(c.pq_revenue, 0), 2) AS qoq_growth_pct,
        ROUND(100.0 * ABS(c.cq_revenue - c.pq_revenue) / t.total_qoq_delta_magnitude, 2) AS contribution_to_growth_pct,
        ROUND(c.plan_revenue, 0) AS qtd_plan,
        ROUND(c.cq_revenue - c.plan_revenue, 0) AS delta_to_plan,
        ROUND(100.0 * (c.cq_revenue - c.plan_revenue) / NULLIF(c.plan_revenue, 0), 2) AS pct_vs_plan,
        ROUND(100.0 * ABS(c.cq_revenue - c.plan_revenue) / t.total_variance_magnitude, 2) AS variance_magnitude_pct,
        ROUND(c.py_revenue, 0) AS prior_year_revenue,
        ROUND(c.cq_revenue - c.py_revenue, 0) AS yoy_delta,
        ROUND(100.0 * (c.cq_revenue - c.py_revenue) / NULLIF(c.py_revenue, 0), 2) AS yoy_growth_pct,
        ROUND(100.0 * ABS(c.cq_revenue - c.py_revenue) / t.total_yoy_delta_magnitude, 2) AS yoy_contribution_to_growth_pct,
        ROUND(100.0 * c.cq_revenue / NULLIF(t.total_revenue, 0), 2) AS mix_pct
    FROM combined c
    CROSS JOIN totals t
    WHERE c.industry IS NOT NULL
    ORDER BY c.cq_revenue DESC
    LIMIT {MAX_INDUSTRIES}
    """
    
    return execute_query(conn, query, "Industry performance")


# =============================================================================
# NEW VS EXISTING CUSTOMERS
# =============================================================================

def get_new_vs_existing(
    conn,
    dates: FiscalDates,
    run_date: date,
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Segment customers by lifecycle status: NEW, EXISTING (Growing/Stagnant/Shrinking), CHURNED.
    Includes all standard columns: QoQ, Plan, YoY, Mix.
    """
    if customer is not None:
        return []
    
    actuals_filter = build_actuals_filter(category, use_case, feature)
    plan_filter = build_plan_filter(category, use_case, feature)
    rd_filter = _run_date_filter(run_date)
    
    query = f"""
    WITH current_q AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS cq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {actuals_filter}
            AND agreement_type = 'Capacity'
        GROUP BY 1
    ),
    prior_q AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS pq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.pq_start}' AND '{dates.pq_end}'
            AND {actuals_filter}
            AND agreement_type = 'Capacity'
        GROUP BY 1
    ),
    prior_year AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS py_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.py_start}' AND '{dates.py_end}'
            AND {actuals_filter}
            AND agreement_type = 'Capacity'
        GROUP BY 1
    ),
    plan_q AS (
        SELECT 
            salesforce_account_name AS customer,
            SUM(revenue) AS plan_revenue
        FROM {PLAN_TABLE}
        WHERE ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {plan_filter}
        GROUP BY 1
    ),
    combined AS (
        SELECT 
            COALESCE(c.customer, p.customer) AS customer,
            COALESCE(c.cq_revenue, 0) AS cq_revenue,
            COALESCE(p.pq_revenue, 0) AS pq_revenue,
            COALESCE(py.py_revenue, 0) AS py_revenue,
            COALESCE(pl.plan_revenue, 0) AS plan_revenue,
            CASE 
                WHEN p.pq_revenue IS NULL OR p.pq_revenue = 0 THEN 'NEW'
                WHEN c.cq_revenue IS NULL OR c.cq_revenue = 0 THEN 'CHURNED'
                ELSE 'EXISTING'
            END AS customer_type,
            CASE 
                WHEN p.pq_revenue IS NULL OR p.pq_revenue = 0 THEN NULL
                WHEN c.cq_revenue IS NULL OR c.cq_revenue = 0 THEN NULL
                WHEN (COALESCE(c.cq_revenue, 0) - COALESCE(p.pq_revenue, 0)) / NULLIF(p.pq_revenue, 0) > {GROWTH_THRESHOLD} THEN 'GROWING'
                WHEN (COALESCE(c.cq_revenue, 0) - COALESCE(p.pq_revenue, 0)) / NULLIF(p.pq_revenue, 0) < {SHRINK_THRESHOLD} THEN 'SHRINKING'
                ELSE 'STAGNANT'
            END AS existing_segment
        FROM current_q c
        FULL OUTER JOIN prior_q p ON c.customer = p.customer
        LEFT JOIN prior_year py ON COALESCE(c.customer, p.customer) = py.customer
        LEFT JOIN plan_q pl ON COALESCE(c.customer, p.customer) = pl.customer
    ),
    totals AS (
        SELECT 
            NULLIF(SUM(ABS(cq_revenue - pq_revenue)), 0) AS total_qoq_magnitude,
            NULLIF(SUM(ABS(cq_revenue - plan_revenue)), 0) AS total_plan_magnitude,
            NULLIF(SUM(ABS(cq_revenue - py_revenue)), 0) AS total_yoy_magnitude,
            SUM(cq_revenue) AS total_revenue
        FROM combined
    ),
    aggregated AS (
        SELECT 
            customer_type,
            existing_segment,
            COUNT(DISTINCT customer) AS customer_count,
            SUM(cq_revenue) AS cq_revenue,
            SUM(pq_revenue) AS pq_revenue,
            SUM(py_revenue) AS py_revenue,
            SUM(plan_revenue) AS plan_revenue,
            SUM(ABS(cq_revenue - pq_revenue)) AS qoq_magnitude,
            SUM(ABS(cq_revenue - plan_revenue)) AS plan_magnitude,
            SUM(ABS(cq_revenue - py_revenue)) AS yoy_magnitude
        FROM combined
        GROUP BY 1, 2
    )
    SELECT 
        a.customer_type,
        a.existing_segment,
        a.customer_count,
        ROUND(a.cq_revenue, 0) AS qtd_revenue,
        ROUND(a.pq_revenue, 0) AS prior_q_revenue,
        ROUND(a.cq_revenue - a.pq_revenue, 0) AS qoq_delta,
        ROUND(100.0 * (a.cq_revenue - a.pq_revenue) / NULLIF(a.pq_revenue, 0), 2) AS qoq_growth_pct,
        ROUND(100.0 * a.qoq_magnitude / t.total_qoq_magnitude, 2) AS contribution_to_growth_pct,
        ROUND(a.plan_revenue, 0) AS qtd_plan,
        ROUND(a.cq_revenue - a.plan_revenue, 0) AS delta_to_plan,
        ROUND(100.0 * (a.cq_revenue - a.plan_revenue) / NULLIF(a.plan_revenue, 0), 2) AS pct_vs_plan,
        ROUND(100.0 * a.plan_magnitude / t.total_plan_magnitude, 2) AS variance_magnitude_pct,
        ROUND(a.py_revenue, 0) AS prior_year_revenue,
        ROUND(a.cq_revenue - a.py_revenue, 0) AS yoy_delta,
        ROUND(100.0 * (a.cq_revenue - a.py_revenue) / NULLIF(a.py_revenue, 0), 2) AS yoy_growth_pct,
        ROUND(100.0 * a.yoy_magnitude / t.total_yoy_magnitude, 2) AS yoy_contribution_to_growth_pct,
        ROUND(100.0 * a.cq_revenue / NULLIF(t.total_revenue, 0), 2) AS mix_pct
    FROM aggregated a
    CROSS JOIN totals t
    ORDER BY a.customer_type, a.existing_segment
    """
    
    return execute_query(conn, query, "New vs Existing")


# =============================================================================
# TOP GAINERS (CHILD ENTITIES)
# =============================================================================

def get_top_gainers(
    conn,
    dates: FiscalDates,
    run_date: date,
    level: str,
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get top entities with largest positive QoQ revenue change.
    """
    hierarchy_level = HIERARCHY.get(level)
    if not hierarchy_level or not hierarchy_level.child_level:
        return []
    
    child_column = HIERARCHY[hierarchy_level.child_level].column
    actuals_filter = build_actuals_filter(category, use_case, feature, customer)
    rd_filter = _run_date_filter(run_date)
    
    query = f"""
    WITH current_q AS (
        SELECT {child_column} AS entity, SUM(revenue + product_led_revenue) AS cq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    prior_q AS (
        SELECT {child_column} AS entity, SUM(revenue + product_led_revenue) AS pq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.pq_start}' AND '{dates.pq_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    combined AS (
        SELECT 
            COALESCE(c.entity, p.entity) AS entity,
            COALESCE(c.cq_revenue, 0) AS cq_revenue,
            COALESCE(p.pq_revenue, 0) AS pq_revenue,
            COALESCE(c.cq_revenue, 0) - COALESCE(p.pq_revenue, 0) AS delta
        FROM current_q c
        FULL OUTER JOIN prior_q p ON c.entity = p.entity
    ),
    totals AS (
        SELECT NULLIF(SUM(ABS(delta)), 0) AS total_magnitude FROM combined
    )
    SELECT 
        c.entity,
        ROUND(c.cq_revenue, 0) AS current_quarter_revenue,
        ROUND(c.pq_revenue, 0) AS prior_quarter_revenue,
        ROUND(c.delta, 0) AS delta,
        ROUND(100.0 * c.delta / NULLIF(c.pq_revenue, 0), 2) AS qoq_growth_pct,
        ROUND(100.0 * ABS(c.delta) / t.total_magnitude, 2) AS contribution_pct
    FROM combined c
    CROSS JOIN totals t
    WHERE c.delta > 0
    ORDER BY c.delta DESC
    LIMIT {MAX_GAINERS}
    """
    
    return execute_query(conn, query, f"Top gainers for {level}")


# =============================================================================
# TOP CONTRACTORS (CHILD ENTITIES)
# =============================================================================

def get_top_contractors(
    conn,
    dates: FiscalDates,
    run_date: date,
    level: str,
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get top entities with largest negative QoQ revenue change.
    """
    hierarchy_level = HIERARCHY.get(level)
    if not hierarchy_level or not hierarchy_level.child_level:
        return []
    
    child_column = HIERARCHY[hierarchy_level.child_level].column
    actuals_filter = build_actuals_filter(category, use_case, feature, customer)
    rd_filter = _run_date_filter(run_date)
    
    query = f"""
    WITH current_q AS (
        SELECT {child_column} AS entity, SUM(revenue + product_led_revenue) AS cq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    prior_q AS (
        SELECT {child_column} AS entity, SUM(revenue + product_led_revenue) AS pq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.pq_start}' AND '{dates.pq_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    combined AS (
        SELECT 
            COALESCE(c.entity, p.entity) AS entity,
            COALESCE(c.cq_revenue, 0) AS cq_revenue,
            COALESCE(p.pq_revenue, 0) AS pq_revenue,
            COALESCE(c.cq_revenue, 0) - COALESCE(p.pq_revenue, 0) AS delta
        FROM current_q c
        FULL OUTER JOIN prior_q p ON c.entity = p.entity
    ),
    totals AS (
        SELECT NULLIF(SUM(ABS(delta)), 0) AS total_magnitude FROM combined
    )
    SELECT 
        c.entity,
        ROUND(c.cq_revenue, 0) AS current_quarter_revenue,
        ROUND(c.pq_revenue, 0) AS prior_quarter_revenue,
        ROUND(c.delta, 0) AS delta,
        ROUND(100.0 * c.delta / NULLIF(c.pq_revenue, 0), 2) AS qoq_growth_pct,
        ROUND(100.0 * ABS(c.delta) / t.total_magnitude, 2) AS contribution_pct
    FROM combined c
    CROSS JOIN totals t
    WHERE c.delta < 0
    ORDER BY c.delta ASC
    LIMIT {MAX_CONTRACTORS}
    """
    
    return execute_query(conn, query, f"Top contractors for {level}")


# =============================================================================
# CONCENTRATION TREND
# =============================================================================

def get_concentration_trend(
    conn,
    dates: FiscalDates,
    run_date: date,
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Track Top 10/20 customer concentration over the quarter months.
    """
    if customer is not None:
        return []
    
    actuals_filter = build_actuals_filter(category, use_case, feature)
    rd_filter = _run_date_filter(run_date)
    
    query = f"""
    WITH monthly_by_customer AS (
        SELECT 
            DATE_TRUNC('month', ds) AS month,
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {actuals_filter}
        GROUP BY 1, 2
    ),
    ranked AS (
        SELECT 
            month, customer, revenue,
            ROW_NUMBER() OVER (PARTITION BY month ORDER BY revenue DESC) AS rnk,
            SUM(revenue) OVER (PARTITION BY month) AS total_revenue
        FROM monthly_by_customer
    )
    SELECT 
        month,
        ROUND(SUM(CASE WHEN rnk <= 10 THEN revenue ELSE 0 END), 0) AS top10_revenue,
        ROUND(SUM(CASE WHEN rnk <= 20 THEN revenue ELSE 0 END), 0) AS top20_revenue,
        ROUND(MAX(total_revenue), 0) AS total_revenue,
        ROUND(100.0 * SUM(CASE WHEN rnk <= 10 THEN revenue ELSE 0 END) / NULLIF(MAX(total_revenue), 0), 2) AS top10_pct,
        ROUND(100.0 * SUM(CASE WHEN rnk <= 20 THEN revenue ELSE 0 END) / NULLIF(MAX(total_revenue), 0), 2) AS top20_pct
    FROM ranked
    GROUP BY month
    ORDER BY month
    """
    
    return execute_query(conn, query, "Concentration trend")


# =============================================================================
# TOP CUSTOMERS (BY REVENUE)
# =============================================================================

def get_top_customers(
    conn,
    dates: FiscalDates,
    run_date: date,
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get top customers by QTD revenue with growth metrics.
    """
    if customer is not None:
        return []
    
    actuals_filter = build_actuals_filter(category, use_case, feature)
    plan_filter = build_plan_filter(category, use_case, feature)
    rd_filter = _run_date_filter(run_date)
    
    query = f"""
    WITH current_q AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS cq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    prior_q AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS pq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.pq_start}' AND '{dates.pq_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    prior_year AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS py_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.py_start}' AND '{dates.py_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    plan_q AS (
        SELECT 
            salesforce_account_name AS customer,
            SUM(revenue) AS plan_revenue
        FROM {PLAN_TABLE}
        WHERE ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {plan_filter}
        GROUP BY 1
    ),
    combined AS (
        SELECT 
            COALESCE(c.customer, p.customer, py.customer, pl.customer) AS customer,
            COALESCE(c.cq_revenue, 0) AS cq_revenue,
            COALESCE(p.pq_revenue, 0) AS pq_revenue,
            COALESCE(py.py_revenue, 0) AS py_revenue,
            COALESCE(pl.plan_revenue, 0) AS plan_revenue
        FROM current_q c
        FULL OUTER JOIN prior_q p ON c.customer = p.customer
        FULL OUTER JOIN prior_year py ON COALESCE(c.customer, p.customer) = py.customer
        FULL OUTER JOIN plan_q pl ON COALESCE(c.customer, p.customer, py.customer) = pl.customer
    ),
    totals AS (
        SELECT 
            SUM(cq_revenue) AS total_revenue,
            NULLIF(SUM(ABS(cq_revenue - pq_revenue)), 0) AS total_qoq_delta_magnitude,
            NULLIF(SUM(ABS(cq_revenue - py_revenue)), 0) AS total_yoy_delta_magnitude,
            NULLIF(SUM(ABS(cq_revenue - plan_revenue)), 0) AS total_variance_magnitude
        FROM combined
    )
    SELECT 
        c.customer,
        ROUND(c.cq_revenue, 0) AS qtd_revenue,
        ROUND(c.pq_revenue, 0) AS prior_q_revenue,
        ROUND(c.cq_revenue - c.pq_revenue, 0) AS qoq_delta,
        ROUND(100.0 * (c.cq_revenue - c.pq_revenue) / NULLIF(c.pq_revenue, 0), 2) AS qoq_growth_pct,
        ROUND(100.0 * ABS(c.cq_revenue - c.pq_revenue) / t.total_qoq_delta_magnitude, 2) AS contribution_to_growth_pct,
        ROUND(c.plan_revenue, 0) AS qtd_plan,
        ROUND(c.cq_revenue - c.plan_revenue, 0) AS vs_plan,
        ROUND(100.0 * (c.cq_revenue - c.plan_revenue) / NULLIF(c.plan_revenue, 0), 2) AS vs_plan_pct,
        ROUND(100.0 * ABS(c.cq_revenue - c.plan_revenue) / t.total_variance_magnitude, 2) AS variance_magnitude_pct,
        ROUND(c.py_revenue, 0) AS prior_year_revenue,
        ROUND(c.cq_revenue - c.py_revenue, 0) AS yoy_delta,
        ROUND(100.0 * (c.cq_revenue - c.py_revenue) / NULLIF(c.py_revenue, 0), 2) AS yoy_growth_pct,
        ROUND(100.0 * ABS(c.cq_revenue - c.py_revenue) / t.total_yoy_delta_magnitude, 2) AS yoy_contribution_to_growth_pct,
        ROUND(100.0 * c.cq_revenue / NULLIF(t.total_revenue, 0), 2) AS mix_pct
    FROM combined c
    CROSS JOIN totals t
    WHERE c.customer IS NOT NULL
    ORDER BY c.cq_revenue DESC
    LIMIT {MAX_TOP_CUSTOMERS}
    """
    
    return execute_query(conn, query, "Top customers")


# =============================================================================
# TOP CUSTOMER GAINERS
# =============================================================================

def get_top_customer_gainers(
    conn,
    dates: FiscalDates,
    run_date: date,
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get customers with largest positive QoQ revenue change.
    Includes all standard columns: QoQ, Plan, YoY, Mix.
    """
    if customer is not None:
        return []
    
    actuals_filter = build_actuals_filter(category, use_case, feature)
    plan_filter = build_plan_filter(category, use_case, feature)
    rd_filter = _run_date_filter(run_date)
    
    query = f"""
    WITH current_q AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS cq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    prior_q AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS pq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.pq_start}' AND '{dates.pq_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    prior_year AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS py_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.py_start}' AND '{dates.py_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    plan_q AS (
        SELECT 
            salesforce_account_name AS customer,
            SUM(revenue) AS plan_revenue
        FROM {PLAN_TABLE}
        WHERE ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {plan_filter}
        GROUP BY 1
    ),
    combined AS (
        SELECT 
            COALESCE(c.customer, p.customer, py.customer, pl.customer) AS customer,
            COALESCE(c.cq_revenue, 0) AS cq_revenue,
            COALESCE(p.pq_revenue, 0) AS pq_revenue,
            COALESCE(py.py_revenue, 0) AS py_revenue,
            COALESCE(pl.plan_revenue, 0) AS plan_revenue,
            COALESCE(c.cq_revenue, 0) - COALESCE(p.pq_revenue, 0) AS delta
        FROM current_q c
        FULL OUTER JOIN prior_q p ON c.customer = p.customer
        FULL OUTER JOIN prior_year py ON COALESCE(c.customer, p.customer) = py.customer
        FULL OUTER JOIN plan_q pl ON COALESCE(c.customer, p.customer, py.customer) = pl.customer
    ),
    totals AS (
        SELECT 
            NULLIF(SUM(CASE WHEN delta > 0 THEN delta ELSE 0 END), 0) AS total_gains,
            NULLIF(SUM(ABS(cq_revenue - plan_revenue)), 0) AS total_plan_magnitude,
            NULLIF(SUM(ABS(cq_revenue - py_revenue)), 0) AS total_yoy_magnitude,
            SUM(cq_revenue) AS total_revenue
        FROM combined
    )
    SELECT 
        c.customer,
        ROUND(c.cq_revenue, 0) AS qtd_revenue,
        ROUND(c.pq_revenue, 0) AS prior_q_revenue,
        ROUND(c.delta, 0) AS qoq_delta,
        ROUND(100.0 * c.delta / NULLIF(c.pq_revenue, 0), 2) AS qoq_growth_pct,
        ROUND(100.0 * c.delta / t.total_gains, 2) AS contribution_to_growth_pct,
        ROUND(c.plan_revenue, 0) AS qtd_plan,
        ROUND(c.cq_revenue - c.plan_revenue, 0) AS delta_to_plan,
        ROUND(100.0 * (c.cq_revenue - c.plan_revenue) / NULLIF(c.plan_revenue, 0), 2) AS pct_vs_plan,
        ROUND(100.0 * ABS(c.cq_revenue - c.plan_revenue) / t.total_plan_magnitude, 2) AS variance_magnitude_pct,
        ROUND(c.py_revenue, 0) AS prior_year_revenue,
        ROUND(c.cq_revenue - c.py_revenue, 0) AS yoy_delta,
        ROUND(100.0 * (c.cq_revenue - c.py_revenue) / NULLIF(c.py_revenue, 0), 2) AS yoy_growth_pct,
        ROUND(100.0 * ABS(c.cq_revenue - c.py_revenue) / t.total_yoy_magnitude, 2) AS yoy_contribution_to_growth_pct,
        ROUND(100.0 * c.cq_revenue / NULLIF(t.total_revenue, 0), 2) AS mix_pct
    FROM combined c
    CROSS JOIN totals t
    WHERE c.delta > 0 AND c.customer IS NOT NULL
    ORDER BY c.delta DESC
    LIMIT {MAX_GAINERS}
    """
    
    return execute_query(conn, query, "Top customer gainers")


# =============================================================================
# TOP CUSTOMER CONTRACTORS
# =============================================================================

def get_top_customer_contractors(
    conn,
    dates: FiscalDates,
    run_date: date,
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get customers with largest negative QoQ revenue change.
    Includes all standard columns: QoQ, Plan, YoY, Mix.
    """
    if customer is not None:
        return []
    
    actuals_filter = build_actuals_filter(category, use_case, feature)
    plan_filter = build_plan_filter(category, use_case, feature)
    rd_filter = _run_date_filter(run_date)
    
    query = f"""
    WITH current_q AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS cq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    prior_q AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS pq_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.pq_start}' AND '{dates.pq_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    prior_year AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS py_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.py_start}' AND '{dates.py_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    plan_q AS (
        SELECT 
            salesforce_account_name AS customer,
            SUM(revenue) AS plan_revenue
        FROM {PLAN_TABLE}
        WHERE ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {plan_filter}
        GROUP BY 1
    ),
    combined AS (
        SELECT 
            COALESCE(c.customer, p.customer, py.customer, pl.customer) AS customer,
            COALESCE(c.cq_revenue, 0) AS cq_revenue,
            COALESCE(p.pq_revenue, 0) AS pq_revenue,
            COALESCE(py.py_revenue, 0) AS py_revenue,
            COALESCE(pl.plan_revenue, 0) AS plan_revenue,
            COALESCE(c.cq_revenue, 0) - COALESCE(p.pq_revenue, 0) AS delta
        FROM current_q c
        FULL OUTER JOIN prior_q p ON c.customer = p.customer
        FULL OUTER JOIN prior_year py ON COALESCE(c.customer, p.customer) = py.customer
        FULL OUTER JOIN plan_q pl ON COALESCE(c.customer, p.customer, py.customer) = pl.customer
    ),
    totals AS (
        SELECT 
            NULLIF(SUM(CASE WHEN delta < 0 THEN ABS(delta) ELSE 0 END), 0) AS total_losses,
            NULLIF(SUM(ABS(cq_revenue - plan_revenue)), 0) AS total_plan_magnitude,
            NULLIF(SUM(ABS(cq_revenue - py_revenue)), 0) AS total_yoy_magnitude,
            SUM(cq_revenue) AS total_revenue
        FROM combined
    )
    SELECT 
        c.customer,
        ROUND(c.cq_revenue, 0) AS qtd_revenue,
        ROUND(c.pq_revenue, 0) AS prior_q_revenue,
        ROUND(c.delta, 0) AS qoq_delta,
        ROUND(100.0 * c.delta / NULLIF(c.pq_revenue, 0), 2) AS qoq_growth_pct,
        ROUND(100.0 * ABS(c.delta) / t.total_losses, 2) AS contribution_to_decline_pct,
        ROUND(c.plan_revenue, 0) AS qtd_plan,
        ROUND(c.cq_revenue - c.plan_revenue, 0) AS delta_to_plan,
        ROUND(100.0 * (c.cq_revenue - c.plan_revenue) / NULLIF(c.plan_revenue, 0), 2) AS pct_vs_plan,
        ROUND(100.0 * ABS(c.cq_revenue - c.plan_revenue) / t.total_plan_magnitude, 2) AS variance_magnitude_pct,
        ROUND(c.py_revenue, 0) AS prior_year_revenue,
        ROUND(c.cq_revenue - c.py_revenue, 0) AS yoy_delta,
        ROUND(100.0 * (c.cq_revenue - c.py_revenue) / NULLIF(c.py_revenue, 0), 2) AS yoy_growth_pct,
        ROUND(100.0 * ABS(c.cq_revenue - c.py_revenue) / t.total_yoy_magnitude, 2) AS yoy_contribution_to_growth_pct,
        ROUND(100.0 * c.cq_revenue / NULLIF(t.total_revenue, 0), 2) AS mix_pct
    FROM combined c
    CROSS JOIN totals t
    WHERE c.delta < 0 AND c.customer IS NOT NULL
    ORDER BY c.delta ASC
    LIMIT {MAX_CONTRACTORS}
    """
    
    return execute_query(conn, query, "Top customer contractors")


# =============================================================================
# PLAN VARIANCE BY CHILD ENTITY (TOP 20 VS LONG TAIL)
# =============================================================================

def get_plan_variance_by_segment(
    conn,
    dates: FiscalDates,
    run_date: date,
    level: str,
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get plan variance for each child entity, split by Top 20 vs Long Tail customers.
    Shows how much each use case/feature beat or missed plan, broken down by customer segment.
    """
    if customer is not None:
        return []
    
    hierarchy_level = HIERARCHY.get(level)
    if not hierarchy_level or not hierarchy_level.child_level:
        return []
    
    child_config = HIERARCHY[hierarchy_level.child_level]
    child_column = child_config.column
    plan_child_column = "salesforce_account_name" if child_column == "latest_salesforce_account_name" else child_column
    
    actuals_filter = build_actuals_filter(category, use_case, feature)
    plan_filter = build_plan_filter(category, use_case, feature)
    rd_filter = _run_date_filter(run_date)
    
    query = f"""
    WITH customer_totals AS (
        SELECT 
            latest_salesforce_account_name AS customer,
            SUM(revenue + product_led_revenue) AS total_revenue
        FROM {ACTUALS_TABLE}
        WHERE {rd_filter}
            AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {actuals_filter}
        GROUP BY 1
    ),
    customer_ranks AS (
        SELECT 
            customer,
            ROW_NUMBER() OVER (ORDER BY total_revenue DESC) AS rnk
        FROM customer_totals
    ),
    actuals_with_segment AS (
        SELECT 
            a.{child_column} AS entity,
            a.latest_salesforce_account_name AS customer,
            CASE WHEN cr.rnk <= 20 THEN 'Top 20' ELSE 'Long Tail' END AS segment,
            SUM(a.revenue + a.product_led_revenue) AS revenue
        FROM {ACTUALS_TABLE} a
        LEFT JOIN customer_ranks cr ON a.latest_salesforce_account_name = cr.customer
        WHERE {rd_filter}
            AND a.ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {actuals_filter}
        GROUP BY 1, 2, 3
    ),
    plan_with_segment AS (
        SELECT 
            p.{plan_child_column} AS entity,
            p.salesforce_account_name AS customer,
            CASE WHEN cr.rnk <= 20 THEN 'Top 20' ELSE 'Long Tail' END AS segment,
            SUM(p.revenue) AS plan_revenue
        FROM {PLAN_TABLE} p
        LEFT JOIN customer_ranks cr ON p.salesforce_account_name = cr.customer
        WHERE p.ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
            AND {plan_filter}
        GROUP BY 1, 2, 3
    ),
    combined AS (
        SELECT 
            COALESCE(a.entity, p.entity) AS entity,
            COALESCE(a.segment, p.segment) AS segment,
            COALESCE(SUM(a.revenue), 0) AS actual_revenue,
            COALESCE(SUM(p.plan_revenue), 0) AS plan_revenue
        FROM actuals_with_segment a
        FULL OUTER JOIN plan_with_segment p 
            ON a.entity = p.entity AND a.customer = p.customer AND a.segment = p.segment
        WHERE COALESCE(a.entity, p.entity) IS NOT NULL
        GROUP BY 1, 2
    )
    SELECT 
        entity,
        segment,
        ROUND(actual_revenue, 0) AS actual_revenue,
        ROUND(plan_revenue, 0) AS plan_revenue,
        ROUND(actual_revenue - plan_revenue, 0) AS variance
    FROM combined
    WHERE entity IS NOT NULL AND segment IS NOT NULL
    ORDER BY entity, segment
    """
    
    return execute_query(conn, query, f"Plan variance by segment for {level}")
