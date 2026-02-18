# Advanced SOQL Features

> Back to [SKILL.md](../SKILL.md)

## Polymorphic Relationships (TYPEOF)

```sql
-- Query polymorphic fields like Task.What or Event.Who
SELECT Id, Subject, What.Name, What.Type
FROM Task
WHERE What.Type IN ('Account', 'Opportunity')

-- TYPEOF for conditional field selection
SELECT Id, Subject,
    TYPEOF What
        WHEN Account THEN Name, Phone, Website
        WHEN Opportunity THEN Name, Amount, StageName
    END
FROM Task
WHERE CreatedDate = THIS_MONTH
```

## Semi-Joins and Anti-Joins

```sql
-- Semi-join: Records WITH related records
SELECT Id, Name FROM Account
WHERE Id IN (SELECT AccountId FROM Contact WHERE Email != null)

-- Anti-join: Records WITHOUT related records
SELECT Id, Name FROM Account
WHERE Id NOT IN (SELECT AccountId FROM Opportunity)

-- Multi-level semi-join
SELECT Id, Name FROM Account
WHERE Id IN (
    SELECT AccountId FROM Contact
    WHERE Id IN (SELECT ContactId FROM CampaignMember WHERE Status = 'Responded')
)
```

## FOR UPDATE (Record Locking)

```apex
// Lock records to prevent concurrent modification
List<Account> accounts = [
    SELECT Id, Name, AnnualRevenue
    FROM Account
    WHERE Id = :targetId
    FOR UPDATE
];
// Records locked until transaction commits or rolls back
// NOT supported in: subqueries, aggregate queries, SOSL
```

## FORMAT() and convertCurrency()

```sql
-- Format fields for display (respects user locale)
SELECT FORMAT(Amount), FORMAT(CloseDate), FORMAT(CreatedDate)
FROM Opportunity

-- Convert to user's currency (multi-currency orgs)
SELECT Id, Name, convertCurrency(Amount) convertedAmount
FROM Opportunity
WHERE convertCurrency(Amount) > 100000
```

## FIELDS() Functions

```sql
-- STANDARD fields only (safe for production)
SELECT FIELDS(STANDARD) FROM Account LIMIT 200

-- ALL fields (developer/debug use only -- requires LIMIT 200)
SELECT FIELDS(ALL) FROM Account LIMIT 200

-- CUSTOM fields only
SELECT FIELDS(CUSTOM) FROM Account LIMIT 200
```

## Date Functions in GROUP BY

```sql
-- Available date functions
SELECT CALENDAR_YEAR(CloseDate) yr, CALENDAR_MONTH(CloseDate) mo, COUNT(Id)
FROM Opportunity
GROUP BY CALENDAR_YEAR(CloseDate), CALENDAR_MONTH(CloseDate)

-- Other date functions: DAY_IN_MONTH, DAY_IN_WEEK, DAY_IN_YEAR,
-- DAY_ONLY, FISCAL_MONTH, FISCAL_QUARTER, FISCAL_YEAR,
-- HOUR_IN_DAY, WEEK_IN_MONTH, WEEK_IN_YEAR
```

## OFFSET (Pagination)

```sql
-- Skip first 100 results, return next 50
SELECT Id, Name FROM Account
ORDER BY Name
LIMIT 50 OFFSET 100

-- Maximum OFFSET: 2,000 records
-- For deep pagination, use query locators or keyset pagination
```
