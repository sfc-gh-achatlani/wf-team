"""
reporter.py - HTML and Markdown Report Generator

Generates interactive HTML reports with click-to-expand hierarchy
and summary Markdown reports from collected L1 data.
"""

import json
from typing import Any, Dict, List, Optional

from .config import HIERARCHY, ANALYSES_BY_LEVEL, CUSTOMER_SEGMENTS


# =============================================================================
# FORMATTING UTILITIES
# =============================================================================

def format_currency(value: Any) -> str:
    """Format a number as currency (e.g., $1.2M, $500K, $100)."""
    if value is None:
        return "N/A"
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "N/A"
    
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:.0f}"


def format_pct(value: Any) -> str:
    """Format a number as percentage with sign."""
    if value is None:
        return "N/A"
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "N/A"
    
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f}%"


def get_perf_class(value: Any) -> str:
    """Get CSS class based on performance (positive/negative/neutral)."""
    if value is None:
        return ""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ""
    
    if value > 2:
        return "positive"
    elif value < -2:
        return "negative"
    return "neutral"


def safe_id(name: str) -> str:
    """Convert a name to a safe HTML ID."""
    if not name:
        return "unknown"
    return (
        name.replace(" ", "-")
        .replace("/", "-")
        .replace("&", "and")
        .replace("'", "")
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
    )


# =============================================================================
# ANALYSIS SECTION RENDERERS
# =============================================================================

def render_kpis(analysis: Dict) -> str:
    """Render the KPI summary row."""
    kpis = analysis.get('summary_kpis', {})
    
    return f'''
    <div class="kpi-row">
        <div class="kpi">
            <span class="kpi-label">QTD Revenue</span>
            <span class="kpi-value">{format_currency(kpis.get('qtd_revenue'))}</span>
        </div>
        <div class="kpi">
            <span class="kpi-label">vs Plan</span>
            <span class="kpi-value {get_perf_class(kpis.get('pct_vs_plan'))}">
                {format_currency(kpis.get('delta_to_plan'))} ({format_pct(kpis.get('pct_vs_plan'))})
            </span>
        </div>
        <div class="kpi">
            <span class="kpi-label">YoY</span>
            <span class="kpi-value {get_perf_class(kpis.get('yoy_growth_pct'))}">
                {format_pct(kpis.get('yoy_growth_pct'))}
            </span>
        </div>
        <div class="kpi">
            <span class="kpi-label">QoQ</span>
            <span class="kpi-value {get_perf_class(kpis.get('qoq_growth_pct'))}">
                {format_pct(kpis.get('qoq_growth_pct'))}
            </span>
        </div>
    </div>
    '''


def render_monthly_trends(data: List[Dict]) -> str:
    """Render monthly trends table with extended history."""
    if not data:
        return ""
    
    rows = ""
    for m in data:
        month_str = str(m.get('month', ''))[:7] if m.get('month') else 'N/A'
        in_q = m.get('in_quarter', False)
        row_class = 'in-quarter' if in_q else 'pre-quarter'
        q_marker = '●' if in_q else '○'
        
        plan_cell = ""
        vs_plan_cell = ""
        if in_q and m.get('plan_revenue'):
            plan_cell = f"<td>{format_currency(m.get('plan_revenue'))}</td>"
            vs_plan_cell = f'<td class="{get_perf_class(m.get("vs_plan_pct"))}">{format_pct(m.get("vs_plan_pct"))}</td>'
        elif in_q:
            plan_cell = "<td>-</td>"
            vs_plan_cell = "<td>-</td>"
        else:
            plan_cell = "<td class='pre-quarter-cell'>-</td>"
            vs_plan_cell = "<td class='pre-quarter-cell'>-</td>"
        
        rows += f'''
        <tr class="{row_class}">
            <td><span class="q-marker">{q_marker}</span> {month_str}</td>
            <td>{format_currency(m.get('revenue'))}</td>
            {plan_cell}
            {vs_plan_cell}
            <td class="{get_perf_class(m.get('mom_pct'))}">{format_pct(m.get('mom_pct'))}</td>
        </tr>
        '''
    
    return f'''
    <div class="analysis-card">
        <h4>📈 Monthly Trends (Extended)</h4>
        <p style="font-size: 11px; color: #64748b; margin-bottom: 8px;">● In-Quarter | ○ Prior Months</p>
        <table class="mini-table">
            <thead><tr><th>Month</th><th>Actuals</th><th>Plan</th><th>vs Plan</th><th>MoM %</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    '''


def render_top20_vs_longtail(data: List[Dict]) -> str:
    """Render Top 20 Customers vs Long Tail analysis."""
    if not data:
        return ""
    
    rows = ""
    for seg in data:
        rows += f'''
        <tr>
            <td><strong>{seg.get('segment', 'N/A')}</strong></td>
            <td>{seg.get('customer_count', 0):,}</td>
            <td>{format_currency(seg.get('current_quarter_revenue'))}</td>
            <td class="{get_perf_class(seg.get('qoq_growth_pct'))}">{format_pct(seg.get('qoq_growth_pct'))}</td>
            <td>{format_pct(seg.get('revenue_share_pct'))}</td>
        </tr>
        '''
    
    return f'''
    <div class="analysis-card">
        <h4>🎯 Top 20 Customers vs Long Tail</h4>
        <table class="mini-table">
            <thead><tr><th>Segment</th><th>Customers</th><th>Revenue</th><th>QoQ %</th><th>Share %</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    '''


def render_new_vs_existing(data: List[Dict]) -> str:
    """Render New vs Existing customer segmentation."""
    if not data:
        return ""
    
    # Aggregate by segment
    segments = {}
    for row in data:
        ctype = row.get('customer_type', 'UNKNOWN')
        seg = row.get('existing_segment')
        key = f"{ctype}-{seg}" if seg else ctype
        
        if key not in segments:
            segments[key] = {'count': 0, 'cq_rev': 0, 'delta': 0}
        segments[key]['count'] += row.get('customer_count', 0) or 0
        segments[key]['cq_rev'] += row.get('current_quarter_revenue', 0) or 0
        segments[key]['delta'] += row.get('delta', 0) or 0
    
    rows = ""
    for seg_key in ['NEW', 'EXISTING-GROWING', 'EXISTING-STAGNANT', 'EXISTING-SHRINKING', 'CHURNED']:
        if seg_key in segments:
            s = segments[seg_key]
            badge_class = seg_key.lower().replace('existing-', '')
            rows += f'''
            <tr>
                <td><span class="badge {badge_class}">{seg_key}</span></td>
                <td>{s['count']:,}</td>
                <td>{format_currency(s['cq_rev'])}</td>
                <td class="{get_perf_class(s['delta'])}">{format_currency(s['delta'])}</td>
            </tr>
            '''
    
    return f'''
    <div class="analysis-card">
        <h4>🔄 New vs Existing</h4>
        <table class="mini-table">
            <thead><tr><th>Segment</th><th>Customers</th><th>Revenue</th><th>Delta</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    '''


def render_industry_performance(data: List[Dict]) -> str:
    """Render industry performance breakdown."""
    if not data:
        return ""
    
    rows = ""
    for ind in data[:8]:
        rows += f'''
        <tr>
            <td>{ind.get('industry', 'N/A')}</td>
            <td>{format_currency(ind.get('qtd_revenue'))}</td>
            <td class="{get_perf_class(ind.get('qoq_growth_pct'))}">{format_pct(ind.get('qoq_growth_pct'))}</td>
            <td class="{get_perf_class(ind.get('yoy_growth_pct'))}">{format_pct(ind.get('yoy_growth_pct'))}</td>
            <td>{format_pct(ind.get('revenue_share_pct'))}</td>
        </tr>
        '''
    
    return f'''
    <div class="analysis-card">
        <h4>🏢 Industry Performance</h4>
        <table class="mini-table">
            <thead><tr><th>Industry</th><th>Revenue</th><th>QoQ %</th><th>YoY %</th><th>Share %</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    '''


def render_top_movers(data: List[Dict], title: str, icon: str, is_positive: bool) -> str:
    """Render top gainers or contractors table (for child entities)."""
    if not data:
        return ""
    
    perf_class = "positive" if is_positive else "negative"
    rows = ""
    for item in data[:5]:
        rows += f'''
        <tr>
            <td title="{item.get('entity', 'N/A')}">{str(item.get('entity', 'N/A'))[:30]}</td>
            <td>{format_currency(item.get('current_quarter_revenue'))}</td>
            <td class="{perf_class}">{format_currency(item.get('delta'))}</td>
            <td class="{perf_class}">{format_pct(item.get('qoq_growth_pct'))}</td>
            <td>{format_pct(item.get('contribution_pct'))}</td>
        </tr>
        '''
    
    return f'''
    <div class="analysis-card">
        <h4>{icon} {title}</h4>
        <table class="mini-table">
            <thead><tr><th>Entity</th><th>Revenue</th><th>Delta</th><th>QoQ %</th><th>Contrib %</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    '''


def render_top_customers(data: List[Dict]) -> str:
    """Render top customers by revenue."""
    if not data:
        return ""
    
    rows = ""
    for cust in data[:10]:
        rows += f'''
        <tr>
            <td title="{cust.get('customer', 'N/A')}">{str(cust.get('customer', 'N/A'))[:35]}</td>
            <td>{format_currency(cust.get('qtd_revenue'))}</td>
            <td>{format_currency(cust.get('qtd_plan'))}</td>
            <td class="{get_perf_class(cust.get('vs_plan_pct'))}">{format_pct(cust.get('vs_plan_pct'))}</td>
            <td class="{get_perf_class(cust.get('qoq_growth_pct'))}">{format_pct(cust.get('qoq_growth_pct'))}</td>
            <td>{format_pct(cust.get('revenue_share_pct'))}</td>
        </tr>
        '''
    
    return f'''
    <div class="analysis-card full-width">
        <h4>👥 Top Customers</h4>
        <table class="mini-table">
            <thead><tr><th>Customer</th><th>Revenue</th><th>Plan</th><th>vs Plan</th><th>QoQ %</th><th>Share %</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    '''


def render_customer_movers(data: List[Dict], title: str, icon: str, is_positive: bool) -> str:
    """Render top customer gainers or contractors."""
    if not data:
        return ""
    
    perf_class = "positive" if is_positive else "negative"
    contrib_label = "contribution_to_growth_pct" if is_positive else "contribution_to_decline_pct"
    
    rows = ""
    for cust in data[:5]:
        rows += f'''
        <tr>
            <td title="{cust.get('customer', 'N/A')}">{str(cust.get('customer', 'N/A'))[:35]}</td>
            <td>{format_currency(cust.get('current_quarter_revenue'))}</td>
            <td class="{perf_class}">{format_currency(cust.get('delta'))}</td>
            <td class="{perf_class}">{format_pct(cust.get('qoq_growth_pct'))}</td>
            <td>{format_pct(cust.get(contrib_label))}</td>
        </tr>
        '''
    
    return f'''
    <div class="analysis-card">
        <h4>{icon} {title}</h4>
        <table class="mini-table">
            <thead><tr><th>Customer</th><th>Revenue</th><th>Delta</th><th>QoQ %</th><th>Contrib %</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    '''


def render_concentration_trend(data: List[Dict]) -> str:
    """Render concentration trend over months."""
    if not data:
        return ""
    
    rows = ""
    for c in data:
        month_str = str(c.get('month', ''))[:7] if c.get('month') else 'N/A'
        rows += f'''
        <tr>
            <td>{month_str}</td>
            <td>{format_pct(c.get('top10_pct'))}</td>
            <td>{format_pct(c.get('top20_pct'))}</td>
        </tr>
        '''
    
    return f'''
    <div class="analysis-card">
        <h4>📊 Concentration Trend</h4>
        <table class="mini-table">
            <thead><tr><th>Month</th><th>Top 10 %</th><th>Top 20 %</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    '''


def render_children_breakdown(data: List[Dict]) -> str:
    """Render children breakdown table."""
    if not data:
        return ""
    
    rows = ""
    for child in data[:15]:
        rows += f'''
        <tr>
            <td title="{child.get('entity', 'N/A')}">{str(child.get('entity', 'N/A'))[:25]}</td>
            <td>{format_currency(child.get('qtd_revenue'))}</td>
            <td>{format_currency(child.get('qtd_plan'))}</td>
            <td class="{get_perf_class(child.get('pct_vs_plan'))}">{format_pct(child.get('pct_vs_plan'))}</td>
            <td class="{get_perf_class(child.get('qoq_growth_pct'))}">{format_pct(child.get('qoq_growth_pct'))}</td>
            <td>{format_pct(child.get('mix_pct'))}</td>
        </tr>
        '''
    
    return f'''
    <div class="analysis-card full-width">
        <h4>📋 Breakdown</h4>
        <table class="mini-table">
            <thead><tr><th>Entity</th><th>Revenue</th><th>Plan</th><th>vs Plan</th><th>QoQ %</th><th>Mix %</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    '''


# =============================================================================
# ENTITY RENDERER
# =============================================================================

def render_analysis_section(analysis: Dict, level: str) -> str:
    """Render all analyses for an entity based on its level.
    
    Section order:
    1. KPIs (always first)
    2. Monthly Trends (time context)
    3. Children Breakdown (hierarchy overview)
    4. Customer Segmentation (Top 20 vs Long Tail, New vs Existing)
    5. Customer Tables (Top Customers, Gainers, Contractors)
    6. Industry & Concentration
    """
    available_analyses = ANALYSES_BY_LEVEL.get(level, [])
    
    html = render_kpis(analysis)
    
    if 'monthly_trends' in available_analyses:
        html += render_monthly_trends(analysis.get('monthly_trends', []))
    
    if 'children_breakdown' in available_analyses:
        html += render_children_breakdown(analysis.get('children_breakdown', []))
    
    html += '<div class="analysis-grid">'
    
    if 'top20_vs_longtail' in available_analyses:
        html += render_top20_vs_longtail(analysis.get('top20_vs_longtail', []))
    
    if 'new_vs_existing' in available_analyses:
        html += render_new_vs_existing(analysis.get('new_vs_existing', []))
    
    html += '</div>'
    
    if 'top_customers' in available_analyses:
        html += render_top_customers(analysis.get('top_customers', []))
    
    html += '<div class="analysis-grid">'
    
    if 'top_customer_gainers' in available_analyses:
        html += render_customer_movers(
            analysis.get('top_customer_gainers', []),
            "Top Customer Gainers", "🚀", is_positive=True
        )
    
    if 'top_customer_contractors' in available_analyses:
        html += render_customer_movers(
            analysis.get('top_customer_contractors', []),
            "Top Customer Contractors", "⬇️", is_positive=False
        )
    
    html += '</div>'
    
    html += '<div class="analysis-grid">'
    
    if 'industry_performance' in available_analyses:
        html += render_industry_performance(analysis.get('industry_performance', []))
    
    if 'concentration_trend' in available_analyses:
        html += render_concentration_trend(analysis.get('concentration_trend', []))
    
    html += '</div>'
    
    return html


def render_entity(entity_data: Dict, depth: int = 0, parent_id: str = "") -> str:
    """Recursively render an entity and its children."""
    name = entity_data.get('name', 'Unknown')
    level = entity_data.get('level', 'unknown')
    analysis = entity_data.get('analysis', {})
    children = entity_data.get('children', {})
    
    entity_id = f"{parent_id}-{safe_id(name)}" if parent_id else safe_id(name)
    
    level_config = HIERARCHY.get(level, {})
    icon = getattr(level_config, 'icon', '📄') if level_config else '📄'
    color = getattr(level_config, 'color', '#333') if level_config else '#333'
    display_name = getattr(level_config, 'display_name', level.title()) if level_config else level.title()
    
    has_children = len(children) > 0
    kpis = analysis.get('summary_kpis', {})
    
    toggle_icon = '<span class="toggle-icon">▶</span>' if has_children else '<span class="toggle-icon empty"></span>'
    
    html = f'''
    <div class="entity level-{level}" data-depth="{depth}" id="entity-{entity_id}">
        <div class="entity-header" style="background: {color}; padding-left: {20 + depth * 20}px;" onclick="toggleEntity('{entity_id}')">
            <span class="entity-icon">{icon}</span>
            <span class="entity-name">{name}</span>
            <span class="entity-level">{display_name}</span>
            <span class="entity-kpi">{format_currency(kpis.get('qtd_revenue'))}</span>
            <span class="entity-delta {get_perf_class(kpis.get('pct_vs_plan'))}">{format_pct(kpis.get('pct_vs_plan'))} vs Plan</span>
            {toggle_icon}
        </div>
        <div class="entity-content" id="content-{entity_id}">
            <div class="analysis-container">
                {render_analysis_section(analysis, level)}
            </div>
    '''
    
    if has_children:
        html += f'<div class="entity-children" id="children-{entity_id}">'
        for child_name, child_data in children.items():
            html += render_entity(child_data, depth + 1, entity_id)
        html += '</div>'
    
    html += '</div></div>'
    return html


# =============================================================================
# MAIN REPORT GENERATORS
# =============================================================================

def get_html_styles() -> str:
    """Return CSS styles for the HTML report."""
    return '''
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; color: #1a1a2e; line-height: 1.5; }
        .container { max-width: 1600px; margin: 0 auto; padding: 16px; }
        
        header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 20px; }
        header h1 { font-size: 24px; font-weight: 600; }
        header .subtitle { opacity: 0.8; margin-top: 6px; font-size: 14px; }
        
        .entity { margin-bottom: 2px; }
        .entity-header { 
            display: flex; align-items: center; gap: 12px; padding: 12px 16px; 
            color: white; cursor: pointer; border-radius: 6px; transition: all 0.2s;
        }
        .entity-header:hover { filter: brightness(1.1); }
        .entity-icon { font-size: 18px; }
        .entity-name { font-weight: 600; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .entity-level { font-size: 11px; text-transform: uppercase; opacity: 0.7; padding: 2px 8px; background: rgba(255,255,255,0.15); border-radius: 4px; }
        .entity-kpi { font-weight: 600; min-width: 80px; text-align: right; }
        .entity-delta { font-size: 12px; min-width: 100px; text-align: right; }
        .toggle-icon { font-size: 12px; transition: transform 0.2s; width: 16px; text-align: center; }
        .toggle-icon.empty { visibility: hidden; }
        
        .entity-content { display: none; background: white; border-radius: 0 0 8px 8px; margin-bottom: 8px; }
        .entity.expanded > .entity-content { display: block; }
        .entity.expanded > .entity-header .toggle-icon { transform: rotate(90deg); }
        
        .entity-children { margin-left: 12px; border-left: 2px solid #e2e8f0; padding-left: 8px; }
        
        .analysis-container { padding: 16px; }
        .kpi-row { display: flex; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
        .kpi { background: #f8fafc; padding: 12px 16px; border-radius: 8px; min-width: 140px; }
        .kpi-label { display: block; font-size: 11px; text-transform: uppercase; color: #64748b; margin-bottom: 4px; }
        .kpi-value { font-size: 18px; font-weight: 600; }
        
        .analysis-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; }
        .analysis-card { background: #f8fafc; border-radius: 8px; padding: 12px; }
        .analysis-card.full-width { grid-column: 1 / -1; }
        .analysis-card h4 { font-size: 13px; font-weight: 600; margin-bottom: 10px; color: #334155; }
        
        .mini-table { width: 100%; border-collapse: collapse; font-size: 12px; }
        .mini-table th { text-align: left; padding: 6px 8px; background: #e2e8f0; font-weight: 600; color: #475569; }
        .mini-table td { padding: 6px 8px; border-bottom: 1px solid #e2e8f0; }
        .mini-table tr:hover { background: #f1f5f9; }
        .mini-table tr.pre-quarter { opacity: 0.6; }
        .mini-table tr.in-quarter { font-weight: 500; }
        .q-marker { font-size: 10px; margin-right: 4px; }
        
        .positive { color: #10b981; }
        .negative { color: #ef4444; }
        .neutral { color: #6b7280; }
        
        .badge { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 500; }
        .badge.new { background: #dbeafe; color: #1e40af; }
        .badge.growing { background: #d1fae5; color: #065f46; }
        .badge.stagnant { background: #f3f4f6; color: #4b5563; }
        .badge.shrinking { background: #fee2e2; color: #991b1b; }
        .badge.churned { background: #f3e8ff; color: #6b21a8; }
        
        .controls { margin-bottom: 16px; display: flex; gap: 8px; flex-wrap: wrap; }
        .controls button { padding: 8px 16px; border: 1px solid #e2e8f0; border-radius: 6px; background: white; cursor: pointer; font-size: 13px; }
        .controls button:hover { background: #f1f5f9; }
        
        .footer { text-align: center; padding: 20px; color: #94a3b8; font-size: 12px; margin-top: 20px; }
    </style>
    '''


def get_html_scripts() -> str:
    """Return JavaScript for the HTML report."""
    return '''
    <script>
        function toggleEntity(entityId) {
            const entity = document.getElementById('entity-' + entityId);
            entity.classList.toggle('expanded');
        }
        
        function expandAll() {
            document.querySelectorAll('.entity').forEach(e => e.classList.add('expanded'));
        }
        
        function collapseAll() {
            document.querySelectorAll('.entity').forEach(e => e.classList.remove('expanded'));
        }
        
        function expandToLevel(targetLevel) {
            const levels = ['total', 'category', 'use_case', 'feature'];
            const targetIndex = levels.indexOf(targetLevel);
            
            document.querySelectorAll('.entity').forEach(e => {
                const entityLevel = Array.from(e.classList).find(c => c.startsWith('level-'));
                if (entityLevel) {
                    const level = entityLevel.replace('level-', '');
                    const levelIndex = levels.indexOf(level);
                    if (levelIndex <= targetIndex) {
                        e.classList.add('expanded');
                    } else {
                        e.classList.remove('expanded');
                    }
                }
            });
        }
        
        // Auto-expand Total and Categories on load
        document.querySelectorAll('.level-total, .level-category').forEach(e => e.classList.add('expanded'));
    </script>
    '''


def generate_html_report(data: Dict, output_path: str) -> None:
    """Generate the interactive HTML report."""
    metadata = data['metadata']
    total = data.get('total', {})
    hierarchy = data.get('hierarchy', {})
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>L1 Commentary - {metadata['fiscal_quarter']}</title>
    {get_html_styles()}
</head>
<body>
    <div class="container">
        <header>
            <h1>L1 Commentary Report</h1>
            <div class="subtitle">
                {metadata['fiscal_quarter']} | 
                {metadata['q_start']} to {metadata['effective_end']} | 
                Generated {metadata['generated_at'][:10]}
            </div>
        </header>
        
        <div class="controls">
            <button onclick="expandAll()">Expand All</button>
            <button onclick="collapseAll()">Collapse All</button>
            <button onclick="expandToLevel('category')">Categories Only</button>
            <button onclick="expandToLevel('use_case')">+ Use Cases</button>
            <button onclick="expandToLevel('feature')">+ Features</button>
        </div>
        
        <div class="hierarchy">
            {render_entity(total, depth=0)}
'''
    
    for cat_name, cat_data in hierarchy.items():
        html += render_entity(cat_data, depth=0)
    
    html += f'''
        </div>
        
        <div class="footer">
            L1 Commentary v5 | Hierarchical Analysis | Snowflake Finance
        </div>
    </div>
    {get_html_scripts()}
</body>
</html>
'''
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"✅ HTML report saved to {output_path}")


def generate_markdown_report(data: Dict, output_path: str) -> None:
    """Generate the Markdown summary report."""
    metadata = data['metadata']
    total = data.get('total', {})
    hierarchy = data.get('hierarchy', {})
    
    total_kpis = total.get('analysis', {}).get('summary_kpis', {})
    
    md = f"""# L1 Commentary - {metadata['fiscal_quarter']}

**Period:** {metadata['q_start']} to {metadata['effective_end']}  
**Generated:** {metadata['generated_at'][:10]}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| QTD Revenue | {format_currency(total_kpis.get('qtd_revenue'))} |
| vs Plan | {format_currency(total_kpis.get('delta_to_plan'))} ({format_pct(total_kpis.get('pct_vs_plan'))}) |
| YoY Growth | {format_pct(total_kpis.get('yoy_growth_pct'))} |
| QoQ Growth | {format_pct(total_kpis.get('qoq_growth_pct'))} |

---

## Category Summary

"""
    
    for cat_name, cat_data in hierarchy.items():
        kpis = cat_data.get('analysis', {}).get('summary_kpis', {})
        md += f"""### {cat_name}

| Metric | Value |
|--------|-------|
| Revenue | {format_currency(kpis.get('qtd_revenue'))} |
| vs Plan | {format_pct(kpis.get('pct_vs_plan'))} |
| YoY | {format_pct(kpis.get('yoy_growth_pct'))} |
| QoQ | {format_pct(kpis.get('qoq_growth_pct'))} |

"""
        
        # Add use case summary
        children = cat_data.get('children', {})
        if children:
            md += "**Use Cases:**\n\n"
            for uc_name, uc_data in list(children.items())[:5]:
                uc_kpis = uc_data.get('analysis', {}).get('summary_kpis', {})
                md += f"- **{uc_name}**: {format_currency(uc_kpis.get('qtd_revenue'))} ({format_pct(uc_kpis.get('qoq_growth_pct'))} QoQ)\n"
            md += "\n"
        
        md += "---\n\n"
    
    with open(output_path, 'w') as f:
        f.write(md)
    
    print(f"✅ Markdown report saved to {output_path}")


def generate_report(data_path: str, html_path: str, md_path: str) -> None:
    """
    Generate both HTML and Markdown reports from collected data.
    
    Args:
        data_path: Path to the JSON data file
        html_path: Output path for HTML report
        md_path: Output path for Markdown report
    """
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    generate_html_report(data, html_path)
    generate_markdown_report(data, md_path)
