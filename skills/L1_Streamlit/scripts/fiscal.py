"""
fiscal.py - Fiscal Calendar Utilities

Handles fiscal quarter date calculations and provides consistent
date ranges for current quarter, prior quarter, and prior year comparisons.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from .db import execute_query
from .config import CALENDAR_TABLE


@dataclass
class FiscalDates:
    """
    Container for all date ranges needed for quarterly analysis.
    
    Attributes:
        q_start: First day of current quarter
        q_end: Last day of current quarter
        effective_end: Actual end date (today-2 if quarter in progress)
        pq_start: First day of prior quarter
        pq_end: Last day of prior quarter
        py_start: Same period last year start
        py_end: Same period last year end
    """
    q_start: date
    q_end: date
    effective_end: date
    pq_start: date
    pq_end: date
    py_start: date
    py_end: date
    
    def __str__(self) -> str:
        return (
            f"Current Q: {self.q_start} to {self.q_end} (effective: {self.effective_end})\n"
            f"Prior Q:   {self.pq_start} to {self.pq_end}\n"
            f"Prior Y:   {self.py_start} to {self.py_end}"
        )


def get_fiscal_dates(conn, fiscal_quarter: str) -> Optional[FiscalDates]:
    """
    Calculate all date ranges for a fiscal quarter.
    
    Args:
        conn: Snowflake connection
        fiscal_quarter: Quarter identifier (e.g., 'FY2026-Q4')
    
    Returns:
        FiscalDates object with all date ranges, or None if quarter not found.
    
    Example:
        >>> dates = get_fiscal_dates(conn, 'FY2026-Q4')
        >>> print(dates)
        Current Q: 2025-11-01 to 2026-01-31 (effective: 2026-01-31)
        Prior Q:   2025-08-01 to 2025-10-31
        Prior Y:   2024-11-01 to 2025-01-31
    """
    query = f"""
    WITH current_q AS (
        SELECT 
            MIN(_date) AS q_start, 
            MAX(_date) AS q_end
        FROM {CALENDAR_TABLE}
        WHERE fiscal_quarter_fyyyyy_qq = '{fiscal_quarter}'
    ),
    prior_q AS (
        SELECT 
            MIN(_date) AS pq_start, 
            MAX(_date) AS pq_end
        FROM {CALENDAR_TABLE}
        WHERE fiscal_quarter_fyyyyy_qq = (
            SELECT DISTINCT fiscal_quarter_fyyyyy_qq
            FROM {CALENDAR_TABLE}
            WHERE _date = DATEADD('month', -3, (SELECT q_start FROM current_q))
        )
    ),
    prior_year AS (
        SELECT 
            DATEADD('year', -1, (SELECT q_start FROM current_q)) AS py_start,
            DATEADD('year', -1, (SELECT q_end FROM current_q)) AS py_end
    )
    SELECT 
        cq.q_start, 
        cq.q_end,
        pq.pq_start, 
        pq.pq_end,
        py.py_start, 
        py.py_end,
        CASE 
            WHEN cq.q_end >= CURRENT_DATE() 
            THEN CURRENT_DATE() - 2 
            ELSE cq.q_end 
        END AS effective_end
    FROM current_q cq
    CROSS JOIN prior_q pq
    CROSS JOIN prior_year py
    """
    
    results = execute_query(conn, query, f"Get fiscal dates for {fiscal_quarter}")
    
    if not results:
        return None
    
    row = results[0]
    return FiscalDates(
        q_start=row['q_start'],
        q_end=row['q_end'],
        effective_end=row['effective_end'],
        pq_start=row['pq_start'],
        pq_end=row['pq_end'],
        py_start=row['py_start'],
        py_end=row['py_end'],
    )
