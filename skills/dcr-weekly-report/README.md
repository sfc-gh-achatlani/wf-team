# DCR Weekly Report Generator

Generates interactive HTML reports for Data Clean Room (DCR) metrics.

## Setup

1. Clone to your Claude skills directory:
   ```bash
   git clone <repo-url> ~/.claude/skills/dcr-weekly-report
   ```

2. Install dependencies:
   ```bash
   cd ~/.claude/skills/dcr-weekly-report
   uv sync
   ```

3. Set your Snowflake connection name:
   ```bash
   export SNOWFLAKE_CONNECTION_NAME=your_connection_name
   ```

## Usage

```bash
uv run python run_dcr_report.py --week-end 2026-01-25
```

Reports are saved to `output/dcr_report_YYYY-MM-DD.html`

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Snowflake connection with access to `finance` and `snowscience` databases
