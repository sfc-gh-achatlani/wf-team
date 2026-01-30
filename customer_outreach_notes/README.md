# Product Finance Customer Outreach Notes

Knowledge base for tracking account team feedback and customer insights.

## Structure

```
product_finance_customer_outreach_notes/
├── accounts/                    # One file per account
│   ├── acme_corp_001ABC.md     # Format: {name}_{sfdc_id}.md
│   └── ...
├── templates/
│   └── account_template.md     # Copy this for new accounts
└── README.md
```

## File Naming Convention

**Pattern**: `{account_name_snake_case}_{sfdc_account_id}.md`

Examples:
- `capital_one_0015000001ABC.md`
- `jpmorgan_chase_0015000002XYZ.md`

This enables:
1. Lookup by name (human-readable)
2. Lookup by SFDC ID (join to revenue data)
3. Alphabetical browsing

## Adding a New Account

1. Copy `templates/account_template.md` to `accounts/`
2. Rename using the convention above
3. Fill in Account Info section (only need to do once)
4. Add notes chronologically (newest at top)

## Adding Notes to Existing Account

1. Open the account file
2. Add a new section under `## Notes` with today's date
3. Fill in the fields

## Querying with AI

Ask Cortex Code questions like:
- "What do we know about {Account Name}?"
- "Find notes mentioning {Feature Name}"
- "What accounts discussed {Use Case} in the last month?"
- "Summarize feedback on {Product Category} from Q3"

## Syncing to GitHub

```bash
cd ~/product_finance_customer_outreach_notes
git init
git add .
git commit -m "Initial commit"
git remote add origin {your-repo-url}
git push -u origin main
```

## Tips

- Use consistent terminology (match product category/feature names from revenue data)
- Include SFDC Account ID in every file for joining to financial data
- Date format: YYYY-MM-DD (enables chronological sorting)
- Tag revenue impact as Positive/Negative/Neutral for quick filtering
