"""
filters.py - SQL Filter Building Utilities

Provides consistent filter clause generation for all hierarchy levels.
Handles the complexity of different column names between actuals and plan tables.
"""

from typing import Optional
from .db import safe_string
from .config import ACTUALS_COLUMNS, PLAN_COLUMNS


def build_actuals_filter(
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
) -> str:
    """
    Build a WHERE clause for the actuals table.
    
    Args:
        category: Filter by product_category
        use_case: Filter by use_case
        feature: Filter by feature
        customer: Filter by latest_salesforce_account_name
    
    Returns:
        SQL WHERE clause (without WHERE keyword), e.g.:
        "product_category = 'Analytics' AND use_case = 'BI'"
        Returns "1=1" if no filters provided.
    
    Example:
        >>> build_actuals_filter(category="Analytics", use_case="BI")
        "product_category = 'Analytics' AND use_case = 'BI'"
    """
    clauses = []
    
    if category:
        clauses.append(f"{ACTUALS_COLUMNS['category']} = '{safe_string(category)}'")
    if use_case:
        clauses.append(f"{ACTUALS_COLUMNS['use_case']} = '{safe_string(use_case)}'")
    if feature:
        clauses.append(f"{ACTUALS_COLUMNS['feature']} = '{safe_string(feature)}'")
    if customer:
        clauses.append(f"{ACTUALS_COLUMNS['customer']} = '{safe_string(customer)}'")
    
    return " AND ".join(clauses) if clauses else "1=1"


def build_plan_filter(
    category: Optional[str] = None,
    use_case: Optional[str] = None,
    feature: Optional[str] = None,
    customer: Optional[str] = None,
) -> str:
    """
    Build a WHERE clause for the plan table.
    
    Args:
        category: Filter by product_category
        use_case: Filter by use_case  
        feature: Filter by feature
        customer: Filter by salesforce_account_name
    
    Returns:
        SQL WHERE clause (without WHERE keyword).
        Returns "1=1" if no filters provided.
    """
    clauses = []
    
    if category:
        clauses.append(f"{PLAN_COLUMNS['category']} = '{safe_string(category)}'")
    if use_case:
        clauses.append(f"{PLAN_COLUMNS['use_case']} = '{safe_string(use_case)}'")
    if feature:
        clauses.append(f"{PLAN_COLUMNS['feature']} = '{safe_string(feature)}'")
    if customer:
        clauses.append(f"{PLAN_COLUMNS['customer']} = '{safe_string(customer)}'")
    
    return " AND ".join(clauses) if clauses else "1=1"
