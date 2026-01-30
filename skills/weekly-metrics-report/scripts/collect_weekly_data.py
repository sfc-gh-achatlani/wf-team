#!/usr/bin/env python3
"""
collect_weekly_data.py - Collect all data for weekly metrics HTML report.

DATA SOURCES:
- Actuals: finance.customer.fy26_product_category_revenue (revenue + product_led_revenue)
- Forecast: finance.customer.product_category_rev_actuals_w_forecast_sfdc
- Plan (feature-level): finance.customer.temp_product_category_revenue_plan
- Plan (account-level): finance.customer.product_category_most_recent_plan
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import snowflake.connector


def get_connection():
    return snowflake.connector.connect(
        connection_name=os.getenv("SNOWFLAKE_CONNECTION_NAME") or "snowhouse"
    )


def get_fiscal_dates(conn):
    query = """
    SELECT fiscal_quarter_start, fiscal_quarter_end
    FROM finance.stg_utils.stg_fiscal_calendar
    WHERE _date = CURRENT_DATE() LIMIT 1
    """
    cursor = conn.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    cursor.close()
    return (row[0], row[1]) if row else (None, None)


def calculate_week_dates(reference_date=None):
    if reference_date is None:
        reference_date = datetime.now().date()
    days_since_sunday = (reference_date.weekday() + 1) % 7
    current_week_end = reference_date - timedelta(days=days_since_sunday + 1)
    current_week_start = current_week_end - timedelta(days=6)
    prior_week_end = current_week_start - timedelta(days=1)
    prior_week_start = prior_week_end - timedelta(days=6)
    return {
        'current_week_start': current_week_start,
        'current_week_end': current_week_end,
        'prior_week_start': prior_week_start,
        'prior_week_end': prior_week_end,
    }


def execute_query(conn, query, desc=""):
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [d[0].lower() for d in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    return [dict(zip(columns, row)) for row in rows]


def get_category_wow(conn, current_start, current_end, prior_start, prior_end):
    """Category WoW using actuals table with revenue + product_led_revenue."""
    query = f"""
    WITH current_week AS (
        SELECT product_category, SUM(revenue + product_led_revenue) AS current_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        GROUP BY 1
    ),
    prior_week AS (
        SELECT product_category, SUM(revenue + product_led_revenue) AS prior_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{prior_start}' AND '{prior_end}'
        GROUP BY 1
    ),
    totals AS (
        SELECT SUM(c.current_rev) AS total_current, 
               SUM(ABS(COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0))) AS total_magnitude
        FROM current_week c FULL OUTER JOIN prior_week p ON c.product_category = p.product_category
    )
    SELECT COALESCE(c.product_category, p.product_category) AS product_category,
        ROUND(COALESCE(c.current_rev, 0), 0) AS current_rev,
        ROUND(COALESCE(p.prior_rev, 0), 0) AS prior_rev,
        ROUND(100.0 * (COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0)) / NULLIF(p.prior_rev, 0), 1) AS pct_change,
        ROUND(COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0), 0) AS dollar_change,
        ROUND(100.0 * COALESCE(c.current_rev, 0) / NULLIF(t.total_current, 0), 1) AS mix_pct,
        ROUND(100.0 * ABS(COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0)) / NULLIF(t.total_magnitude, 0), 1) AS contribution_pct
    FROM current_week c FULL OUTER JOIN prior_week p ON c.product_category = p.product_category
    CROSS JOIN totals t
    ORDER BY ABS(COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0)) DESC
    """
    return execute_query(conn, query)


def get_qtd_vs_plan(conn, week_end):
    """QTD actuals vs plan at category level using feature-level plan table."""
    query = f"""
    WITH fiscal_context AS (
        SELECT fiscal_quarter_start FROM finance.stg_utils.stg_fiscal_calendar
        WHERE _date = '{week_end}' LIMIT 1
    ),
    qtd_actuals AS (
        SELECT product_category, SUM(revenue + product_led_revenue) AS qtd_actual
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds >= (SELECT fiscal_quarter_start FROM fiscal_context) AND ds <= '{week_end}'
        GROUP BY 1
    ),
    qtd_plan AS (
        SELECT product_category, SUM(revenue) AS qtd_plan
        FROM finance.customer.temp_product_category_revenue_plan
        WHERE general_date >= (SELECT fiscal_quarter_start FROM fiscal_context) 
          AND general_date <= '{week_end}'
        GROUP BY 1
    )
    SELECT a.product_category, ROUND(a.qtd_actual, 0) AS qtd_actual, ROUND(p.qtd_plan, 0) AS qtd_plan,
           ROUND(a.qtd_actual - p.qtd_plan, 0) AS delta_to_plan,
           ROUND(100.0 * (a.qtd_actual - p.qtd_plan) / NULLIF(p.qtd_plan, 0), 2) AS pct_variance
    FROM qtd_actuals a JOIN qtd_plan p ON a.product_category = p.product_category
    ORDER BY ABS(a.qtd_actual - p.qtd_plan) DESC
    """
    return execute_query(conn, query)


def get_qtd_plan_by_use_case(conn, week_end):
    """QTD plan at use case level using feature-level plan table."""
    query = f"""
    WITH fiscal_context AS (
        SELECT fiscal_quarter_start FROM finance.stg_utils.stg_fiscal_calendar
        WHERE _date = '{week_end}' LIMIT 1
    ),
    qtd_actuals AS (
        SELECT product_category, use_case, SUM(revenue + product_led_revenue) AS qtd_actual
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds >= (SELECT fiscal_quarter_start FROM fiscal_context) AND ds <= '{week_end}'
        GROUP BY 1, 2
    ),
    qtd_plan AS (
        SELECT product_category, use_case, SUM(revenue) AS qtd_plan
        FROM finance.customer.temp_product_category_revenue_plan
        WHERE general_date >= (SELECT fiscal_quarter_start FROM fiscal_context) 
          AND general_date <= '{week_end}'
        GROUP BY 1, 2
    )
    SELECT COALESCE(a.product_category, p.product_category) as product_category,
           COALESCE(a.use_case, p.use_case) as use_case,
           ROUND(COALESCE(a.qtd_actual, 0) - COALESCE(p.qtd_plan, 0), 0) AS delta_to_plan,
           ROUND(100.0 * (COALESCE(a.qtd_actual, 0) - COALESCE(p.qtd_plan, 0)) / NULLIF(p.qtd_plan, 0), 2) AS pct_variance
    FROM qtd_actuals a FULL OUTER JOIN qtd_plan p 
        ON a.product_category = p.product_category AND a.use_case = p.use_case
    """
    results = execute_query(conn, query)
    lookup = {}
    for r in results:
        key = (r['product_category'], r['use_case'])
        lookup[key] = {'delta': r['delta_to_plan'], 'pct': r['pct_variance']}
    return lookup


def get_qtd_plan_by_feature(conn, week_end):
    """QTD plan at feature level using feature-level plan table."""
    query = f"""
    WITH fiscal_context AS (
        SELECT fiscal_quarter_start FROM finance.stg_utils.stg_fiscal_calendar
        WHERE _date = '{week_end}' LIMIT 1
    ),
    qtd_actuals AS (
        SELECT product_category, use_case, feature, SUM(revenue + product_led_revenue) AS qtd_actual
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds >= (SELECT fiscal_quarter_start FROM fiscal_context) AND ds <= '{week_end}'
        GROUP BY 1, 2, 3
    ),
    qtd_plan AS (
        SELECT product_category, use_case, feature, SUM(revenue) AS qtd_plan
        FROM finance.customer.temp_product_category_revenue_plan
        WHERE general_date >= (SELECT fiscal_quarter_start FROM fiscal_context) 
          AND general_date <= '{week_end}'
        GROUP BY 1, 2, 3
    )
    SELECT COALESCE(a.product_category, p.product_category) as product_category,
           COALESCE(a.use_case, p.use_case) as use_case,
           COALESCE(a.feature, p.feature) as feature,
           ROUND(COALESCE(a.qtd_actual, 0) - COALESCE(p.qtd_plan, 0), 0) AS delta_to_plan,
           ROUND(100.0 * (COALESCE(a.qtd_actual, 0) - COALESCE(p.qtd_plan, 0)) / NULLIF(p.qtd_plan, 0), 2) AS pct_variance
    FROM qtd_actuals a FULL OUTER JOIN qtd_plan p 
        ON a.product_category = p.product_category AND a.use_case = p.use_case AND a.feature = p.feature
    """
    results = execute_query(conn, query)
    lookup = {}
    for r in results:
        lookup[r['feature']] = {'delta': r['delta_to_plan'], 'pct': r['pct_variance']}
    return lookup


def get_use_cases(conn, current_start, current_end, prior_start, prior_end, uc_plan_lookup):
    """Use case WoW using actuals with revenue + product_led_revenue."""
    query = f"""
    WITH current_week AS (
        SELECT product_category, use_case, SUM(revenue + product_led_revenue) AS current_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        GROUP BY 1, 2
    ),
    prior_week AS (
        SELECT product_category, use_case, SUM(revenue + product_led_revenue) AS prior_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{prior_start}' AND '{prior_end}'
        GROUP BY 1, 2
    ),
    use_case_wow AS (
        SELECT COALESCE(c.product_category, p.product_category) AS product_category,
            COALESCE(c.use_case, p.use_case) AS use_case,
            COALESCE(c.current_rev, 0) AS current_rev,
            COALESCE(p.prior_rev, 0) AS prior_rev,
            COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS dollar_change
        FROM current_week c FULL OUTER JOIN prior_week p ON c.product_category = p.product_category AND c.use_case = p.use_case
    ),
    category_totals AS (
        SELECT product_category, SUM(current_rev) AS cat_total_current, SUM(ABS(dollar_change)) AS cat_total_abs_change
        FROM use_case_wow GROUP BY product_category
    )
    SELECT uw.product_category, uw.use_case, 
        ROUND(uw.current_rev, 0) AS current_rev, ROUND(uw.prior_rev, 0) AS prior_rev,
        ROUND(uw.dollar_change, 0) AS dollar_change,
        ROUND(100.0 * uw.dollar_change / NULLIF(uw.prior_rev, 0), 1) AS pct_change,
        ROUND(100.0 * uw.current_rev / NULLIF(ct.cat_total_current, 0), 2) AS mix_pct,
        ROUND(100.0 * ABS(uw.dollar_change) / NULLIF(ct.cat_total_abs_change, 0), 2) AS contribution_pct
    FROM use_case_wow uw JOIN category_totals ct ON uw.product_category = ct.product_category
    ORDER BY uw.product_category, ABS(uw.dollar_change) DESC
    """
    results = execute_query(conn, query)
    by_category = defaultdict(list)
    for row in results:
        key = (row['product_category'], row['use_case'])
        plan_data = uc_plan_lookup.get(key, {})
        row['delta_to_plan'] = plan_data.get('delta', 0)
        row['pct_to_plan'] = plan_data.get('pct', 0)
        by_category[row['product_category']].append(row)
    return dict(by_category)


def get_features(conn, current_start, current_end, prior_start, prior_end, feat_plan_lookup):
    """Feature WoW using actuals with revenue + product_led_revenue."""
    query = f"""
    WITH current_week AS (
        SELECT product_category, use_case, feature, SUM(revenue + product_led_revenue) AS current_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        GROUP BY 1, 2, 3
    ),
    prior_week AS (
        SELECT product_category, use_case, feature, SUM(revenue + product_led_revenue) AS prior_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{prior_start}' AND '{prior_end}'
        GROUP BY 1, 2, 3
    ),
    feature_wow AS (
        SELECT COALESCE(c.product_category, p.product_category) AS product_category,
            COALESCE(c.use_case, p.use_case) AS use_case,
            COALESCE(c.feature, p.feature) AS feature,
            COALESCE(c.current_rev, 0) AS current_rev,
            COALESCE(p.prior_rev, 0) AS prior_rev,
            COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS dollar_change
        FROM current_week c FULL OUTER JOIN prior_week p 
            ON c.product_category = p.product_category AND c.use_case = p.use_case AND c.feature = p.feature
    ),
    use_case_totals AS (
        SELECT product_category, use_case, SUM(current_rev) AS uc_total_current, SUM(ABS(dollar_change)) AS uc_total_abs_change
        FROM feature_wow GROUP BY product_category, use_case
    )
    SELECT fw.product_category, fw.use_case, fw.feature, 
        ROUND(fw.current_rev, 0) AS current_rev, ROUND(fw.prior_rev, 0) AS prior_rev,
        ROUND(fw.dollar_change, 0) AS dollar_change,
        ROUND(100.0 * fw.dollar_change / NULLIF(fw.prior_rev, 0), 1) AS pct_change,
        ROUND(100.0 * fw.current_rev / NULLIF(uct.uc_total_current, 0), 2) AS mix_pct,
        ROUND(100.0 * ABS(fw.dollar_change) / NULLIF(uct.uc_total_abs_change, 0), 2) AS contribution_pct
    FROM feature_wow fw JOIN use_case_totals uct ON fw.product_category = uct.product_category AND fw.use_case = uct.use_case
    ORDER BY fw.product_category, fw.use_case, ABS(fw.dollar_change) DESC
    """
    results = execute_query(conn, query)
    by_category = defaultdict(list)
    for row in results:
        plan_data = feat_plan_lookup.get(row['feature'], {})
        row['delta_to_plan'] = plan_data.get('delta', 0)
        row['pct_to_plan'] = plan_data.get('pct', 0)
        by_category[row['product_category']].append(row)
    return dict(by_category)


def get_qtd_plan_by_customer(conn, week_end):
    """QTD plan at customer level using account-level RFMA plan table."""
    query = f"""
    WITH fiscal_context AS (
        SELECT fiscal_quarter_start FROM finance.stg_utils.stg_fiscal_calendar
        WHERE _date = '{week_end}' LIMIT 1
    ),
    qtd_actuals AS (
        SELECT feature, latest_salesforce_account_name as customer, SUM(revenue + product_led_revenue) AS qtd_actual
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds >= (SELECT fiscal_quarter_start FROM fiscal_context) AND ds <= '{week_end}'
        GROUP BY 1, 2
    ),
    qtd_plan AS (
        SELECT feature, salesforce_account_name as customer, SUM(plan_revenue) AS qtd_plan
        FROM finance.customer.product_category_most_recent_plan
        WHERE ds >= (SELECT fiscal_quarter_start FROM fiscal_context) AND ds <= '{week_end}'
        GROUP BY 1, 2
    )
    SELECT COALESCE(a.feature, p.feature) as feature,
           COALESCE(a.customer, p.customer) as customer,
           ROUND(COALESCE(a.qtd_actual, 0) - COALESCE(p.qtd_plan, 0), 0) AS delta_to_plan,
           ROUND(100.0 * (COALESCE(a.qtd_actual, 0) - COALESCE(p.qtd_plan, 0)) / NULLIF(p.qtd_plan, 0), 2) AS pct_variance
    FROM qtd_actuals a FULL OUTER JOIN qtd_plan p 
        ON a.feature = p.feature AND a.customer = p.customer
    """
    results = execute_query(conn, query)
    lookup = {}
    for r in results:
        key = (r['feature'], r['customer'])
        lookup[key] = {'delta': r['delta_to_plan'], 'pct': r['pct_variance']}
    return lookup


def get_customers(conn, current_start, current_end, prior_start, prior_end, cust_plan_lookup):
    """Customer WoW using actuals with revenue + product_led_revenue."""
    query = f"""
    WITH current_week AS (
        SELECT feature, use_case, product_category, latest_salesforce_account_name as customer,
               SUM(revenue + product_led_revenue) as current_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        GROUP BY feature, use_case, product_category, latest_salesforce_account_name
    ),
    prior_week AS (
        SELECT feature, use_case, product_category, latest_salesforce_account_name as customer,
               SUM(revenue + product_led_revenue) as prior_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{prior_start}' AND '{prior_end}'
        GROUP BY feature, use_case, product_category, latest_salesforce_account_name
    ),
    customer_wow AS (
        SELECT COALESCE(c.product_category, p.product_category) as product_category,
            COALESCE(c.use_case, p.use_case) as use_case,
            COALESCE(c.feature, p.feature) as feature,
            COALESCE(c.customer, p.customer) as customer,
            COALESCE(c.current_rev, 0) as current_rev,
            COALESCE(p.prior_rev, 0) as prior_rev,
            COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) as dollar_change
        FROM current_week c FULL OUTER JOIN prior_week p ON c.feature = p.feature AND c.customer = p.customer
    ),
    feature_totals AS (
        SELECT feature, SUM(current_rev) as feat_total_current, SUM(ABS(dollar_change)) as feat_total_abs_change
        FROM customer_wow GROUP BY feature
    ),
    ranked AS (
        SELECT cw.product_category, cw.use_case, cw.feature, cw.customer, cw.current_rev, cw.prior_rev, cw.dollar_change,
            CASE WHEN cw.prior_rev > 0 THEN ROUND((cw.dollar_change / cw.prior_rev) * 100, 1) ELSE NULL END as pct_change,
            CASE WHEN ft.feat_total_current > 0 THEN ROUND((cw.current_rev / ft.feat_total_current) * 100, 2) ELSE 0 END as mix_pct,
            CASE WHEN ft.feat_total_abs_change > 0 THEN ROUND((ABS(cw.dollar_change) / ft.feat_total_abs_change) * 100, 2) ELSE 0 END as contribution_pct,
            ROW_NUMBER() OVER (PARTITION BY cw.feature ORDER BY ABS(cw.dollar_change) DESC) as rn
        FROM customer_wow cw JOIN feature_totals ft ON cw.feature = ft.feature
    )
    SELECT product_category, use_case, feature, customer, current_rev, prior_rev, dollar_change, pct_change, mix_pct, contribution_pct
    FROM ranked WHERE rn <= 10 ORDER BY product_category, feature, contribution_pct DESC
    """
    results = execute_query(conn, query)
    by_category = defaultdict(list)
    for row in results:
        key = (row['feature'], row['customer'])
        plan_data = cust_plan_lookup.get(key, {})
        row['delta_to_plan'] = plan_data.get('delta', None)
        row['pct_to_plan'] = plan_data.get('pct', None)
        by_category[row['product_category']].append(row)
    return dict(by_category)


def get_forecast_evolution(conn):
    """Y/Y growth forecast evolution using original forecast aligned view."""
    query = """
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
        SELECT * FROM actuals UNION ALL SELECT * FROM forecasts
    ),
    prep AS (
        SELECT run_date, fy_fq, product_category, SUM(revenue) AS total_revenue,
            LAG(total_revenue, 4) OVER (PARTITION BY run_date, product_category ORDER BY fy_fq) AS prev_year_quarter_revenue,
            DIV0(total_revenue, prev_year_quarter_revenue) - 1 AS yoy_growth
        FROM blended GROUP BY ALL
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
        SELECT * FROM total_actuals UNION ALL SELECT * FROM total_forecasts
    ),
    total_prep AS (
        SELECT run_date, fy_fq, SUM(revenue) AS total_revenue,
            LAG(total_revenue, 4) OVER (PARTITION BY run_date ORDER BY fy_fq) AS prev_year_quarter_revenue,
            DIV0(total_revenue, prev_year_quarter_revenue) - 1 AS yoy_growth
        FROM total_blended GROUP BY ALL
    )
    SELECT run_date, product_category, ROUND(yoy_growth * 100, 2) AS yoy_growth_pct FROM prep WHERE fy_fq = 'FY2026-Q4'
    UNION ALL
    SELECT run_date, 'Total' AS product_category, ROUND(yoy_growth * 100, 2) AS yoy_growth_pct FROM total_prep WHERE fy_fq = 'FY2026-Q4'
    ORDER BY 1, 2
    """
    return execute_query(conn, query)


def get_top_gainers(conn, current_start, current_end, prior_start, prior_end):
    """Top 15 weekly gainers using actuals with revenue + product_led_revenue."""
    query = f"""
    WITH current_week AS (
        SELECT latest_salesforce_account_name AS customer, SUM(revenue + product_led_revenue) AS current_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        GROUP BY 1
    ),
    prior_week AS (
        SELECT latest_salesforce_account_name AS customer, SUM(revenue + product_led_revenue) AS prior_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{prior_start}' AND '{prior_end}'
        GROUP BY 1
    ),
    prior_year AS (
        SELECT latest_salesforce_account_name AS customer, SUM(revenue + product_led_revenue) AS py_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN DATEADD(year, -1, '{current_start}'::date) AND DATEADD(year, -1, '{current_end}'::date)
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
        SELECT latest_salesforce_account_name AS customer, feature, SUM(revenue + product_led_revenue) AS current_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        GROUP BY 1, 2
    ),
    feature_prior AS (
        SELECT latest_salesforce_account_name AS customer, feature, SUM(revenue + product_led_revenue) AS prior_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{prior_start}' AND '{prior_end}'
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
    SELECT c.customer, 
        ROUND(c.current_rev, 0) AS current_rev, 
        ROUND(c.prior_rev, 0) AS prior_rev, 
        ROUND(c.wow_change, 0) AS wow_change,
        ROUND(100.0 * c.wow_change / NULLIF(c.prior_rev, 0), 2) AS wow_pct,
        ROUND(100.0 * (c.current_rev - c.py_rev) / NULLIF(c.py_rev, 0), 2) AS yoy_pct,
        ROUND(100.0 * c.current_rev / NULLIF(t.total_current, 0), 2) AS mix_pct,
        ROUND(100.0 * ABS(c.wow_change) / NULLIF(t.total_mag, 0), 2) AS contribution_pct,
        tgf.feature AS top_gaining_feature
    FROM combined c
    CROSS JOIN totals t
    LEFT JOIN top_gaining_feature tgf ON c.customer = tgf.customer AND tgf.rn = 1
    WHERE c.wow_change > 0
    ORDER BY c.wow_change DESC
    LIMIT 15
    """
    return execute_query(conn, query)


def get_top_contractors(conn, current_start, current_end, prior_start, prior_end):
    """Top 15 weekly contractors using actuals with revenue + product_led_revenue."""
    query = f"""
    WITH current_week AS (
        SELECT latest_salesforce_account_name AS customer, SUM(revenue + product_led_revenue) AS current_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        GROUP BY 1
    ),
    prior_week AS (
        SELECT latest_salesforce_account_name AS customer, SUM(revenue + product_led_revenue) AS prior_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{prior_start}' AND '{prior_end}'
        GROUP BY 1
    ),
    prior_year AS (
        SELECT latest_salesforce_account_name AS customer, SUM(revenue + product_led_revenue) AS py_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN DATEADD(year, -1, '{current_start}'::date) AND DATEADD(year, -1, '{current_end}'::date)
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
        SELECT latest_salesforce_account_name AS customer, feature, SUM(revenue + product_led_revenue) AS current_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        GROUP BY 1, 2
    ),
    feature_prior AS (
        SELECT latest_salesforce_account_name AS customer, feature, SUM(revenue + product_led_revenue) AS prior_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{prior_start}' AND '{prior_end}'
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
    SELECT c.customer, 
        ROUND(c.current_rev, 0) AS current_rev, 
        ROUND(c.prior_rev, 0) AS prior_rev, 
        ROUND(c.wow_change, 0) AS wow_change,
        ROUND(100.0 * c.wow_change / NULLIF(c.prior_rev, 0), 2) AS wow_pct,
        ROUND(100.0 * (c.current_rev - c.py_rev) / NULLIF(c.py_rev, 0), 2) AS yoy_pct,
        ROUND(100.0 * c.current_rev / NULLIF(t.total_current, 0), 2) AS mix_pct,
        ROUND(100.0 * ABS(c.wow_change) / NULLIF(t.total_mag, 0), 2) AS contribution_pct,
        tcf.feature AS top_contracting_feature
    FROM combined c
    CROSS JOIN totals t
    LEFT JOIN top_contracting_feature tcf ON c.customer = tcf.customer AND tcf.rn = 1
    WHERE c.wow_change < 0
    ORDER BY c.wow_change ASC
    LIMIT 15
    """
    return execute_query(conn, query)


def get_customer_feature_breakdown(conn, current_start, current_end, prior_start, prior_end):
    """Feature breakdown for customers using actuals with revenue + product_led_revenue."""
    query = f"""
    WITH feature_current AS (
        SELECT latest_salesforce_account_name AS customer, feature, SUM(revenue + product_led_revenue) AS current_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        GROUP BY 1, 2
    ),
    feature_prior AS (
        SELECT latest_salesforce_account_name AS customer, feature, SUM(revenue + product_led_revenue) AS prior_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{prior_start}' AND '{prior_end}'
        GROUP BY 1, 2
    ),
    feature_change AS (
        SELECT COALESCE(c.customer, p.customer) AS customer,
            COALESCE(c.feature, p.feature) AS feature,
            COALESCE(c.current_rev, 0) AS current_rev,
            COALESCE(p.prior_rev, 0) AS prior_rev,
            COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0) AS wow_change
        FROM feature_current c
        FULL OUTER JOIN feature_prior p ON c.customer = p.customer AND c.feature = p.feature
    )
    SELECT customer, feature, 
        ROUND(current_rev, 0) AS current_rev, 
        ROUND(prior_rev, 0) AS prior_rev, 
        ROUND(wow_change, 0) AS wow_change,
        ROUND(100.0 * wow_change / NULLIF(prior_rev, 0), 2) AS wow_pct
    FROM feature_change
    WHERE ABS(wow_change) > 0
    ORDER BY customer, ABS(wow_change) DESC
    """
    results = execute_query(conn, query)
    by_customer = defaultdict(list)
    for row in results:
        by_customer[row['customer']].append(row)
    return dict(by_customer)


def get_fq_forecast_vs_plan_target(conn, qtd_start):
    """Full quarter forecast vs plan vs target using correct tables."""
    query = f"""
    WITH fq_forecast AS (
        SELECT product_category, SUM(revenue) AS full_quarter_revenue
        FROM finance.customer.product_category_rev_actuals_w_forecast_sfdc
        WHERE DATE(usage_date) BETWEEN '{qtd_start}' AND '2026-01-31'
        GROUP BY 1
    ),
    fq_plan AS (
        SELECT product_category, SUM(revenue) AS full_quarter_plan
        FROM finance.customer.temp_product_category_revenue_plan
        WHERE DATE(general_date) BETWEEN '{qtd_start}' AND '2026-01-31'
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
        ROUND(f.full_quarter_revenue, 0) AS fq_forecast,
        ROUND(p.full_quarter_plan, 0) AS fq_plan,
        ROUND(100.0 * ((f.full_quarter_revenue / NULLIF(p.full_quarter_plan, 0)) - 1), 2) AS fq_vs_plan_pct,
        ROUND(t.full_quarter_target, 0) AS fq_target,
        ROUND(100.0 * ((f.full_quarter_revenue / NULLIF(t.full_quarter_target, 0)) - 1), 2) AS fq_vs_target_pct
    FROM fq_forecast f
    LEFT JOIN fq_plan p ON f.product_category = p.product_category
    LEFT JOIN fq_target t ON f.product_category = t.product_category
    ORDER BY f.full_quarter_revenue DESC NULLS LAST
    """
    return execute_query(conn, query)


def get_top_25_customers(conn, current_start, current_end, prior_start, prior_end):
    """Top 25 customers using actuals with revenue + product_led_revenue."""
    query = f"""
    WITH current_week AS (
        SELECT latest_salesforce_account_name AS customer, feature, SUM(revenue + product_led_revenue) AS current_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        GROUP BY 1, 2
    ),
    prior_week AS (
        SELECT latest_salesforce_account_name AS customer, feature, SUM(revenue + product_led_revenue) AS prior_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{prior_start}' AND '{prior_end}'
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
    total_change AS (
        SELECT SUM(wow_change) AS total_wow_change FROM combined
    ),
    customer_totals AS (
        SELECT 
            customer,
            SUM(current_rev) AS current_rev,
            SUM(prior_rev) AS prior_rev,
            SUM(wow_change) AS wow_change
        FROM combined
        GROUP BY 1
    ),
    total_rev AS (
        SELECT SUM(current_rev) AS total_current FROM customer_totals
    ),
    top_25 AS (
        SELECT customer
        FROM customer_totals
        ORDER BY current_rev DESC
        LIMIT 25
    ),
    feature_ranked AS (
        SELECT 
            c.customer,
            c.feature,
            c.current_rev AS feat_current,
            c.prior_rev AS feat_prior,
            c.wow_change AS feat_change,
            100.0 * c.wow_change / NULLIF(t.total_wow_change, 0) AS feat_contribution,
            ROW_NUMBER() OVER (PARTITION BY c.customer ORDER BY ABS(c.wow_change) DESC) AS rn
        FROM combined c
        CROSS JOIN total_change t
        WHERE c.customer IN (SELECT customer FROM top_25)
    )
    SELECT 
        ct.customer,
        ct.current_rev,
        ct.prior_rev,
        ct.wow_change,
        100.0 * ct.wow_change / NULLIF(ct.prior_rev, 0) AS wow_pct,
        100.0 * ct.current_rev / NULLIF(tr.total_current, 0) AS mix_pct,
        100.0 * ct.wow_change / NULLIF(tc.total_wow_change, 0) AS contribution_pct,
        fr.feature,
        fr.feat_current,
        fr.feat_prior,
        fr.feat_change,
        fr.feat_contribution
    FROM customer_totals ct
    CROSS JOIN total_rev tr
    CROSS JOIN total_change tc
    JOIN feature_ranked fr ON ct.customer = fr.customer AND fr.rn <= 5
    WHERE ct.customer IN (SELECT customer FROM top_25)
    ORDER BY ct.current_rev DESC, ct.customer, fr.rn
    """
    results = execute_query(conn, query)
    
    customers = {}
    for row in results:
        cust = row['customer']
        if cust not in customers:
            customers[cust] = {
                'customer': cust,
                'current_rev': row['current_rev'],
                'prior_rev': row['prior_rev'],
                'wow_change': row['wow_change'],
                'wow_pct': row['wow_pct'],
                'mix_pct': row['mix_pct'],
                'contribution_pct': row['contribution_pct'],
                'top_features': []
            }
        customers[cust]['top_features'].append({
            'feature': row['feature'],
            'current_rev': row['feat_current'],
            'prior_rev': row['feat_prior'],
            'wow_change': row['feat_change'],
            'contribution_pct': row['feat_contribution']
        })
    
    return list(customers.values())


def convert_to_json_safe(obj):
    if isinstance(obj, dict):
        return {k: convert_to_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_safe(v) for v in obj]
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif obj is None:
        return None
    elif isinstance(obj, (int, float, str, bool)):
        return obj
    else:
        return float(obj) if obj else 0


def main(args):
    output_path = args.output

    conn = get_connection()
    
    if args.current_week_start and args.current_week_end:
        current_start = args.current_week_start
        current_end = args.current_week_end
        current_start_dt = datetime.strptime(current_start, '%Y-%m-%d').date()
        prior_end_dt = current_start_dt - timedelta(days=1)
        prior_start_dt = prior_end_dt - timedelta(days=6)
        prior_start = prior_start_dt.strftime('%Y-%m-%d')
        prior_end = prior_end_dt.strftime('%Y-%m-%d')
    else:
        dates = calculate_week_dates()
        current_start = dates['current_week_start'].strftime('%Y-%m-%d')
        current_end = dates['current_week_end'].strftime('%Y-%m-%d')
        prior_start = dates['prior_week_start'].strftime('%Y-%m-%d')
        prior_end = dates['prior_week_end'].strftime('%Y-%m-%d')

    qtd_start, _ = get_fiscal_dates(conn)
    
    print(f"Week: {current_start} to {current_end} | Prior: {prior_start} to {prior_end} | QTD: {qtd_start}")

    print("1/13 Category WoW...")
    category_wow = get_category_wow(conn, current_start, current_end, prior_start, prior_end)
    
    print("2/13 QTD vs Plan (category)...")
    qtd_vs_plan = get_qtd_vs_plan(conn, current_end)
    
    print("3/13 QTD Plan by use case & feature...")
    uc_plan_lookup = get_qtd_plan_by_use_case(conn, current_end)
    feat_plan_lookup = get_qtd_plan_by_feature(conn, current_end)
    
    print("4/13 Use cases...")
    use_cases = get_use_cases(conn, current_start, current_end, prior_start, prior_end, uc_plan_lookup)
    
    print("5/13 Features...")
    features = get_features(conn, current_start, current_end, prior_start, prior_end, feat_plan_lookup)
    
    print("6/13 QTD Plan by customer...") 
    cust_plan_lookup = get_qtd_plan_by_customer(conn, current_end)
    
    print("7/13 Customers (top 10 per feature)...")
    customers = get_customers(conn, current_start, current_end, prior_start, prior_end, cust_plan_lookup)
    
    print("8/13 Forecast evolution...")
    forecast_evolution = get_forecast_evolution(conn)
    
    print("9/13 Top gainers...")
    top_gainers = get_top_gainers(conn, current_start, current_end, prior_start, prior_end)
    
    print("10/13 Top contractors...")
    top_contractors = get_top_contractors(conn, current_start, current_end, prior_start, prior_end)
    
    print("11/13 Customer feature breakdown...")
    customer_features = get_customer_feature_breakdown(conn, current_start, current_end, prior_start, prior_end)
    
    print("12/13 FQ Forecast vs Plan vs Target...")
    fq_forecast = get_fq_forecast_vs_plan_target(conn, str(qtd_start) if qtd_start else '2025-11-01')
    
    print("13/13 Top 25 customers with feature breakdown...")
    top_25_customers = get_top_25_customers(conn, current_start, current_end, prior_start, prior_end)
    
    conn.close()

    data = convert_to_json_safe({
        'metadata': {
            'current_week_start': current_start, 'current_week_end': current_end,
            'prior_week_start': prior_start, 'prior_week_end': prior_end,
            'qtd_start': str(qtd_start) if qtd_start else None,
            'generated_at': datetime.now().isoformat(),
        },
        'category_wow': category_wow,
        'qtd_vs_plan': qtd_vs_plan,
        'use_cases': use_cases,
        'features': features,
        'customers': customers,
        'forecast_evolution': forecast_evolution,
        'top_gainers': top_gainers,
        'top_contractors': top_contractors,
        'customer_features': customer_features,
        'fq_forecast': fq_forecast,
        'top_25_customers': top_25_customers,
    })

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Saved to {output_path}")
    print(f"   {len(category_wow)} categories, {sum(len(uc) for uc in use_cases.values())} use cases")
    print(f"   {len(top_gainers)} gainers, {len(top_contractors)} contractors")
    print(f"   {len(forecast_evolution)} forecast data points")


def collect_all_data(week_start, week_end, output_path):
    """Entry point for programmatic use."""
    class Args:
        current_week_start = week_start
        current_week_end = week_end
        output = output_path
    main(Args())


def main_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--current-week-start')
    parser.add_argument('--current-week-end')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    main_cli()
