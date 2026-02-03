"""
collector.py - Hierarchical Data Collection Orchestrator

This is the main entry point for collecting L1 commentary data.
It orchestrates the hierarchy traversal and analysis collection.
"""

import os
import json
import fcntl
import atexit
from typing import Any, Dict, List, Optional
from datetime import datetime, date

from .db import get_connection, execute_query, to_json_safe, get_available_run_dates
from .config import (
    HIERARCHY, ANALYSES_BY_LEVEL, ACTUALS_TABLE, RUN_DATE_COLUMN,
    MAX_CUSTOMERS_PER_FEATURE,
)
from .fiscal import get_fiscal_dates, FiscalDates
from .filters import build_actuals_filter
from .analyses import (
    get_summary_kpis,
    get_monthly_trends,
    get_children_breakdown,
    get_top20_vs_longtail,
    get_industry_performance,
    get_new_vs_existing,
    get_top_gainers,
    get_top_contractors,
    get_concentration_trend,
    get_top_customers,
    get_top_customer_gainers,
    get_top_customer_contractors,
    get_plan_variance_by_segment,
)


# =============================================================================
# LOCK FILE TO PREVENT DUPLICATE RUNS
# =============================================================================

LOCK_FILE = '/tmp/l1_commentary_collector.lock'
_lock_fd = None

def acquire_lock() -> bool:
    """Try to acquire exclusive lock. Returns False if already running."""
    global _lock_fd
    try:
        _lock_fd = open(LOCK_FILE, 'w')
        fcntl.flock(_lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        _lock_fd.write(str(datetime.now()))
        _lock_fd.flush()
        return True
    except (IOError, OSError):
        if _lock_fd:
            _lock_fd.close()
            _lock_fd = None
        return False

def release_lock():
    """Release the lock."""
    global _lock_fd
    if _lock_fd:
        try:
            fcntl.flock(_lock_fd.fileno(), fcntl.LOCK_UN)
            _lock_fd.close()
        except:
            pass
        _lock_fd = None
        try:
            os.remove(LOCK_FILE)
        except:
            pass

atexit.register(release_lock)


# =============================================================================
# ANALYSIS DISPATCHER
# =============================================================================

def collect_analyses_for_level(
    conn,
    dates: FiscalDates,
    run_date: date,
    level: str,
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Collect all appropriate analyses for a given hierarchy level.
    
    Uses ANALYSES_BY_LEVEL config to determine which analyses to run.
    Returns a dict with analysis name as key and results as value.
    """
    analyses_to_run = ANALYSES_BY_LEVEL.get(level, [])
    results = {}
    
    for analysis_name in analyses_to_run:
        try:
            if analysis_name == "summary_kpis":
                results[analysis_name] = get_summary_kpis(
                    conn, dates, run_date, category, use_case, feature, customer
                )
            elif analysis_name == "monthly_trends":
                results[analysis_name] = get_monthly_trends(
                    conn, dates, run_date, category, use_case, feature, customer
                )
            elif analysis_name == "children_breakdown":
                results[analysis_name] = get_children_breakdown(
                    conn, dates, run_date, level, category, use_case, feature, customer
                )
            elif analysis_name == "top20_vs_longtail":
                results[analysis_name] = get_top20_vs_longtail(
                    conn, dates, run_date, level, category, use_case, feature, customer
                )
            elif analysis_name == "industry_performance":
                results[analysis_name] = get_industry_performance(
                    conn, dates, run_date, category, use_case, feature, customer
                )
            elif analysis_name == "new_vs_existing":
                results[analysis_name] = get_new_vs_existing(
                    conn, dates, run_date, category, use_case, feature, customer
                )
            elif analysis_name == "top_gainers":
                results[analysis_name] = get_top_gainers(
                    conn, dates, run_date, level, category, use_case, feature, customer
                )
            elif analysis_name == "top_contractors":
                results[analysis_name] = get_top_contractors(
                    conn, dates, run_date, level, category, use_case, feature, customer
                )
            elif analysis_name == "concentration_trend":
                results[analysis_name] = get_concentration_trend(
                    conn, dates, run_date, category, use_case, feature, customer
                )
            elif analysis_name == "top_customers":
                results[analysis_name] = get_top_customers(
                    conn, dates, run_date, category, use_case, feature, customer
                )
            elif analysis_name == "top_customer_gainers":
                results[analysis_name] = get_top_customer_gainers(
                    conn, dates, run_date, category, use_case, feature, customer
                )
            elif analysis_name == "top_customer_contractors":
                results[analysis_name] = get_top_customer_contractors(
                    conn, dates, run_date, category, use_case, feature, customer
                )
            elif analysis_name == "plan_variance_by_segment":
                results[analysis_name] = get_plan_variance_by_segment(
                    conn, dates, run_date, level, category, use_case, feature, customer
                )
        except Exception as e:
            print(f"    WARNING: {analysis_name} failed: {e}")
            results[analysis_name] = [] if analysis_name != "summary_kpis" else {}
    
    return results


# =============================================================================
# HIERARCHY NAVIGATION
# =============================================================================

def get_categories(conn, dates: FiscalDates, run_date: date) -> List[str]:
    """Get all product categories with revenue in the quarter."""
    query = f"""
    SELECT DISTINCT product_category
    FROM {ACTUALS_TABLE}
    WHERE {RUN_DATE_COLUMN} = '{run_date}'
        AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
        AND product_category IS NOT NULL
    ORDER BY 1
    """
    results = execute_query(conn, query, "Get categories")
    return [r['product_category'] for r in results]


def get_use_cases(conn, dates: FiscalDates, run_date: date, category: str) -> List[str]:
    """Get use cases for a category."""
    query = f"""
    SELECT DISTINCT use_case
    FROM {ACTUALS_TABLE}
    WHERE {RUN_DATE_COLUMN} = '{run_date}'
        AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
        AND product_category = '{category}'
        AND use_case IS NOT NULL
    ORDER BY 1
    """
    results = execute_query(conn, query, f"Get use cases for {category}")
    return [r['use_case'] for r in results]


def get_features(conn, dates: FiscalDates, run_date: date, category: str, use_case: str) -> List[str]:
    """Get features for a use case."""
    from .db import safe_string
    query = f"""
    SELECT DISTINCT feature
    FROM {ACTUALS_TABLE}
    WHERE {RUN_DATE_COLUMN} = '{run_date}'
        AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
        AND product_category = '{safe_string(category)}'
        AND use_case = '{safe_string(use_case)}'
        AND feature IS NOT NULL
    ORDER BY 1
    """
    results = execute_query(conn, query, f"Get features for {use_case}")
    return [r['feature'] for r in results]


def get_feature_customers(
    conn, 
    dates: FiscalDates,
    run_date: date,
    category: str, 
    use_case: str, 
    feature: str,
    limit: int = MAX_CUSTOMERS_PER_FEATURE,
) -> List[str]:
    """Get top customers by revenue for a specific feature (for hierarchy traversal)."""
    from .db import safe_string
    query = f"""
    SELECT 
        latest_salesforce_account_name AS customer, 
        SUM(revenue + product_led_revenue) AS revenue
    FROM {ACTUALS_TABLE}
    WHERE {RUN_DATE_COLUMN} = '{run_date}'
        AND ds BETWEEN '{dates.q_start}' AND '{dates.effective_end}'
        AND product_category = '{safe_string(category)}'
        AND use_case = '{safe_string(use_case)}'
        AND feature = '{safe_string(feature)}'
        AND latest_salesforce_account_name IS NOT NULL
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT {limit}
    """
    results = execute_query(conn, query, f"Get customers for {feature}")
    return [r['customer'] for r in results]


# =============================================================================
# MAIN COLLECTION FUNCTION
# =============================================================================

def collect_all_data(
    fiscal_quarter: str,
    output_path: str,
    run_date: Optional[date] = None,
    filter_category: Optional[str] = None,
    max_customers: int = MAX_CUSTOMERS_PER_FEATURE,
) -> Dict[str, Any]:
    """
    Collect hierarchical L1 commentary data for a fiscal quarter.
    
    Traverses the full hierarchy: Total -> Categories -> Use Cases -> Features
    Collects appropriate analyses at each level based on ANALYSES_BY_LEVEL config.
    
    Args:
        fiscal_quarter: e.g., 'FY2026-Q4'
        output_path: Path to save JSON output
        run_date: Snapshot date to use (defaults to latest)
        filter_category: Optional single category to process
        max_customers: Max customers to collect per feature
    
    Returns:
        The collected data dictionary
    """
    if not acquire_lock():
        print("ERROR: Another collection is already running. Aborting to prevent corruption.")
        return {}
    
    try:
        return _collect_all_data_impl(
            fiscal_quarter, output_path, run_date, filter_category, max_customers
        )
    finally:
        release_lock()


def _collect_all_data_impl(
    fiscal_quarter: str,
    output_path: str,
    run_date: Optional[date] = None,
    filter_category: Optional[str] = None,
    max_customers: int = MAX_CUSTOMERS_PER_FEATURE,
) -> Dict[str, Any]:
    """Internal implementation of collect_all_data."""
    print(f"Connecting to Snowflake...")
    conn = get_connection()
    
    # Get run_date if not provided
    if run_date is None:
        available_dates = get_available_run_dates(conn)
        if not available_dates:
            print("ERROR: No snapshot dates found in actuals table")
            conn.close()
            return {}
        run_date = available_dates[0]
        print(f"Using latest snapshot: {run_date}")
    else:
        print(f"Using snapshot: {run_date}")
    
    print(f"Getting fiscal dates for {fiscal_quarter}...")
    dates = get_fiscal_dates(conn, fiscal_quarter)
    if not dates:
        print(f"ERROR: Could not find fiscal dates for {fiscal_quarter}")
        conn.close()
        return {}
    
    print(dates)
    print()
    
    # Collect TOTAL level
    print("Collecting TOTAL level analysis...")
    total_analysis = collect_analyses_for_level(conn, dates, run_date, 'total')
    
    # Get categories to process
    all_categories = get_categories(conn, dates, run_date)
    if filter_category:
        categories = [c for c in all_categories if c == filter_category]
        if not categories:
            print(f"WARNING: Category '{filter_category}' not found.")
            print(f"Available: {all_categories}")
            categories = all_categories
    else:
        categories = all_categories
    
    print(f"\nProcessing {len(categories)} categories...")
    
    hierarchy = {}
    
    for cat in categories:
        print(f"\n📁 {cat}")
        
        cat_data = {
            'name': cat,
            'level': 'category',
            'analysis': collect_analyses_for_level(conn, dates, run_date, 'category', category=cat),
            'children': {},
        }
        
        use_cases = get_use_cases(conn, dates, run_date, cat)
        print(f"   {len(use_cases)} use cases")
        
        for uc in use_cases:
            print(f"   📂 {uc}")
            
            uc_data = {
                'name': uc,
                'level': 'use_case',
                'analysis': collect_analyses_for_level(conn, dates, run_date, 'use_case', category=cat, use_case=uc),
                'children': {},
            }
            
            features = get_features(conn, dates, run_date, cat, uc)
            
            for feat in features:
                print(f"      🔧 {feat}")
                
                feat_data = {
                    'name': feat,
                    'level': 'feature',
                    'analysis': collect_analyses_for_level(
                        conn, dates, run_date, 'feature', 
                        category=cat, use_case=uc, feature=feat
                    ),
                    'children': {},
                }
                
                uc_data['children'][feat] = feat_data
            
            cat_data['children'][uc] = uc_data
        
        hierarchy[cat] = cat_data
    
    conn.close()
    
    # Build output structure
    data = to_json_safe({
        'metadata': {
            'fiscal_quarter': fiscal_quarter,
            'run_date': str(run_date),
            'q_start': str(dates.q_start),
            'q_end': str(dates.q_end),
            'effective_end': str(dates.effective_end),
            'pq_start': str(dates.pq_start),
            'pq_end': str(dates.pq_end),
            'py_start': str(dates.py_start),
            'py_end': str(dates.py_end),
            'generated_at': datetime.now().isoformat(),
            'version': 'v6',
        },
        'total': {
            'name': 'All Categories',
            'level': 'total',
            'analysis': total_analysis,
        },
        'hierarchy': hierarchy,
    })
    
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n✅ Data saved to {output_path}")
    
    return data
