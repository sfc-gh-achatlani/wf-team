"""
L1 Commentary - Streamlit Application

Interactive quarterly financial analysis report with:
- Drill-down page navigation (Total -> Category -> Use Case -> Feature)
- KPI cards grid for quick comparison
- Local JSON caching for fast re-access
"""

import os
import json
import fcntl
import streamlit as st
from datetime import date, datetime
from typing import Dict, Any, Optional, List

# Add scripts to path
import sys
sys.path.insert(0, os.path.dirname(__file__))

from scripts.db import get_connection, get_available_run_dates
from scripts.fiscal import get_fiscal_dates
from scripts.collector import collect_all_data

# Page config
st.set_page_config(
    page_title="L1 Commentary",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# CACHING
# =============================================================================

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_path(fiscal_quarter: str, run_date: date, category: Optional[str] = None) -> str:
    """Generate cache file path."""
    cat_suffix = f"_{category.replace('/', '_').replace(' ', '_')}" if category else "_all"
    return os.path.join(CACHE_DIR, f"l1_{fiscal_quarter}_{run_date}{cat_suffix}.json")


def load_from_cache(cache_path: str) -> Optional[Dict]:
    """Load data from cache if exists."""
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)
    return None


def save_to_cache(data: Dict, cache_path: str) -> None:
    """Save data to cache with file locking to prevent corruption."""
    temp_path = cache_path + '.tmp'
    with open(temp_path, 'w') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    os.rename(temp_path, cache_path)


# =============================================================================
# DATA LOADING
# =============================================================================

@st.cache_data(ttl=3600)
def get_run_dates() -> List[date]:
    """Get available snapshot dates."""
    conn = get_connection()
    dates = get_available_run_dates(conn)
    conn.close()
    return dates


@st.cache_data(ttl=3600)
def get_fiscal_quarters() -> List[str]:
    """Get available fiscal quarters."""
    return [
        "FY2026-Q4",
        "FY2026-Q3",
        "FY2026-Q2",
        "FY2026-Q1",
        "FY2025-Q4",
        "FY2025-Q3",
    ]


def load_data(fiscal_quarter: str, run_date: date, category: Optional[str] = None) -> Dict:
    """Load data from cache or generate."""
    cache_path = get_cache_path(fiscal_quarter, run_date, category)
    
    cached = load_from_cache(cache_path)
    if cached:
        return cached
    
    data = collect_all_data(
        fiscal_quarter=fiscal_quarter,
        output_path=None,
        run_date=run_date,
        filter_category=category if category != "All" else None,
    )
    
    if data:
        save_to_cache(data, cache_path)
    
    return data


# =============================================================================
# FORMATTERS
# =============================================================================

def format_currency(value) -> str:
    """Format number as currency."""
    if value is None:
        return "-"
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:,.1f}M"
    elif abs(value) >= 1_000:
        return f"${value/1_000:,.1f}K"
    return f"${value:,.0f}"


def format_pct(value) -> str:
    """Format growth rate as percentage with +/- sign."""
    if value is None:
        return "-"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f}%"


def format_share(value) -> str:
    """Format proportion/share as percentage (no sign)."""
    if value is None:
        return "-"
    return f"{value:.1f}%"


def format_int(value) -> str:
    """Format integer with commas."""
    if value is None:
        return "-"
    return f"{int(value):,}"


def format_delta(value) -> str:
    """Format delta with sign."""
    if value is None:
        return "-"
    sign = "+" if value > 0 else ""
    return f"{sign}{format_currency(value)}"


# Column name mappings for display
COLUMN_NAMES = {
    'customer': 'Customer',
    'entity': 'Name',
    'industry': 'Industry',
    'segment': 'Segment',
    'customer_type': 'Type',
    'existing_segment': 'Segment',
    'month': 'Month',
    'day': 'Date',
    'qtd_revenue': 'Q4 Revenue',
    'prior_q_revenue': 'Q3 Revenue',
    'qoq_delta': 'QoQ $',
    'qoq_growth_pct': 'QoQ %',
    'contribution_to_growth_pct': 'QoQ Contrib %',
    'qtd_plan': 'Q4 Plan',
    'vs_plan': 'vs Plan $',
    'delta_to_plan': 'vs Plan $',
    'vs_plan_pct': 'vs Plan %',
    'pct_vs_plan': 'vs Plan %',
    'variance_magnitude_pct': 'Plan Contrib %',
    'prior_year_revenue': 'FY25 Q4',
    'yoy_delta': 'YoY $',
    'yoy_growth_pct': 'YoY %',
    'yoy_contribution_to_growth_pct': 'YoY Contrib %',
    'mix_pct': 'Mix %',
    'revenue_share_pct': 'Mix %',
    'current_quarter_revenue': 'Q4 Revenue',
    'prior_quarter_revenue': 'Q3 Revenue',
    'delta': 'Change $',
    'contribution_to_decline_pct': 'Decline Contrib %',
    'customer_count': 'Customers',
    'revenue': 'Daily Revenue',
    'plan_revenue': 'Daily Plan',
    'cumulative_revenue': 'Cumul. Revenue',
    'cumulative_plan': 'Cumul. Plan',
    'mom_delta': 'MoM $',
    'mom_pct': 'MoM %',
    'in_quarter': 'In Quarter',
    'contribution_pct': 'Contrib %',
}

# Columns that should use format_currency
CURRENCY_COLS = {
    'qtd_revenue', 'prior_q_revenue', 'prior_year_revenue', 'qtd_plan',
    'vs_plan', 'qoq_delta', 'current_quarter_revenue', 'prior_quarter_revenue',
    'delta', 'delta_to_plan', 'revenue', 'plan_revenue', 'mom_delta', 'yoy_delta',
    'cumulative_revenue', 'cumulative_plan',
}

# Columns that should use format_pct (growth rates with +/-)
GROWTH_PCT_COLS = {
    'vs_plan_pct', 'pct_vs_plan', 'qoq_growth_pct', 'yoy_growth_pct', 'mom_pct',
}

# Columns that should use format_share (proportions, no sign)
SHARE_PCT_COLS = {
    'revenue_share_pct', 'contribution_to_growth_pct', 'contribution_pct',
    'mix_pct', 'variance_magnitude_pct', 'revenue_pct',
    'yoy_contribution_to_growth_pct', 'contribution_to_decline_pct',
}

# Columns that should use format_int
INT_COLS = {'customer_count'}


def format_dataframe(df):
    """Format DataFrame columns and rename headers."""
    import pandas as pd
    
    display_df = df.copy()
    
    # Format values
    for col in display_df.columns:
        if col in CURRENCY_COLS:
            display_df[col] = display_df[col].apply(lambda x: format_currency(x) if pd.notna(x) else "-")
        elif col in GROWTH_PCT_COLS:
            display_df[col] = display_df[col].apply(lambda x: format_pct(x) if pd.notna(x) else "-")
        elif col in SHARE_PCT_COLS:
            display_df[col] = display_df[col].apply(lambda x: format_share(x) if pd.notna(x) else "-")
        elif col in INT_COLS:
            display_df[col] = display_df[col].apply(lambda x: format_int(x) if pd.notna(x) else "-")
    
    # Rename columns
    display_df.columns = [COLUMN_NAMES.get(c, c) for c in display_df.columns]
    
    return display_df


# =============================================================================
# NAVIGATION
# =============================================================================

def get_current_entity(data: Dict, nav_path: List[str]) -> tuple[Dict, str]:
    """Navigate to current entity based on path. Returns (entity, level)."""
    if not nav_path:
        return data.get('total', {}), 'total'
    
    # Start from hierarchy
    current = data.get('hierarchy', {})
    
    # Navigate down the path
    for i, step in enumerate(nav_path):
        if step in current:
            entity = current[step]
            current = entity.get('children', {})
        else:
            return data.get('total', {}), 'total'
    
    return entity, entity.get('level', 'unknown')


def get_children(data: Dict, nav_path: List[str]) -> Dict:
    """Get children of current entity."""
    if not nav_path:
        return data.get('hierarchy', {})
    
    entity, _ = get_current_entity(data, nav_path)
    return entity.get('children', {})


def render_breadcrumbs(nav_path: List[str]):
    """Render clickable breadcrumb navigation."""
    st.markdown("##### " + " → ".join(["📊 Total"] + [f"📁 {p}" for p in nav_path]))
    
    # Navigation buttons
    if nav_path:
        cols = st.columns(len(nav_path) + 1)
        
        # Total button
        with cols[0]:
            if st.button("← Total", key="bread_total"):
                st.session_state.nav_path = []
                st.rerun()
        
        # Intermediate path buttons
        for i, part in enumerate(nav_path[:-1]):
            with cols[i + 1]:
                if st.button(f"← {part}", key=f"bread_{i}"):
                    st.session_state.nav_path = nav_path[:i + 1]
                    st.rerun()
    
    st.markdown("---")


# =============================================================================
# KPI CARDS
# =============================================================================

def render_kpi_header(kpis: Dict, name: str = ""):
    """Render main KPI metrics row."""
    if not kpis:
        return
    
    st.subheader(name if name else "Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(
        "QTD Revenue",
        format_currency(kpis.get('qtd_revenue')),
        format_delta(kpis.get('delta_to_plan')),
    )
    col2.metric(
        "vs Plan",
        format_pct(kpis.get('pct_vs_plan')),
    )
    col3.metric(
        "QoQ Growth",
        format_pct(kpis.get('qoq_growth_pct')),
    )
    col4.metric(
        "YoY Growth",
        format_pct(kpis.get('yoy_growth_pct')),
    )


def render_children_cards(children: Dict, current_level: str):
    """Render clickable KPI cards for each child."""
    if not children:
        return
    
    level_labels = {
        'total': 'Categories',
        'category': 'Use Cases',
        'use_case': 'Features',
        'feature': 'Details',
    }
    
    st.subheader(level_labels.get(current_level, 'Breakdown'))
    
    items = list(children.items())
    clicked_name = None
    
    # 3 cards per row
    for row_start in range(0, len(items), 3):
        cols = st.columns(3)
        for col_idx, (name, child_data) in enumerate(items[row_start:row_start+3]):
            kpis = child_data.get('analysis', {}).get('summary_kpis', {})
            has_children = bool(child_data.get('children'))
            
            with cols[col_idx]:
                with st.container(border=True):
                    icon = "📁" if has_children else "🔧"
                    if st.button(f"{icon} {name}", key=f"card_{name}", use_container_width=True, type="primary"):
                        clicked_name = name
                    
                    # Revenue and vs Plan
                    c1, c2 = st.columns(2)
                    c1.metric("Revenue", format_currency(kpis.get('qtd_revenue')))
                    c2.metric("vs Plan", format_pct(kpis.get('pct_vs_plan')))
                    
                    # Growth metrics
                    c3, c4 = st.columns(2)
                    c3.metric("QoQ", format_pct(kpis.get('qoq_growth_pct')))
                    c4.metric("YoY", format_pct(kpis.get('yoy_growth_pct')))
    
    # Handle navigation after all cards rendered
    if clicked_name:
        st.session_state.nav_path.append(clicked_name)
        st.rerun()


# =============================================================================
# DETAIL VIEWS
# =============================================================================

def render_monthly_trends(trends: List[Dict]):
    """Render daily trends chart for current quarter."""
    if not trends:
        st.info("No trend data available")
        return
    
    import pandas as pd
    
    df = pd.DataFrame(trends)
    if 'day' in df.columns:
        df['day'] = pd.to_datetime(df['day'])
        df = df.set_index('day')
        
        if 'cumulative_revenue' in df.columns and 'cumulative_plan' in df.columns:
            chart_data = df[['cumulative_revenue', 'cumulative_plan']].copy()
            chart_data.columns = ['Actual (Cumul.)', 'Plan (Cumul.)']
            st.line_chart(chart_data, use_container_width=True)
    elif 'month' in df.columns:
        df['month'] = pd.to_datetime(df['month'])
        df = df.set_index('month')
        if 'revenue' in df.columns:
            chart_data = df[['revenue']].copy()
            if 'plan_revenue' in df.columns:
                chart_data['plan_revenue'] = df['plan_revenue']
            st.line_chart(chart_data, use_container_width=True)
    
    with st.expander("View Details"):
        display_df = format_dataframe(df.reset_index())
        st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_plan_variance_chart(data: List[Dict], child_type: str):
    """Render plan variance by child entity, split by Top 20 vs Long Tail."""
    if not data:
        st.info("No variance data available")
        return
    
    import pandas as pd
    import altair as alt
    
    df = pd.DataFrame(data)
    
    # Pivot to get Top 20 and Long Tail as separate columns per entity
    chart_df = df.pivot(index='entity', columns='segment', values='variance').reset_index()
    chart_df = chart_df.fillna(0)
    
    # Melt for Altair grouped bar chart
    melted = df[['entity', 'segment', 'variance']].copy()
    melted['variance_m'] = melted['variance'] / 1_000_000  # Convert to millions
    
    # Create grouped bar chart
    chart = alt.Chart(melted).mark_bar().encode(
        x=alt.X('entity:N', title=child_type, sort='-y', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('variance_m:Q', title='vs Plan ($M)'),
        color=alt.Color('segment:N', 
                       scale=alt.Scale(domain=['Top 20', 'Long Tail'], range=['#1f77b4', '#ff7f0e']),
                       title='Customer Segment'),
        xOffset='segment:N',
        tooltip=[
            alt.Tooltip('entity:N', title=child_type),
            alt.Tooltip('segment:N', title='Segment'),
            alt.Tooltip('variance:Q', title='vs Plan $', format='$,.0f')
        ]
    ).properties(
        height=350
    )
    
    # Add zero line
    rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(strokeDash=[3, 3], color='gray').encode(y='y:Q')
    
    st.altair_chart(chart + rule, use_container_width=True)
    
    with st.expander("View Details"):
        display_df = df.copy()
        display_df['variance'] = display_df['variance'].apply(lambda x: format_currency(x) if pd.notna(x) else "-")
        display_df['actual_revenue'] = display_df['actual_revenue'].apply(lambda x: format_currency(x) if pd.notna(x) else "-")
        display_df['plan_revenue'] = display_df['plan_revenue'].apply(lambda x: format_currency(x) if pd.notna(x) else "-")
        display_df.columns = [child_type, 'Segment', 'Actual', 'Plan', 'vs Plan']
        st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_top_customers(customers: List[Dict]):
    """Render top customers table."""
    if not customers:
        st.info("No customer data available")
        return
    
    import pandas as pd
    df = pd.DataFrame(customers)
    st.dataframe(format_dataframe(df), use_container_width=True, hide_index=True)


def render_customer_movers(gainers: List[Dict], contractors: List[Dict]):
    """Render customer gainers and contractors side by side."""
    import pandas as pd
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top Gainers**")
        if gainers:
            df = pd.DataFrame(gainers)
            st.dataframe(format_dataframe(df), use_container_width=True, hide_index=True)
        else:
            st.info("No data")
    
    with col2:
        st.markdown("**Top Contractors**")
        if contractors:
            df = pd.DataFrame(contractors)
            st.dataframe(format_dataframe(df), use_container_width=True, hide_index=True)
        else:
            st.info("No data")


def render_industry_performance(data: List[Dict]):
    """Render industry performance table."""
    if not data:
        st.info("No industry data available")
        return
    
    import pandas as pd
    df = pd.DataFrame(data)
    st.dataframe(format_dataframe(df), use_container_width=True, hide_index=True)


def render_children_breakdown(children: List[Dict], child_type: str = "Entity"):
    """Render children breakdown table."""
    if not children:
        return
    
    import pandas as pd
    df = pd.DataFrame(children)
    st.dataframe(format_dataframe(df), use_container_width=True, hide_index=True)


def render_detail_tabs(analysis: Dict, level: str):
    """Render all analysis sections in two-column layout."""
    if not analysis:
        return
    
    import pandas as pd
    
    child_type = {
        'total': 'Category',
        'category': 'Use Case',
        'use_case': 'Feature',
        'feature': 'Customer',
    }.get(level, 'Child')
    
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.markdown("### Daily Trends (Q4)")
        render_monthly_trends(analysis.get('monthly_trends', []))
        
        st.markdown("---")
        st.markdown(f"### {child_type} Plan Variance by Customer Segment")
        render_plan_variance_chart(analysis.get('plan_variance_by_segment', []), child_type)
        
        st.markdown("---")
        st.markdown(f"### {child_type} Breakdown")
        breakdown = analysis.get('children_breakdown', [])
        if breakdown and len(breakdown) < 100:
            render_children_breakdown(breakdown, child_type)
        elif breakdown:
            with st.expander(f"View all {len(breakdown)} items"):
                render_children_breakdown(breakdown, child_type)
        
        st.markdown("---")
        st.markdown("### Industry Performance")
        render_industry_performance(analysis.get('industry_performance', []))
    
    with right_col:
        st.markdown("### Top Customers")
        render_top_customers(analysis.get('top_customers', []))
        
        st.markdown("---")
        st.markdown("### Top Gainers")
        gainers = analysis.get('top_customer_gainers', [])
        if gainers:
            df = pd.DataFrame(gainers)
            st.dataframe(format_dataframe(df), use_container_width=True, hide_index=True)
        else:
            st.info("No data")
        
        st.markdown("---")
        st.markdown("### Top Contractors")
        contractors = analysis.get('top_customer_contractors', [])
        if contractors:
            df = pd.DataFrame(contractors)
            st.dataframe(format_dataframe(df), use_container_width=True, hide_index=True)
        else:
            st.info("No data")
        
        st.markdown("---")
        st.markdown("### Revenue Concentration")
        st.caption("*Capacity customers only (excludes On Demand)*")
        top20 = analysis.get('top20_vs_longtail', [])
        if top20:
            df = pd.DataFrame(top20)
            st.dataframe(format_dataframe(df), use_container_width=True, hide_index=True)
        
        new_existing = analysis.get('new_vs_existing', [])
        if new_existing:
            st.markdown("**New vs Existing**")
            df = pd.DataFrame(new_existing)
            st.dataframe(format_dataframe(df), use_container_width=True, hide_index=True)


# =============================================================================
# MAIN APP
# =============================================================================

def main():
    st.title("L1 Commentary Report")
    
    # Initialize session state
    if 'report_data' not in st.session_state:
        st.session_state.report_data = None
        st.session_state.report_params = None
    
    if 'nav_path' not in st.session_state:
        st.session_state.nav_path = []
    
    # Check if we already have data
    has_data = st.session_state.report_data is not None
    
    # Sidebar
    with st.sidebar:
        st.header("Report Settings")
        
        # Get available dates
        try:
            run_dates = get_run_dates()
            if not run_dates:
                st.error("No snapshot dates found")
                return
        except Exception as e:
            st.error(f"Connection error: {e}")
            return
        
        # Snapshot date selector
        run_date = st.selectbox(
            "Snapshot Date",
            options=run_dates,
            format_func=lambda x: str(x),
            help="Select which data snapshot to analyze"
        )
        
        # Fiscal quarter selector
        fiscal_quarter = st.selectbox(
            "Fiscal Quarter",
            options=get_fiscal_quarters(),
            help="Select the fiscal quarter to analyze"
        )
        
        st.markdown("---")
        
        # Generate button
        if st.button("Generate Report", type="primary", use_container_width=True):
            with st.spinner("Loading..."):
                data = load_data(fiscal_quarter, run_date, None)
                if data:
                    st.session_state.report_data = data
                    st.session_state.report_params = {
                        'fiscal_quarter': fiscal_quarter,
                        'run_date': run_date,
                    }
                    st.session_state.nav_path = []
                    st.rerun()
        
        # Cache info
        cache_path = get_cache_path(fiscal_quarter, run_date, None)
        if os.path.exists(cache_path):
            st.success("📦 Cached data available")
        else:
            st.info("🔄 Will fetch fresh data")
        
        # Clear/reset buttons
        if has_data:
            st.markdown("---")
            if st.session_state.nav_path:
                if st.button("↩ Back to Total", use_container_width=True):
                    st.session_state.nav_path = []
                    st.rerun()
            
            if st.button("Clear Report", use_container_width=True):
                st.session_state.report_data = None
                st.session_state.report_params = None
                st.session_state.nav_path = []
                st.rerun()
    
    # Display report
    if st.session_state.report_data is not None:
        data = st.session_state.report_data
        params = st.session_state.report_params
        
        # Header
        st.caption(f"{params['fiscal_quarter']} | Snapshot: {params['run_date']}")
        
        # Breadcrumb navigation
        render_breadcrumbs(st.session_state.nav_path)
        
        # Get current entity
        entity, level = get_current_entity(data, st.session_state.nav_path)
        analysis = entity.get('analysis', {})
        
        # Entity KPIs
        entity_name = entity.get('name', 'Total')
        render_kpi_header(analysis.get('summary_kpis', {}), entity_name)
        
        st.markdown("---")
        
        # Children cards
        children = get_children(data, st.session_state.nav_path)
        if children:
            render_children_cards(children, level)
            st.markdown("---")
        
        # Detail tabs
        render_detail_tabs(analysis, level)
    
    else:
        st.info("👈 Select options and click 'Generate Report' to begin")


if __name__ == "__main__":
    main()
