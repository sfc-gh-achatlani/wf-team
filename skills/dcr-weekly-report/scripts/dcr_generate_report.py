#!/usr/bin/env python3
"""
dcr_generate_report.py - Generate interactive HTML report for DCR weekly metrics
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def load_data(data_path: str) -> dict:
    with open(data_path, "r") as f:
        return json.load(f)


def prepare_chart_data(data: dict) -> dict:
    daily_revenue = data.get("daily_revenue", [])
    
    # Filter to only include rows where 7-day avg exists (skip first 6 days)
    daily_revenue_filtered = [r for r in daily_revenue if r.get("revenue_7day_avg") is not None]
    
    revenue_dates = [str(r.get("ds", ""))[:10] for r in daily_revenue_filtered]
    revenue_values = [r.get("revenue", 0) for r in daily_revenue_filtered]
    revenue_7day_avg = [r.get("revenue_7day_avg") for r in daily_revenue_filtered]
    
    dau_wau_mau_customers = data.get("dau_wau_mau_customers", [])
    dau_dates_customers = [str(r.get("ds", ""))[:10] for r in dau_wau_mau_customers]
    dau_values_customers = [r.get("daily", 0) for r in dau_wau_mau_customers]
    wau_values_customers = [r.get("last_7_days") for r in dau_wau_mau_customers]
    mau_values_customers = [r.get("last_28_days") for r in dau_wau_mau_customers]
    
    dau_wau_mau_all = data.get("dau_wau_mau_all", [])
    dau_dates_all = [str(r.get("ds", ""))[:10] for r in dau_wau_mau_all]
    dau_values_all = [r.get("daily", 0) for r in dau_wau_mau_all]
    wau_values_all = [r.get("last_7_days") for r in dau_wau_mau_all]
    mau_values_all = [r.get("last_28_days") for r in dau_wau_mau_all]
    
    credits_daily = data.get("credits_daily", [])
    credits_dates = [str(r.get("ds", ""))[:10] for r in credits_daily]
    credits_values = [r.get("credits", 0) for r in credits_daily]
    credits_7day_avg = [r.get("last_7_moving_avg") for r in credits_daily]
    
    return {
        "revenue_dates": revenue_dates,
        "revenue_values": revenue_values,
        "revenue_7day_avg": revenue_7day_avg,
        "dau_dates_customers": dau_dates_customers,
        "dau_values_customers": dau_values_customers,
        "wau_values_customers": wau_values_customers,
        "mau_values_customers": mau_values_customers,
        "dau_dates_all": dau_dates_all,
        "dau_values_all": dau_values_all,
        "wau_values_all": wau_values_all,
        "mau_values_all": mau_values_all,
        "credits_dates": credits_dates,
        "credits_values": credits_values,
        "credits_7day_avg": credits_7day_avg,
    }


def generate_report(data_path: str, output_path: str):
    data = load_data(data_path)
    metadata = data.get("metadata", {})
    
    script_dir = Path(__file__).parent.parent
    assets_dir = script_dir / "assets"
    
    env = Environment(loader=FileSystemLoader(str(assets_dir)))
    template = env.get_template("dcr_report_template.html")
    
    chart_data = prepare_chart_data(data)
    
    dcr_revenue_wow = data.get("dcr_revenue_wow", {})
    dcr_qtd = data.get("dcr_qtd", {})
    
    class DictWithDefaults(dict):
        def __getattr__(self, name):
            return self.get(name, 0)
    
    context = {
        "week_start": metadata.get("current_week_start", ""),
        "week_end": metadata.get("current_week_end", ""),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dcr_revenue_wow": DictWithDefaults(dcr_revenue_wow),
        "dcr_qtd": DictWithDefaults(dcr_qtd),
        "dau_wau_mau_customers": data.get("dau_wau_mau_customers", []),
        "dau_wau_mau_all": data.get("dau_wau_mau_all", []),
        "credits_daily": data.get("credits_daily", []),
        "credits_by_source": data.get("credits_by_source", []),
        "partner_edges": data.get("partner_edges", []),
        "top_customers_credits": data.get("top_customers_credits", []),
        "top_customers_revenue": data.get("top_customers_revenue", []),
        "job_buckets": data.get("job_buckets", []),
        "account_cohorts": DictWithDefaults(data.get("account_cohorts", {})),
        "weekly_revenue_table": data.get("weekly_revenue_table", []),
        **chart_data,
    }
    
    html_content = template.render(**context)
    
    with open(output_path, "w") as f:
        f.write(html_content)
    
    print(f"Report generated: {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to JSON data file")
    parser.add_argument("--output", required=True, help="Output HTML file path")
    args = parser.parse_args()
    
    generate_report(args.data, args.output)


if __name__ == "__main__":
    main()
