#!/usr/bin/env python3
"""
generate_html_report.py - Generate interactive HTML report for weekly metrics
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader


def load_data(data_path: str) -> dict:
    """Load query results from JSON file."""
    with open(data_path, "r") as f:
        return json.load(f)


def calculate_totals(data: dict) -> dict:
    """Calculate executive summary totals."""
    category_wow = data.get("category_wow", [])
    qtd_vs_plan = data.get("qtd_vs_plan", [])
    
    total_current = sum(row.get("current_rev", 0) for row in category_wow)
    total_prior = sum(row.get("prior_rev", 0) for row in category_wow)
    total_wow_change = total_current - total_prior
    total_wow_pct = (total_wow_change / total_prior * 100) if total_prior else 0
    
    total_qtd_actual = sum(row.get("qtd_actual", 0) for row in qtd_vs_plan)
    total_qtd_plan = sum(row.get("qtd_plan", 0) for row in qtd_vs_plan)
    total_qtd_variance = sum(row.get("delta_to_plan", 0) for row in qtd_vs_plan)
    total_qtd_pct = (total_qtd_variance / total_qtd_plan * 100) if total_qtd_plan else 0
    
    categories_beating_plan = sum(1 for row in qtd_vs_plan if row.get("delta_to_plan", 0) >= 0)
    
    top_mover = max(category_wow, key=lambda x: abs(x.get("dollar_change", 0)), default={})
    
    return {
        "total_current": total_current,
        "total_prior": total_prior,
        "total_wow_change": total_wow_change,
        "total_wow_pct": total_wow_pct,
        "total_qtd_actual": total_qtd_actual,
        "total_qtd_plan": total_qtd_plan,
        "total_qtd_variance": total_qtd_variance,
        "total_qtd_pct": total_qtd_pct,
        "categories_beating_plan": categories_beating_plan,
        "total_categories": len(qtd_vs_plan),
        "top_mover_category": top_mover.get("product_category", "N/A"),
        "top_mover_change": top_mover.get("dollar_change", 0),
    }


def prepare_chart_data(data: dict) -> dict:
    """Prepare data for Chart.js visualizations."""
    category_wow = data.get("category_wow", [])
    qtd_vs_plan = data.get("qtd_vs_plan", [])
    forecast_evolution = data.get("forecast_evolution", [])
    
    category_labels = [row.get("product_category", "") for row in category_wow]
    current_values = [row.get("current_rev", 0) for row in category_wow]
    prior_values = [row.get("prior_rev", 0) for row in category_wow]
    
    qtd_labels = [row.get("product_category", "") for row in qtd_vs_plan]
    qtd_variance_values = [row.get("delta_to_plan", 0) for row in qtd_vs_plan]
    qtd_variance_colors = [
        "rgba(16, 185, 129, 0.8)" if v >= 0 else "rgba(239, 68, 68, 0.8)"
        for v in qtd_variance_values
    ]
    
    forecast_dates = sorted(set(row.get("run_date", "") for row in forecast_evolution))
    forecast_categories = sorted(set(row.get("product_category", "") for row in forecast_evolution))
    
    forecast_by_cat = {}
    for cat in forecast_categories:
        cat_data = [r for r in forecast_evolution if r.get("product_category") == cat]
        forecast_by_cat[cat] = {str(r.get("run_date", "")): r.get("yoy_growth_pct", 0) for r in cat_data}
    
    forecast_datasets = []
    colors = {
        'Total': '#1f77b4',
        'Data Engineering': '#ff7f0e', 
        'Analytics': '#2ca02c',
        'Platform': '#d62728',
        'AI/ML': '#9467bd',
        'Applications & Collaboration': '#8c564b'
    }
    for cat in forecast_categories:
        dataset_data = [forecast_by_cat[cat].get(str(d), None) for d in forecast_dates]
        forecast_datasets.append({
            'label': cat,
            'data': dataset_data,
            'borderColor': colors.get(cat, '#999999'),
            'tension': 0.1,
            'fill': False
        })
    
    return {
        "category_labels": category_labels,
        "current_values": current_values,
        "prior_values": prior_values,
        "qtd_labels": qtd_labels,
        "qtd_variance_values": qtd_variance_values,
        "qtd_variance_colors": qtd_variance_colors,
        "forecast_dates": [str(d) for d in forecast_dates],
        "forecast_datasets": forecast_datasets,
    }


def build_hierarchical_data(data: dict) -> list:
    """Build hierarchical structure: Category -> Use Cases -> Features -> Customers."""
    category_wow = data.get("category_wow", [])
    qtd_vs_plan = data.get("qtd_vs_plan", [])
    
    use_cases_dict = data.get("use_cases", {})
    features_dict = data.get("features", {})
    customers_dict = data.get("customers", {})
    
    qtd_by_cat = {row["product_category"]: {'delta': row.get("delta_to_plan", 0), 'pct': row.get("pct_variance", 0)} for row in qtd_vs_plan}
    
    total_wow_magnitude = sum(abs(row.get("dollar_change", 0)) for row in category_wow)
    
    categories = []
    for row in category_wow:
        cat_name = row["product_category"]
        cat_wow_change = row.get("dollar_change", 0)
        cat_growth_contribution = (abs(cat_wow_change) / total_wow_magnitude * 100) if total_wow_magnitude else 0
        
        feat_by_uc = defaultdict(list)
        for feat in features_dict.get(cat_name, []):
            uc = feat.get("use_case", "Unknown")
            feat_by_uc[uc].append(feat)
        
        cust_by_feat = defaultdict(list)
        for cust in customers_dict.get(cat_name, []):
            feat = cust.get("feature", "Unknown")
            cust_by_feat[feat].append(cust)
        
        use_cases_list = []
        for uc_data in use_cases_dict.get(cat_name, []):
            uc_name = uc_data["use_case"]
            
            features_list = []
            for feat_data in feat_by_uc.get(uc_name, []):
                feat_name = feat_data.get("feature", "Unknown")
                customers = cust_by_feat.get(feat_name, [])[:10]
                feat_copy = dict(feat_data)
                feat_copy["customers"] = customers
                features_list.append(feat_copy)
            
            uc_copy = dict(uc_data)
            uc_copy["features"] = features_list
            use_cases_list.append(uc_copy)
        
        categories.append({
            "name": cat_name,
            "current_rev": row.get("current_rev", 0),
            "prior_rev": row.get("prior_rev", 0),
            "wow_change": row.get("dollar_change", 0),
            "pct_change": row.get("pct_change", 0),
            "mix_pct": row.get("mix_pct", 0),
            "growth_contribution": cat_growth_contribution,
            "qtd_delta": qtd_by_cat.get(cat_name, {}).get('delta', 0),
            "qtd_pct": qtd_by_cat.get(cat_name, {}).get('pct', 0),
            "use_cases": use_cases_list,
        })
    
    return categories


ACCOUNT_CONTEXT = {
    "Merkle, Inc.": "Monthly rekey process causing expected spike; uses Snowpark.",

    "Advisor360": "Unplanned cost spike from data masking implementation for Infosec compliance.",
    "EDO": "One-time backfill error; confirmed anomaly, not expected to recur.",
    "Vertex, Inc.": "Internal data sharing architecture; developer accidentally upsized warehouse from L to 3XL.",
    "NielsenIQ": "Optimization from migrating back to ARM32 warehouses; expect $360-400K monthly savings going forward.",
    "Komodo Health": "Product rearchitecture affecting ~900 managed accounts; slowdown in new customer onboarding.",
    "Coupang Corp. [Blue Team]": "Security breach response; scheduled tasks caused temporary spike, returning to steady state.",
    "Coupang Corp.": "Security breach response; scheduled tasks caused temporary spike, returning to steady state.",
    "Southern California Edison Company": "Developing high-performance Power Flow Analysis solution in Snowflake for grid capacity analysis and simulation. Replacing costly third-party implementations with pure Python alternative. Goes live in September.",
    "Marriott International, Inc.": "Spike from batch jobs and metadata overhead; transitioning from Iceberg to direct Snowflake queries.",
    "E.ON Digital Technology GmbH": "Business continuity/failover strategy implementation; growing data replication costs.",
    "Exaforce": "Large customer onboarding spike; awaiting detailed context from customer.",
    "Freshworks, Inc.": "Churning to Databricks due to cost; migration spike ahead of January contract expiration.",
    "CTC Trading Group LLC": "Optimizing to fit 3-year contract; shifting workloads to externally managed Iceberg.",
    "ServiceTitan": "Accidental spike from warehouse left running 25 hours without timeout.",
}


def generate_report(data_path_or_dict, output_path: str, week_start: str, week_end: str):
    """Generate HTML report from data file or dict."""
    if isinstance(data_path_or_dict, str):
        data = load_data(data_path_or_dict)
    else:
        data = data_path_or_dict
    
    script_dir = Path(__file__).parent.parent
    assets_dir = script_dir / "assets"
    
    env = Environment(loader=FileSystemLoader(str(assets_dir)))
    template = env.get_template("report_template.html")
    
    totals = calculate_totals(data)
    chart_data = prepare_chart_data(data)
    categories = build_hierarchical_data(data)
    
    context = {
        "week_start": week_start,
        "week_end": week_end,
        "prior_week_end": data.get("metadata", {}).get("prior_week_end", ""),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category_wow": data.get("category_wow", []),
        "qtd_vs_plan": data.get("qtd_vs_plan", []),
        "categories": categories,
        "top_gainers": data.get("top_gainers", []),
        "top_contractors": data.get("top_contractors", []),
        "customer_features": data.get("customer_features", {}),
        "fq_forecast": data.get("fq_forecast", []),
        "top_25_customers": data.get("top_25_customers", []),
        "account_context": ACCOUNT_CONTEXT,
        **totals,
        **chart_data,
    }
    
    html_content = template.render(**context)
    
    with open(output_path, "w") as f:
        f.write(html_content)
    
    print(f"Report generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate HTML weekly metrics report")
    parser.add_argument("--data", required=True, help="Path to JSON data file")
    parser.add_argument("--output", required=True, help="Output HTML file path")
    parser.add_argument("--week-start", required=True, help="Current week start date")
    parser.add_argument("--week-end", required=True, help="Current week end date")
    args = parser.parse_args()
    
    data = load_data(args.data)
    generate_report(data, args.output, args.week_start, args.week_end)


if __name__ == "__main__":
    main()
