"""
scripts/__init__.py - L1 Commentary Scripts Package

This package provides hierarchical financial analysis for product categories.

STRUCTURE:
    config.py    - Configuration constants and hierarchy definition
    db.py        - Database connection and query utilities
    fiscal.py    - Fiscal calendar date calculations
    filters.py   - SQL filter clause builders
    analyses.py  - Individual analysis functions
    collector.py - Main data collection orchestrator
    reporter.py  - HTML/Markdown report generation

USAGE:
    from scripts.collector import collect_all_data
    from scripts.reporter import generate_report
    
    collect_all_data('FY2026-Q4', 'output/data.json')
    generate_report('output/data.json', 'output/report.html', 'output/report.md')
"""

from .collector import collect_all_data
from .reporter import generate_report

__all__ = ['collect_all_data', 'generate_report']
