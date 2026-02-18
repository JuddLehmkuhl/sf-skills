# Data Tree Import/Export (Small Datasets < 2,000 Records)

> Referenced from `SKILL.md` -- Data Tree section

---

Use `sf data export tree` / `sf data import tree` for moving parent-child relational data between orgs (e.g., seed data, sample data for demos, QA environments).

## Export with Plan (Recommended)

```bash
# Export Accounts with child Contacts - generates plan file + separate JSON per object
sf data export tree \
  --query "SELECT Id, Name, Industry, (SELECT Id, FirstName, LastName, Email FROM Contacts) FROM Account WHERE Industry = 'Technology'" \
  --plan \
  --output-dir ./data/seed \
  --target-org source-org
```

This produces:
```
data/seed/
  Account-Contact-plan.json   # Plan file referencing both data files
  Accounts.json               # Account records
  Contacts.json               # Contact records with @ref to parent Accounts
```

## Import from Plan

```bash
# Import into target org - plan preserves parent-child relationships
sf data import tree \
  --plan ./data/seed/Account-Contact-plan.json \
  --target-org target-sandbox
```

## Import Individual Files (No Plan)

```bash
# Import a single object file
sf data import tree \
  --files ./data/seed/Accounts.json \
  --target-org target-sandbox
```

## Plan File Structure

```json
[
  {
    "sobject": "Account",
    "saveRefs": true,
    "resolveRefs": false,
    "files": ["Accounts.json"]
  },
  {
    "sobject": "Contact",
    "saveRefs": false,
    "resolveRefs": true,
    "files": ["Contacts.json"]
  }
]
```

- `saveRefs: true` - Save record references so children can resolve them
- `resolveRefs: true` - Resolve `@ref` placeholders to actual parent IDs

## Limitations

| Constraint | Limit |
|------------|-------|
| Max records per export query | 2,000 |
| Max records per import file | 200 |
| API used | Composite sObject Tree |
| Relationship depth | Parent + 1 child level |

If you exceed 200 records per object, split the JSON into multiple files and reference them all in the plan.
