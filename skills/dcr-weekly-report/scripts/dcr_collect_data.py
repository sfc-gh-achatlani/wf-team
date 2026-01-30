#!/usr/bin/env python3
"""
dcr_collect_data.py - Collect all data for DCR/Data Cleanroom weekly HTML report.

DATA SOURCES:
- DCR Revenue: finance.customer.fy26_product_category_revenue (feature='Data Clean Room')
- Active Accounts: snowscience.cleanrooms.samooha_consumption_v
- Credits: snowscience.cleanrooms.samooha_consumption_v + spcs credits
- Partner Edges: snowscience.cleanrooms.all_cleanroom_jobs + cleanroom_edges
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


def execute_query(conn, query, desc=""):
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [d[0].lower() for d in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    return [dict(zip(columns, row)) for row in rows]


def calculate_week_dates(week_end_str):
    """Calculate week boundaries from week end date (Sunday)."""
    week_end = datetime.strptime(week_end_str, '%Y-%m-%d').date()
    week_start = week_end - timedelta(days=6)
    prior_week_end = week_start - timedelta(days=1)
    prior_week_start = prior_week_end - timedelta(days=6)
    return {
        'current_week_start': week_start,
        'current_week_end': week_end,
        'prior_week_start': prior_week_start,
        'prior_week_end': prior_week_end,
    }


def get_fiscal_dates(conn, week_end):
    query = f"""
    SELECT fiscal_quarter_start, fiscal_quarter_end
    FROM finance.stg_utils.stg_fiscal_calendar
    WHERE _date = '{week_end}' LIMIT 1
    """
    cursor = conn.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    cursor.close()
    return (row[0], row[1]) if row else (None, None)


def get_dcr_revenue_wow(conn, current_start, current_end, prior_start, prior_end):
    """DCR revenue WoW from FY26_PRODUCT_CATEGORY_REVENUE."""
    query = f"""
    WITH current_week AS (
        SELECT SUM(revenue + product_led_revenue) AS current_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        AND feature = 'Data Clean Room'
    ),
    prior_week AS (
        SELECT SUM(revenue + product_led_revenue) AS prior_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{prior_start}' AND '{prior_end}'
        AND feature = 'Data Clean Room'
    )
    SELECT 
        ROUND(COALESCE(c.current_rev, 0), 0) AS current_rev,
        ROUND(COALESCE(p.prior_rev, 0), 0) AS prior_rev,
        ROUND(COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0), 0) AS dollar_change,
        ROUND(100.0 * (COALESCE(c.current_rev, 0) - COALESCE(p.prior_rev, 0)) / NULLIF(p.prior_rev, 0), 2) AS pct_change
    FROM current_week c, prior_week p
    """
    return execute_query(conn, query)[0]


def get_dcr_qtd_vs_plan(conn, week_end):
    """DCR QTD actual vs plan."""
    query = f"""
    WITH fiscal_context AS (
        SELECT fiscal_quarter_start FROM finance.stg_utils.stg_fiscal_calendar
        WHERE _date = '{week_end}' LIMIT 1
    ),
    qtd_actuals AS (
        SELECT SUM(revenue + product_led_revenue) AS qtd_actual
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds >= (SELECT fiscal_quarter_start FROM fiscal_context) AND ds <= '{week_end}'
        AND feature = 'Data Clean Room'
    ),
    qtd_plan AS (
        SELECT SUM(revenue) AS qtd_plan
        FROM finance.customer.temp_product_category_revenue_plan
        WHERE general_date >= (SELECT fiscal_quarter_start FROM fiscal_context) 
          AND general_date <= '{week_end}'
          AND feature = 'Data Clean Room'
    )
    SELECT 
        ROUND(COALESCE(a.qtd_actual, 0), 0) AS qtd_actual,
        ROUND(COALESCE(p.qtd_plan, 0), 0) AS qtd_plan,
        ROUND(COALESCE(a.qtd_actual, 0) - COALESCE(p.qtd_plan, 0), 0) AS delta_to_plan,
        ROUND(100.0 * (COALESCE(a.qtd_actual, 0) - COALESCE(p.qtd_plan, 0)) / NULLIF(p.qtd_plan, 0), 2) AS pct_variance
    FROM qtd_actuals a, qtd_plan p
    """
    return execute_query(conn, query)[0]


def get_dau_wau_mau(conn, date_range_start, date_range_end, job_buckets=None, account_types=None):
    """DAU/WAU/MAU metrics for DCR accounts."""
    job_bucket_filter = ""
    if job_buckets:
        bucket_list = ", ".join([f"'{b}'" for b in job_buckets])
        job_bucket_filter = f"AND job_bucket IN ({bucket_list})"
    
    account_type_filter = ""
    if account_types:
        type_list = ", ".join([f"'{t}'" for t in account_types])
        account_type_filter = f"AND snowflake_account_type IN ({type_list})"

    query = f"""
    WITH combined AS (
        SELECT DISTINCT ds, salesforce_account_id AS account_id, 1 as flag 
        FROM snowscience.cleanrooms.samooha_consumption_v j
        WHERE ds BETWEEN '{date_range_start}' AND '{date_range_end}'
        AND coalesce(salesforce_account_id, '') != ''
        {job_bucket_filter}
        {account_type_filter}
    ),
    dau AS (
        SELECT ds,
            COUNT(DISTINCT account_id) AS daily_active_cnt,
            AVG(COUNT(DISTINCT account_id)) OVER (ORDER BY ds ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)::NUMBER AS daily_moving_avg_7_days
        FROM combined 
        GROUP BY 1
    ),
    wau AS (
        SELECT t1.ds,
            COUNT(DISTINCT t2.account_id) AS weekly_active_cnt
        FROM combined t1
        CROSS JOIN combined t2
        WHERE TO_DATE(t2.ds) > TO_DATE(t1.ds) - 7 AND TO_DATE(t2.ds) <= TO_DATE(t1.ds)
        GROUP BY 1
    ),
    mau AS (
        SELECT t1.ds,
            COUNT(DISTINCT t2.account_id) AS monthly_active_cnt
        FROM combined t1
        CROSS JOIN combined t2
        WHERE TO_DATE(t2.ds) > TO_DATE(t1.ds) - 28 AND TO_DATE(t2.ds) <= TO_DATE(t1.ds)
        GROUP BY 1
    )
    SELECT 
        mau.ds,
        ROW_NUMBER() OVER (ORDER BY mau.ds) AS rn,
        daily_active_cnt AS daily,
        IFF(rn >= 7, weekly_active_cnt, NULL) AS last_7_days,
        IFF(rn >= 28, monthly_active_cnt, NULL) AS last_28_days,
        IFF(rn >= 7, daily_moving_avg_7_days, NULL) AS daily_moving_avg_7_days
    FROM mau
    INNER JOIN wau ON mau.ds = wau.ds
    INNER JOIN dau ON mau.ds = dau.ds
    WHERE mau.ds BETWEEN '{date_range_start}' AND '{date_range_end}'
    ORDER BY mau.ds
    """
    return execute_query(conn, query)


def get_total_credits(conn, date_range_start, date_range_end, account_types=None):
    """Total DCR credits (samooha job + SPCS direct + SPCS indirect)."""
    account_type_filter = ""
    if account_types:
        type_list = ", ".join([f"'{t}'" for t in account_types])
        account_type_filter = f"AND c.snowflake_account_type IN ({type_list})"

    query = f"""
    WITH spcs_indirect_jobs AS (
        SELECT ds, deployment, account_id, service_id, compute_pool_id, job_id, total_credits
        FROM snowscience.snowservices.spcs_credits_indirect_from_spcs_raw
        UNION ALL
        SELECT ds, deployment, account_id, target_service_id::VARIANT AS service_id, compute_pool_id::VARIANT AS compute_pool_id, job_id, total_credits
        FROM snowscience.snowservices.spcs_credits_indirect_to_spcs_raw
    ),
    samooha_job_credits AS (
        SELECT ds, SUM(job_credits) AS credits
        FROM snowscience.cleanrooms.samooha_consumption_v c
        WHERE ds BETWEEN '{date_range_start}' AND '{date_range_end}'
        AND coalesce(c.salesforce_account_id, '') != ''
        {account_type_filter}
        GROUP BY 1
    ),
    samooha_spcs_direct AS (
        SELECT ds, SUM(spcs_direct_credits) AS credits
        FROM snowscience.cleanrooms.samooha_spcs_credits c
        WHERE ds BETWEEN '{date_range_start}' AND '{date_range_end}'
        AND coalesce(c.salesforce_account_id, '') != ''
        {account_type_filter.replace('c.', '')}
        GROUP BY 1
    ),
    samooha_spcs_indirect AS (
        SELECT j.ds, SUM(j.total_credits) AS credits
        FROM spcs_indirect_jobs j
        JOIN snowscience.snowservices.spcs_dim_services d 
            ON j.deployment = d.deployment
            AND j.account_id = d.account_id
            AND j.compute_pool_id = d.compute_pool_id
            AND j.service_id = d.service_id
        LEFT JOIN snowscience.cleanrooms.dim_cleanroom_accounts_v a 
            ON j.account_id = a.snowflake_account_id
            AND j.deployment = a.snowflake_deployment
        WHERE j.ds BETWEEN '{date_range_start}' AND '{date_range_end}'
        AND coalesce(a.salesforce_account_id, '') != ''
        AND d.managing_object_type = 'NativeApp(DCR)'
        AND NOT EXISTS (
            SELECT 1 FROM snowscience.cleanrooms.samooha_consumption_v r  
            WHERE r.job_id = j.job_id AND r.deployment = j.deployment AND r.account_id = j.account_id
        )
        GROUP BY 1
    ),
    combined AS (
        SELECT ds, credits FROM samooha_job_credits
        UNION ALL
        SELECT ds, credits FROM samooha_spcs_direct
        UNION ALL
        SELECT ds, credits FROM samooha_spcs_indirect
    )
    SELECT 
        ds,
        SUM(credits) AS credits,
        ROW_NUMBER() OVER (ORDER BY ds ASC) AS rn,
        IFF(rn < 7, NULL, AVG(SUM(credits)) OVER (ORDER BY ds ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)) AS last_7_moving_avg,
        IFF(rn < 28, NULL, AVG(SUM(credits)) OVER (ORDER BY ds ROWS BETWEEN 27 PRECEDING AND CURRENT ROW)) AS last_28_moving_avg
    FROM combined
    GROUP BY ds
    ORDER BY ds
    """
    return execute_query(conn, query)


def get_credits_by_source(conn, current_start, current_end):
    """Credits breakdown by source (job, SPCS direct, SPCS indirect)."""
    query = f"""
    WITH spcs_indirect_jobs AS (
        SELECT ds, deployment, account_id, service_id, compute_pool_id, job_id, total_credits
        FROM snowscience.snowservices.spcs_credits_indirect_from_spcs_raw
        UNION ALL
        SELECT ds, deployment, account_id, target_service_id::VARIANT AS service_id, compute_pool_id::VARIANT AS compute_pool_id, job_id, total_credits
        FROM snowscience.snowservices.spcs_credits_indirect_to_spcs_raw
    ),
    samooha_job_credits AS (
        SELECT 'Samooha Jobs' AS source, SUM(job_credits) AS credits
        FROM snowscience.cleanrooms.samooha_consumption_v c
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        AND coalesce(c.salesforce_account_id, '') != ''
        AND c.snowflake_account_type = 'Customer'
    ),
    samooha_spcs_direct AS (
        SELECT 'SPCS Direct' AS source, SUM(spcs_direct_credits) AS credits
        FROM snowscience.cleanrooms.samooha_spcs_credits c
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        AND coalesce(c.salesforce_account_id, '') != ''
        AND c.snowflake_account_type = 'Customer'
    ),
    samooha_spcs_indirect AS (
        SELECT 'SPCS Indirect' AS source, SUM(j.total_credits) AS credits
        FROM spcs_indirect_jobs j
        JOIN snowscience.snowservices.spcs_dim_services d 
            ON j.deployment = d.deployment AND j.account_id = d.account_id
            AND j.compute_pool_id = d.compute_pool_id AND j.service_id = d.service_id
        LEFT JOIN snowscience.cleanrooms.dim_cleanroom_accounts_v a 
            ON j.account_id = a.snowflake_account_id AND j.deployment = a.snowflake_deployment
        WHERE j.ds BETWEEN '{current_start}' AND '{current_end}'
        AND coalesce(a.salesforce_account_id, '') != ''
        AND a.snowflake_account_type = 'Customer'
        AND d.managing_object_type = 'NativeApp(DCR)'
        AND NOT EXISTS (
            SELECT 1 FROM snowscience.cleanrooms.samooha_consumption_v r  
            WHERE r.job_id = j.job_id AND r.deployment = j.deployment AND r.account_id = j.account_id
        )
    )
    SELECT * FROM samooha_job_credits
    UNION ALL SELECT * FROM samooha_spcs_direct
    UNION ALL SELECT * FROM samooha_spcs_indirect
    """
    return execute_query(conn, query)


def get_partner_edges(conn, date_range_start, date_range_end, account_types=None):
    """Partner/provider-consumer edge details with credits from samooha_analysis_jobs."""
    account_type_filter = ""
    if account_types:
        type_list = ", ".join([f"'{t}'" for t in account_types])
        account_type_filter = f"AND d.snowflake_account_type IN ({type_list})"

    query = f"""
    WITH base_ AS (
        SELECT 
            salesforce_account_name AS consumer,
            COALESCE(ARRAY_TO_STRING(providers, ','), '<unknown>') AS provider,
            SUM(d.total_credits) AS credits,
            MIN(d.ds) AS min_ds,
            MAX(d.ds) AS max_ds,
            ARRAY_UNIQUE_AGG(d.detailed_analysis_type) AS analysis_types,
            ARRAY_UNIQUE_AGG(d.application_id) AS application_ids,
            ARRAY_UNIQUE_AGG(d.cleanroom_id) AS cleanroom_ids,
            ARRAY_UNION_AGG(d.database_name) AS database_names,
            COUNT(DISTINCT root_uuid, deployment) AS jobs,
            COUNT(DISTINCT IFF(sproc_errored, root_uuid || deployment, NULL)) AS errored_jobs,
            errored_jobs / NULLIF(COUNT(DISTINCT root_uuid, deployment), 0) AS job_error_rt
        FROM snowscience.cleanrooms.samooha_analysis_jobs d
        WHERE TRUE
        {account_type_filter}
        AND COALESCE(d.salesforce_account_id, '') != ''
        AND d.ds BETWEEN '{date_range_start}' AND '{date_range_end}'
        GROUP BY ALL
        ORDER BY credits DESC
    ),
    penultimate AS (
        SELECT     
            CASE 
                WHEN provider = consumer THEN provider 
                WHEN provider != consumer THEN CONCAT_WS(' -> ', provider, consumer)
                ELSE 'other'
            END AS provider_consumer_label,
            credits,
            min_ds,
            max_ds,
            analysis_types,
            application_ids,
            cleanroom_ids,
            database_names,
            jobs,
            errored_jobs,
            job_error_rt
        FROM base_
    ),
    stable_edges AS (
        SELECT  
            CONCAT_WS(' -> ', a.salesforce_account_name, a2.salesforce_account_name) AS edge_name,
            COUNT(DISTINCT e.edge_id) AS edges
        FROM snowscience.cleanrooms.cleanroom_edges e
        JOIN snowscience.cleanrooms.dim_cleanroom_accounts_v a ON (
            e.provider_account_id = a.snowflake_account_id
            AND e.provider_deployment = a.snowflake_deployment
        )
        JOIN snowscience.cleanrooms.dim_cleanroom_accounts_v a2 ON (
            e.consumer_account_id = a2.snowflake_account_id
            AND e.consumer_deployment = a2.snowflake_deployment
        )
        WHERE ds = (SELECT MAX(ds) FROM snowscience.cleanrooms.cleanroom_edges)
        AND ASSOCIATED_STABLE_EDGE
        AND ARRAY_CONTAINS('DCR_SAMOOHA'::VARIANT, job_types)
        GROUP BY ALL
    )
    SELECT 
        a.provider_consumer_label,
        ROUND(a.credits, 2) AS job_credits,
        COALESCE(m.edges, 0) AS associated_stable_edges,
        COALESCE(m.edges, 0) > 0 AS has_stable_edge,
        a.min_ds AS first_job,
        a.max_ds AS last_job,
        a.analysis_types,
        a.application_ids,
        a.cleanroom_ids,
        a.database_names,
        a.jobs,
        a.errored_jobs,
        ROUND(a.job_error_rt * 100, 2) AS job_error_pct
    FROM penultimate a
    LEFT JOIN stable_edges m ON (m.edge_name = a.provider_consumer_label)
    ORDER BY credits DESC NULLS LAST
    LIMIT 100
    """
    return execute_query(conn, query)


def get_top_customers_by_credits(conn, current_start, current_end, prior_start, prior_end):
    """Top DCR customers by credits with WoW change."""
    query = f"""
    WITH current_week AS (
        SELECT salesforce_account_name AS customer, SUM(job_credits) AS current_credits
        FROM snowscience.cleanrooms.samooha_consumption_v
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        AND coalesce(salesforce_account_id, '') != ''
        AND snowflake_account_type = 'Customer'
        GROUP BY 1
    ),
    prior_week AS (
        SELECT salesforce_account_name AS customer, SUM(job_credits) AS prior_credits
        FROM snowscience.cleanrooms.samooha_consumption_v
        WHERE ds BETWEEN '{prior_start}' AND '{prior_end}'
        AND coalesce(salesforce_account_id, '') != ''
        AND snowflake_account_type = 'Customer'
        GROUP BY 1
    ),
    combined AS (
        SELECT 
            COALESCE(c.customer, p.customer) AS customer,
            COALESCE(c.current_credits, 0) AS current_credits,
            COALESCE(p.prior_credits, 0) AS prior_credits,
            COALESCE(c.current_credits, 0) - COALESCE(p.prior_credits, 0) AS wow_change
        FROM current_week c
        FULL OUTER JOIN prior_week p ON c.customer = p.customer
    ),
    totals AS (
        SELECT SUM(current_credits) AS total_current FROM combined
    )
    SELECT 
        c.customer,
        ROUND(c.current_credits, 2) AS current_credits,
        ROUND(c.prior_credits, 2) AS prior_credits,
        ROUND(c.wow_change, 2) AS wow_change,
        ROUND(100.0 * c.wow_change / NULLIF(c.prior_credits, 0), 2) AS wow_pct,
        ROUND(100.0 * c.current_credits / NULLIF(t.total_current, 0), 2) AS mix_pct
    FROM combined c
    CROSS JOIN totals t
    WHERE c.current_credits > 0
    ORDER BY c.current_credits DESC
    LIMIT 25
    """
    return execute_query(conn, query)


def get_dcr_job_buckets_breakdown(conn, current_start, current_end):
    """Job breakdown by bucket type."""
    query = f"""
    SELECT 
        job_bucket,
        COUNT(DISTINCT job_id) AS job_count,
        COUNT(DISTINCT salesforce_account_id) AS account_count,
        ROUND(SUM(job_credits), 2) AS credits
    FROM snowscience.cleanrooms.samooha_consumption_v
    WHERE ds BETWEEN '{current_start}' AND '{current_end}'
    AND coalesce(salesforce_account_id, '') != ''
    AND snowflake_account_type = 'Customer'
    GROUP BY 1
    ORDER BY credits DESC
    LIMIT 20
    """
    return execute_query(conn, query)


def get_dcr_daily_revenue(conn, date_range_start, date_range_end):
    """Daily DCR revenue for trend chart with 7-day rolling average."""
    query = f"""
    WITH daily AS (
        SELECT 
            ds,
            SUM(revenue + product_led_revenue) AS revenue
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{date_range_start}' AND '{date_range_end}'
        AND feature = 'Data Clean Room'
        GROUP BY 1
    )
    SELECT 
        ds,
        ROUND(revenue, 2) AS revenue,
        ROW_NUMBER() OVER (ORDER BY ds) AS rn,
        IFF(rn >= 7, ROUND(AVG(revenue) OVER (ORDER BY ds ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2), NULL) AS revenue_7day_avg
    FROM daily
    ORDER BY ds
    """
    return execute_query(conn, query)


def get_dcr_weekly_revenue_table(conn, week_end):
    """Weekly revenue table with comprehensive financial metrics."""
    query = f"""
    WITH fiscal_context AS (
        SELECT 
            fiscal_quarter_start,
            fiscal_quarter_end,
            fiscal_year_start,
            fiscal_year_end,
            fiscal_quarter_qq_fyyyyy AS fiscal_quarter_name,
            fiscal_year_fyyyyy AS fiscal_year_name
        FROM finance.stg_utils.stg_fiscal_calendar
        WHERE _date = '{week_end}' LIMIT 1
    ),
    weeks AS (
        SELECT 
            DATEADD('day', -seq4() * 7, '{week_end}'::DATE) AS week_end_dt,
            DATEADD('day', -seq4() * 7 - 6, '{week_end}'::DATE) AS week_start_dt
        FROM TABLE(GENERATOR(ROWCOUNT => 12))
    ),
    weekly_actuals AS (
        SELECT 
            w.week_end_dt,
            w.week_start_dt,
            SUM(r.revenue + r.product_led_revenue) AS revenue
        FROM weeks w
        LEFT JOIN finance.customer.fy26_product_category_revenue r
            ON r.ds BETWEEN w.week_start_dt AND w.week_end_dt
            AND r.feature = 'Data Clean Room'
        GROUP BY 1, 2
    ),
    weekly_plan AS (
        SELECT 
            w.week_end_dt,
            SUM(p.revenue) AS plan_revenue
        FROM weeks w
        LEFT JOIN finance.customer.temp_product_category_revenue_plan p
            ON p.general_date BETWEEN w.week_start_dt AND w.week_end_dt
            AND p.feature = 'Data Clean Room'
        GROUP BY 1
    ),
    qtd_actuals AS (
        SELECT SUM(revenue + product_led_revenue) AS qtd_actual
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds >= (SELECT fiscal_quarter_start FROM fiscal_context) 
          AND ds <= '{week_end}'
          AND feature = 'Data Clean Room'
    ),
    qtd_plan AS (
        SELECT SUM(revenue) AS qtd_plan
        FROM finance.customer.temp_product_category_revenue_plan
        WHERE general_date >= (SELECT fiscal_quarter_start FROM fiscal_context)
          AND general_date <= '{week_end}'
          AND feature = 'Data Clean Room'
    ),
    ytd_actuals AS (
        SELECT SUM(revenue + product_led_revenue) AS ytd_actual
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds >= (SELECT fiscal_year_start FROM fiscal_context) 
          AND ds <= '{week_end}'
          AND feature = 'Data Clean Room'
    ),
    ytd_plan AS (
        SELECT SUM(revenue) AS ytd_plan
        FROM finance.customer.temp_product_category_revenue_plan
        WHERE general_date >= (SELECT fiscal_year_start FROM fiscal_context)
          AND general_date <= '{week_end}'
          AND feature = 'Data Clean Room'
    )
    SELECT 
        a.week_end_dt AS week_end,
        a.week_start_dt AS week_start,
        ROUND(a.revenue, 0) AS revenue,
        ROUND(p.plan_revenue, 0) AS plan,
        ROUND(a.revenue - p.plan_revenue, 0) AS variance_to_plan,
        ROUND(100.0 * (a.revenue - p.plan_revenue) / NULLIF(p.plan_revenue, 0), 2) AS variance_pct,
        ROUND(LAG(a.revenue) OVER (ORDER BY a.week_end_dt), 0) AS prior_week_rev,
        ROUND(a.revenue - LAG(a.revenue) OVER (ORDER BY a.week_end_dt), 0) AS wow_change,
        ROUND(100.0 * (a.revenue - LAG(a.revenue) OVER (ORDER BY a.week_end_dt)) / NULLIF(LAG(a.revenue) OVER (ORDER BY a.week_end_dt), 0), 2) AS wow_pct,
        ROUND(AVG(a.revenue) OVER (ORDER BY a.week_end_dt ROWS BETWEEN 3 PRECEDING AND CURRENT ROW), 0) AS four_week_avg,
        (SELECT fiscal_quarter_name FROM fiscal_context) AS fiscal_quarter,
        ROUND((SELECT qtd_actual FROM qtd_actuals), 0) AS qtd_actual,
        ROUND((SELECT qtd_plan FROM qtd_plan), 0) AS qtd_plan,
        ROUND((SELECT qtd_actual FROM qtd_actuals) - (SELECT qtd_plan FROM qtd_plan), 0) AS qtd_variance,
        ROUND(100.0 * ((SELECT qtd_actual FROM qtd_actuals) - (SELECT qtd_plan FROM qtd_plan)) / NULLIF((SELECT qtd_plan FROM qtd_plan), 0), 2) AS qtd_variance_pct,
        (SELECT fiscal_year_name FROM fiscal_context) AS fiscal_year,
        ROUND((SELECT ytd_actual FROM ytd_actuals), 0) AS ytd_actual,
        ROUND((SELECT ytd_plan FROM ytd_plan), 0) AS ytd_plan,
        ROUND((SELECT ytd_actual FROM ytd_actuals) - (SELECT ytd_plan FROM ytd_plan), 0) AS ytd_variance,
        ROUND(100.0 * ((SELECT ytd_actual FROM ytd_actuals) - (SELECT ytd_plan FROM ytd_plan)) / NULLIF((SELECT ytd_plan FROM ytd_plan), 0), 2) AS ytd_variance_pct
    FROM weekly_actuals a
    LEFT JOIN weekly_plan p ON a.week_end_dt = p.week_end_dt
    ORDER BY a.week_end_dt DESC
    """
    return execute_query(conn, query)


def get_dcr_top_revenue_customers(conn, current_start, current_end, prior_start, prior_end):
    """Top DCR customers by revenue."""
    query = f"""
    WITH current_week AS (
        SELECT latest_salesforce_account_name AS customer, SUM(revenue + product_led_revenue) AS current_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        AND feature = 'Data Clean Room'
        GROUP BY 1
    ),
    prior_week AS (
        SELECT latest_salesforce_account_name AS customer, SUM(revenue + product_led_revenue) AS prior_rev
        FROM finance.customer.fy26_product_category_revenue
        WHERE ds BETWEEN '{prior_start}' AND '{prior_end}'
        AND feature = 'Data Clean Room'
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
        SELECT SUM(current_rev) AS total_current, SUM(ABS(wow_change)) AS total_mag FROM combined
    )
    SELECT 
        c.customer,
        ROUND(c.current_rev, 0) AS current_rev,
        ROUND(c.prior_rev, 0) AS prior_rev,
        ROUND(c.wow_change, 0) AS wow_change,
        ROUND(100.0 * c.wow_change / NULLIF(c.prior_rev, 0), 2) AS wow_pct,
        ROUND(100.0 * c.current_rev / NULLIF(t.total_current, 0), 2) AS mix_pct,
        ROUND(100.0 * ABS(c.wow_change) / NULLIF(t.total_mag, 0), 2) AS contribution_pct
    FROM combined c
    CROSS JOIN totals t
    WHERE c.current_rev > 0
    ORDER BY c.current_rev DESC
    LIMIT 25
    """
    return execute_query(conn, query)


def get_dcr_new_vs_returning_accounts(conn, current_start, current_end, prior_start, prior_end):
    """New vs returning DCR accounts."""
    query = f"""
    WITH current_accounts AS (
        SELECT DISTINCT salesforce_account_id 
        FROM snowscience.cleanrooms.samooha_consumption_v
        WHERE ds BETWEEN '{current_start}' AND '{current_end}'
        AND coalesce(salesforce_account_id, '') != ''
        AND snowflake_account_type = 'Customer'
    ),
    prior_accounts AS (
        SELECT DISTINCT salesforce_account_id 
        FROM snowscience.cleanrooms.samooha_consumption_v
        WHERE ds BETWEEN '{prior_start}' AND '{prior_end}'
        AND coalesce(salesforce_account_id, '') != ''
        AND snowflake_account_type = 'Customer'
    ),
    all_historical AS (
        SELECT DISTINCT salesforce_account_id 
        FROM snowscience.cleanrooms.samooha_consumption_v
        WHERE ds < '{current_start}'
        AND coalesce(salesforce_account_id, '') != ''
        AND snowflake_account_type = 'Customer'
    )
    SELECT 
        (SELECT COUNT(*) FROM current_accounts) AS total_current,
        (SELECT COUNT(*) FROM current_accounts WHERE salesforce_account_id IN (SELECT * FROM prior_accounts)) AS returning_from_prior,
        (SELECT COUNT(*) FROM current_accounts WHERE salesforce_account_id NOT IN (SELECT * FROM all_historical)) AS brand_new,
        (SELECT COUNT(*) FROM current_accounts WHERE salesforce_account_id NOT IN (SELECT * FROM prior_accounts) AND salesforce_account_id IN (SELECT * FROM all_historical)) AS reactivated
    """
    return execute_query(conn, query)[0]


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
    conn = get_connection()
    
    week_end = args.week_end
    dates = calculate_week_dates(week_end)
    current_start = dates['current_week_start'].strftime('%Y-%m-%d')
    current_end = dates['current_week_end'].strftime('%Y-%m-%d')
    prior_start = dates['prior_week_start'].strftime('%Y-%m-%d')
    prior_end = dates['prior_week_end'].strftime('%Y-%m-%d')
    
    qtd_start, qtd_end = get_fiscal_dates(conn, week_end)
    
    lookback_start = (dates['current_week_end'] - timedelta(days=60)).strftime('%Y-%m-%d')
    
    print(f"Week: {current_start} to {current_end}")
    print(f"Prior: {prior_start} to {prior_end}")
    print(f"QTD: {qtd_start}")
    print(f"Lookback: {lookback_start} to {current_end}")

    print("\n1/11 DCR Revenue WoW...")
    dcr_revenue_wow = get_dcr_revenue_wow(conn, current_start, current_end, prior_start, prior_end)
    
    print("2/11 DCR QTD vs Plan...")
    dcr_qtd = get_dcr_qtd_vs_plan(conn, current_end)
    
    print("3/11 DAU/WAU/MAU (all account types)...")
    dau_wau_mau_all = get_dau_wau_mau(conn, lookback_start, current_end)
    
    print("4/11 DAU/WAU/MAU (customers only)...")
    dau_wau_mau_customers = get_dau_wau_mau(conn, lookback_start, current_end, account_types=['Customer'])
    
    print("5/11 Total Credits daily...")
    credits_daily = get_total_credits(conn, lookback_start, current_end, account_types=['Customer'])
    
    print("6/11 Credits by source...")
    credits_by_source = get_credits_by_source(conn, current_start, current_end)
    
    print("7/11 Partner edges...")
    partner_edges = get_partner_edges(conn, current_start, current_end, account_types=['Customer'])
    
    print("8/11 Top customers by credits...")
    top_customers_credits = get_top_customers_by_credits(conn, current_start, current_end, prior_start, prior_end)
    
    print("9/11 Top customers by revenue...")
    top_customers_revenue = get_dcr_top_revenue_customers(conn, current_start, current_end, prior_start, prior_end)
    
    print("10/11 Job buckets breakdown...")
    job_buckets = get_dcr_job_buckets_breakdown(conn, current_start, current_end)
    
    print("11/11 Daily revenue trend...")
    daily_revenue = get_dcr_daily_revenue(conn, lookback_start, current_end)
    
    print("12/12 Weekly revenue table...")
    weekly_revenue_table = get_dcr_weekly_revenue_table(conn, current_end)
    
    print("Bonus: New vs returning accounts...")
    account_cohorts = get_dcr_new_vs_returning_accounts(conn, current_start, current_end, prior_start, prior_end)
    
    conn.close()

    data = convert_to_json_safe({
        'metadata': {
            'week_end': week_end,
            'current_week_start': current_start,
            'current_week_end': current_end,
            'prior_week_start': prior_start,
            'prior_week_end': prior_end,
            'qtd_start': str(qtd_start) if qtd_start else None,
            'lookback_start': lookback_start,
            'generated_at': datetime.now().isoformat(),
        },
        'dcr_revenue_wow': dcr_revenue_wow,
        'dcr_qtd': dcr_qtd,
        'dau_wau_mau_all': dau_wau_mau_all,
        'dau_wau_mau_customers': dau_wau_mau_customers,
        'credits_daily': credits_daily,
        'credits_by_source': credits_by_source,
        'partner_edges': partner_edges,
        'top_customers_credits': top_customers_credits,
        'top_customers_revenue': top_customers_revenue,
        'job_buckets': job_buckets,
        'daily_revenue': daily_revenue,
        'weekly_revenue_table': weekly_revenue_table,
        'account_cohorts': account_cohorts,
    })

    with open(args.output, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Saved to {args.output}")
    print(f"   Revenue WoW: ${dcr_revenue_wow.get('dollar_change', 0):,.0f} ({dcr_revenue_wow.get('pct_change', 0)}%)")
    print(f"   QTD vs Plan: ${dcr_qtd.get('delta_to_plan', 0):,.0f} ({dcr_qtd.get('pct_variance', 0)}%)")
    print(f"   {len(partner_edges)} partner edges, {len(top_customers_credits)} top credit customers")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--week-end', required=True, help='Week end date (YYYY-MM-DD, Sunday)')
    parser.add_argument('--output', required=True, help='Output JSON path')
    args = parser.parse_args()
    main(args)
