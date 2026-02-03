"""
config.py - Configuration and Constants for L1 Commentary

This file centralizes all configuration to make the tool:
1. Easy to modify for different quarters/thresholds
2. Self-documenting for team members
3. Consistent across all modules
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

# =============================================================================
# DATA SOURCES
# =============================================================================

ACTUALS_TABLE = "finance.customer.product_category_revenue_snapshot"
RUN_DATE_COLUMN = "run_date"
PLAN_TABLE = "finance.dev_sensitive.achatlani_nov_plan_final"
CALENDAR_TABLE = "finance.stg_utils.stg_fiscal_calendar"

# =============================================================================
# COLUMN MAPPINGS
# =============================================================================

# Actuals table columns
ACTUALS_COLUMNS = {
    "date": "ds",
    "run_date": "run_date",
    "category": "product_category",
    "use_case": "use_case",
    "feature": "feature",
    "customer": "latest_salesforce_account_name",
    "industry": "industry_rollup",
    "revenue": "revenue",
    "product_led_revenue": "product_led_revenue",
}

# Plan table columns (has customer data!)
PLAN_COLUMNS = {
    "date": "ds",
    "category": "product_category",
    "use_case": "use_case",
    "feature": "feature",
    "customer": "salesforce_account_name",
    "revenue": "revenue",
}

# =============================================================================
# HIERARCHY DEFINITION
# =============================================================================

@dataclass
class HierarchyLevel:
    """Defines a level in the drill-down hierarchy."""
    name: str
    display_name: str
    column: str
    child_level: Optional[str]
    has_plan_data: bool
    icon: str
    color: str

HIERARCHY: Dict[str, HierarchyLevel] = {
    "total": HierarchyLevel(
        name="total",
        display_name="Total",
        column=None,
        child_level="category",
        has_plan_data=True,
        icon="🌐",
        color="#1a1a2e",
    ),
    "category": HierarchyLevel(
        name="category",
        display_name="Category",
        column="product_category",
        child_level="use_case",
        has_plan_data=True,
        icon="📁",
        color="#16213e",
    ),
    "use_case": HierarchyLevel(
        name="use_case",
        display_name="Use Case",
        column="use_case",
        child_level="feature",
        has_plan_data=True,
        icon="📂",
        color="#0f3460",
    ),
    "feature": HierarchyLevel(
        name="feature",
        display_name="Feature",
        column="feature",
        child_level="customer",
        has_plan_data=True,
        icon="🔧",
        color="#1a508b",
    ),
    "customer": HierarchyLevel(
        name="customer",
        display_name="Customer",
        column="latest_salesforce_account_name",
        child_level=None,
        has_plan_data=True,  # New plan table has customer data!
        icon="👤",
        color="#2d6a9f",
    ),
}

# =============================================================================
# ANALYSIS CONFIGURATION
# =============================================================================

# Which analyses to run at each level
# Customer level gets reduced set because:
#   - No plan data exists
#   - Concentration/Top20 don't make sense for single entity
ANALYSES_BY_LEVEL: Dict[str, List[str]] = {
    "total": [
        "summary_kpis",
        "monthly_trends",
        "children_breakdown",
        "plan_variance_by_segment",
        "top20_vs_longtail",
        "new_vs_existing",
        "top_customers",
        "top_customer_gainers",
        "top_customer_contractors",
        "industry_performance",
        "concentration_trend",
    ],
    "category": [
        "summary_kpis",
        "monthly_trends",
        "children_breakdown",
        "plan_variance_by_segment",
        "top20_vs_longtail",
        "new_vs_existing",
        "top_customers",
        "top_customer_gainers",
        "top_customer_contractors",
        "industry_performance",
        "concentration_trend",
    ],
    "use_case": [
        "summary_kpis",
        "monthly_trends",
        "children_breakdown",
        "plan_variance_by_segment",
        "top20_vs_longtail",
        "new_vs_existing",
        "top_customers",
        "top_customer_gainers",
        "top_customer_contractors",
        "industry_performance",
        "concentration_trend",
    ],
    "feature": [
        "summary_kpis",
        "monthly_trends",
        "children_breakdown",
        "top20_vs_longtail",
        "new_vs_existing",
        "top_customers",
        "top_customer_gainers",
        "top_customer_contractors",
        "industry_performance",
        "concentration_trend",
    ],
}

# =============================================================================
# THRESHOLDS AND LIMITS
# =============================================================================

# Customer segmentation thresholds
GROWTH_THRESHOLD = 0.05      # >+5% QoQ = GROWING
SHRINK_THRESHOLD = -0.05     # <-5% QoQ = SHRINKING

# Query limits
MAX_CUSTOMERS_PER_FEATURE = 0  # No customer drill-down
MAX_GAINERS = 5
MAX_CONTRACTORS = 5
MAX_INDUSTRIES = 10
MAX_TOP_CUSTOMERS = 10
EXTENDED_TREND_MONTHS = 3  # Months before quarter to show in trends

# =============================================================================
# DISPLAY CONFIGURATION
# =============================================================================

CUSTOMER_SEGMENTS = {
    "NEW": {"badge_class": "new", "description": "No revenue prior quarter"},
    "EXISTING-GROWING": {"badge_class": "growing", "description": f"QoQ > +{GROWTH_THRESHOLD*100:.0f}%"},
    "EXISTING-STAGNANT": {"badge_class": "stagnant", "description": f"QoQ between {SHRINK_THRESHOLD*100:.0f}% and +{GROWTH_THRESHOLD*100:.0f}%"},
    "EXISTING-SHRINKING": {"badge_class": "shrinking", "description": f"QoQ < {SHRINK_THRESHOLD*100:.0f}%"},
    "CHURNED": {"badge_class": "churned", "description": "No revenue current quarter"},
}
