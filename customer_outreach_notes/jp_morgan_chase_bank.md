# JP Morgan Chase Bank, National Association

## Account Info
- **Salesforce Account Name**: JP Morgan Chase Bank, National Association
- **Salesforce Account ID**: 0013r00002EEsZgAAL

---

## Notes

### 2025-01-12 | Account Team

**Context**: Weekly outreach on revenue moves

**Move Observed**: "Moves in DML, Select, CALL"

**Account Team Response**: "Nothing big, very surprised by holiday, counterfactual is 6% growth"

---

### 2024-12-01 | Account Team

**Context**: Weekly outreach on revenue moves

**Move Observed**: Down -5.8%, checking in on Teradata migration status

**Account Team Response**: "Checking in on teradata migration - Migration is ongoing, will begin to slow down in waves over the next 6 months, but the decline recently is that largest DML migration acct 'CCB' decreased a key data eng warehouse from 4xl to 3xl in order to save money"

---

### 2024-10-20 | Account Team

**Context**: Weekly outreach on revenue moves (Analytics, DE)

**Move Observed**: Down -10.4%, DML down 27.5%, Select down 17.6%

**Account Team Response**: "Looks like their usage normalized after their increased DML usage last week"

---

### 2024-10-13 | Account Team

**Context**: Weekly outreach on revenue moves (DE)

**Move Observed**: Down -19% W/W in Transformation driven by DML

**Account Team Response**: "Spikiness is to be expected for the near term; Some is coming from teradata reflection but some is coming for ETL related pipelines that are not going away at the end of the migration. The spikes are likely related to migration related activity though and might not be emblematic of steady state"

---

### 2024-10-06 | Account Team

**Context**: Weekly outreach on revenue moves (DE, Analytics)

**Move Observed**: +9.6% W/W, down -12.9% last week, +18% DML, +15% Select

**Account Team Response**: "There are more data engineering workloads going live for the Hadoop migration and they are doing parallel runs in UAT until the end of the month. That is likely the reason for the continued uptick. The other two anomalous use cases have also not been fully addressed yet"

---

### 2024-09-29 | Account Team

**Context**: Weekly outreach on revenue moves (DE)

**Move Observed**: +4% W/W, down -5.6% T4W, +32.7% Copy, +15.8% Task; Have been down the last two weeks, still behind trailing 4 week

**Account Team Response**: "WAITING, but likely related to the teradata migration reflection process"

---

### 2024-09-22 | Account Team

**Context**: Weekly outreach on revenue moves (DE)

**Move Observed**: -13.3% W/W, Down in ALOT, Select, Call, Reclustering, DML, Storage, Cortex Analyst

**Account Team Response**: "Re: DML, JPMC is coming off the highest DML spike all year due to 'reflection', where they mirror the final data between Teradata and Snowflake. Massive spike associated with this workload likely due to backfills of some big tables."

---

### 2024-09-15 | Account Team

**Context**: Weekly outreach on revenue moves (DE)

**Move Observed**: Down 4.6%

**Account Team Response**: "expected as they saw a massive 34% spike last week"

---

### 2024-09-15 | Account Team (Initial Outreach)

**Context**: Weekly outreach - question about Teradata migration accounts (CCBPXXX, CCBTXXX) with 37.4% DE and 39.8% Analytics revenue share in FY2026YTD, and very large spike in DML with account CCBPAWSUSEAST1VPS

**Move Observed**: High Analytics share of revenue from SELECT and CALL statements; large DML spike

**Account Team Response**: "The CALL statements are SQL stored procedures that are actually doing transformation. I'm not sure why they're bucketed as Analytics vs DE. It probably makes sense to inspect the contents within a given stored procedure to properly bucket these jobs. As for the high volume of SELECT, there are already thousands (maybe over 10k tbh) of active analysts in Snowflake despite the migration being ongoing. For the DML, they have a process currently running called 'reflection'. This mirrors the final data between Teradata and Snowflake. There was a massive spike in the warehouses associated with this workload this week likely due to backfills of some big tables. This happens from time to time"

---
