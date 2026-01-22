# WF Cortex Skills

Custom skills for Cortex Code.

## Skills Included

| Skill | Description |
|-------|-------------|
| `weekly-metrics-analysis` | Generate weekly product category revenue analysis with targets, WoW change, QTD vs plan |
| `de-weekly-metrics` | Data Engineering deep dive with Dynamic Tables, Snowpark, and ingestion metrics |
| `l1-commentary` | L1 financial commentary for product categories with use case and feature analysis |

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/wf-cortex-skills.git
cd wf-cortex-skills
./install.sh
```

Then reload Cortex Code: `Cmd+Shift+P` -> "Reload Window"

## Usage

After installation, trigger skills by saying:
- "weekly metrics" or "WoW report" -> `weekly-metrics-analysis`
- "DE weekly" or "data engineering metrics" -> `de-weekly-metrics`
- "L1 commentary" or "revenue analysis" -> `l1-commentary`

## Requirements

- Cortex Code IDE
- Access to Snowflake finance tables
