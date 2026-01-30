# Weekly Metrics Report Generator

Generates interactive HTML reports for weekly product category revenue metrics.

## Setup

1. Clone to your Claude skills directory:
   ```bash
   git clone <repo-url> ~/.claude/skills/weekly-metrics-report
   ```

2. Install dependencies:
   ```bash
   cd ~/.claude/skills/weekly-metrics-report
   uv sync
   ```

3. Set your Snowflake connection name:
   ```bash
   export SNOWFLAKE_CONNECTION_NAME=your_connection_name
   ```

## Usage

```bash
uv run python run_report.py --week-end 2026-01-19
```

Reports are saved to `output/report_YYYY-MM-DD.html`

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Snowflake connection with access to `finance` database
