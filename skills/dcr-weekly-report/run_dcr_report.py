#!/usr/bin/env python3
"""
run_dcr_report.py - Main entry point for DCR weekly report generation.

Usage:
    SNOWFLAKE_CONNECTION_NAME=<your_connection> uv run python run_dcr_report.py --week-end 2026-01-25
"""

import argparse
from datetime import datetime
from pathlib import Path

from scripts.dcr_collect_data import main as collect_main
from scripts.dcr_generate_report import generate_report


class CollectArgs:
    def __init__(self, week_end, output):
        self.week_end = week_end
        self.output = output


def main():
    parser = argparse.ArgumentParser(description="Generate DCR weekly HTML report")
    parser.add_argument("--week-end", required=True, help="Week end date (YYYY-MM-DD, Sunday)")
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent
    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    data_path = output_dir / f"dcr_data_{args.week_end}.json"
    html_path = output_dir / f"dcr_report_{args.week_end}.html"
    
    print(f"\n{'='*60}")
    print(f"DCR Weekly Report Generator")
    print(f"Week End: {args.week_end}")
    print(f"{'='*60}\n")
    
    print("Step 1: Collecting data from Snowflake...")
    collect_args = CollectArgs(args.week_end, str(data_path))
    collect_main(collect_args)
    
    print("\nStep 2: Generating HTML report...")
    generate_report(str(data_path), str(html_path))
    
    print(f"\n{'='*60}")
    print(f"✅ Report complete!")
    print(f"   Data: {data_path}")
    print(f"   HTML: {html_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
