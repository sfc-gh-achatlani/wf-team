#!/usr/bin/env python3
"""
Weekly Product Category Report Generator

USAGE:
    python run_report.py --week-end YYYY-MM-DD

EXAMPLE:
    python run_report.py --week-end 2026-01-19

The --week-end parameter is REQUIRED and must be a Sunday.
"""
import os
import sys
import argparse
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from scripts.collect_weekly_data import collect_all_data
from scripts.generate_html_report import generate_report

def main():
    parser = argparse.ArgumentParser(description='Generate Weekly Product Category Report')
    parser.add_argument('--week-end', required=True, help='Week ending date (Sunday, YYYY-MM-DD)')
    args = parser.parse_args()
    
    week_end = args.week_end
    week_end_dt = datetime.strptime(week_end, '%Y-%m-%d')
    week_start = (week_end_dt - timedelta(days=6)).strftime('%Y-%m-%d')
    
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    data_file = os.path.join(output_dir, f'data_{week_end}.json')
    html_file = os.path.join(output_dir, f'report_{week_end}.html')
    
    print(f"Week: {week_start} to {week_end}")
    
    print("Collecting data...")
    collect_all_data(week_start, week_end, data_file)
    
    print("Generating HTML...")
    generate_report(data_file, html_file, week_start, week_end)
    
    print(f"Done: {html_file}")
    return html_file

if __name__ == '__main__':
    main()
