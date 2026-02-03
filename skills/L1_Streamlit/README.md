# L1 Streamlit App

Interactive Streamlit dashboard for L1 financial commentary with quarterly revenue analysis.

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/sfc-gh-achatlani/wf-team.git
cd wf-team

# 2. Pull LFS files (required for cached data)
git lfs pull

# 3. Navigate to this skill
cd skills/L1_Streamlit

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the app
SNOWFLAKE_CONNECTION_NAME=snowhouse streamlit run app.py
```

## Pre-cached Data

The `cache/` directory contains pre-generated data for FY2026-Q4 (run_date: 2026-02-03).

This file is stored via Git LFS due to its size (~581MB). After cloning, run `git lfs pull` to download it.

## Regenerating Cache (Optional)

To generate fresh data:

```bash
SNOWFLAKE_CONNECTION_NAME=snowhouse python run_collector.py
```

Note: This requires Snowflake access and takes ~45 minutes.

## Features

- Category/Use Case/Feature/Customer hierarchy navigation
- QoQ, vs Plan, YoY comparisons with contribution percentages
- Daily revenue trends (Q4 only: Nov 1 - Jan 31)
- Top customer gainers/contractors analysis
- Revenue concentration (Top 20 vs Long Tail)
- New vs Existing customer breakdown
