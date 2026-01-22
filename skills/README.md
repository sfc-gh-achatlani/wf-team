# WF Team Skills Setup Guide

This guide explains how to access, download, and configure the weekly metrics analysis skills for use with Cortex Code.

## Prerequisites

- **Cortex Code** installed and configured
- **Git** installed on your machine
- Access to the GitHub repository: `https://github.com/sfc-gh-achatlani/wf-team.git`

---

## Step 1: Clone the Repository

Open your terminal and run:

```bash
git clone https://github.com/sfc-gh-achatlani/wf-team.git
```

This will create a `wf-team` folder in your current directory.

---

## Step 2: Copy Skills to the Correct Directory

Cortex Code looks for skills in the following directory:

```
~/.snowflake/cortex/skills/
```

### Option A: Copy the Skills Manually

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.snowflake/cortex/skills

# Copy the skills from the cloned repo
cp -r wf-team/skills/weekly-metrics-analysis ~/.snowflake/cortex/skills/
cp -r wf-team/skills/de-weekly-metrics ~/.snowflake/cortex/skills/
```

### Option B: One-Line Setup (Clone + Copy)

```bash
git clone https://github.com/sfc-gh-achatlani/wf-team.git /tmp/wf-team && \
mkdir -p ~/.snowflake/cortex/skills && \
cp -r /tmp/wf-team/skills/* ~/.snowflake/cortex/skills/
```

---

## Step 3: Verify Installation

Check that the skills are in place:

```bash
ls -la ~/.snowflake/cortex/skills/
```

You should see:

```
drwxr-xr-x  weekly-metrics-analysis
drwxr-xr-x  de-weekly-metrics
```

Each folder should contain a `SKILL.md` file:

```bash
ls ~/.snowflake/cortex/skills/weekly-metrics-analysis/
# Output: SKILL.md

ls ~/.snowflake/cortex/skills/de-weekly-metrics/
# Output: SKILL.md
```

---

## Step 4: Using the Skills

### Running the Weekly Metrics Analysis

In Cortex Code, type:

```
/weekly-metrics-analysis
```

Or simply ask:

```
Run the weekly metrics analysis
```

The skill will:
1. Ask for your preferred output format (Tables or Narrative)
2. Confirm date parameters (current week, prior week, QTD start)
3. Generate an 8-table report with executive summaries
4. Prompt you to select a product category for deep dive

### Available Product Category Deep Dives

| Category | Skill | Status |
|----------|-------|--------|
| Data Engineering | `de-weekly-metrics` | Available |
| Analytics | — | Not developed yet |
| AI/ML | — | Not developed yet |
| Platform | — | Not developed yet |
| Apps & Collab | — | Not developed yet |

---

## Updating Skills

To get the latest version of the skills:

```bash
cd /path/to/wf-team
git pull origin main

# Re-copy to skills directory
cp -r skills/* ~/.snowflake/cortex/skills/
```

---

## Troubleshooting

### Skill not appearing in Cortex Code

1. Verify the skill is in the correct directory:
   ```bash
   ls ~/.snowflake/cortex/skills/weekly-metrics-analysis/SKILL.md
   ```

2. Restart Cortex Code to reload skills

3. Check file permissions:
   ```bash
   chmod -R 755 ~/.snowflake/cortex/skills/
   ```

### Permission denied when cloning

Contact the repository owner to request access, or verify your GitHub credentials:

```bash
gh auth status
```

---

## Skills Overview

### weekly-metrics-analysis

Generates a comprehensive weekly revenue analysis across all product categories:

- **Table 1:** FQ Y/Y Growth Forecast Evolution
- **Table 2:** QTD vs Plan by Category
- **Table 3:** Product Category Summary (WoW)
- **Table 4:** Full Quarter Forecast vs Plan vs Target
- **Table 5:** Top 25 Customers
- **Table 6:** Top 15 Weekly Gainers
- **Table 7:** Top 15 Weekly Contractors
- **Table 8:** Product Category Weekly View (Mix & Contribution)

### de-weekly-metrics

Deep dive into Data Engineering category:

- Use Case Analysis (Transformation, Ingestion, Interoperable Storage)
- Feature Growth Contribution with Mix % and Outsized Mover flags
- Dynamic Tables metrics (Revenue, Table Count, Storage)
- Snowpark metrics (DE + All-Up)
- TB Ingested by modality with top customers
- Anomalous Customer Detection (8-week baseline analysis)

---

## Questions?

Contact the WF Team or raise an issue in the GitHub repository.
