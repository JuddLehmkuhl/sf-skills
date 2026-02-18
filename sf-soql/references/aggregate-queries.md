# Aggregate Queries

> Back to [SKILL.md](../SKILL.md)

## Basic Aggregates

```sql
-- Count all records (returns Integer)
SELECT COUNT() FROM Account WHERE Industry = 'Technology'

-- Count with alias (returns AggregateResult[])
SELECT COUNT(Id) cnt FROM Account

-- Multiple aggregates in one query
SELECT SUM(Amount) totalRevenue, AVG(Amount) avgDeal,
       MIN(Amount) smallest, MAX(Amount) largest
FROM Opportunity
WHERE StageName = 'Closed Won' AND CloseDate = THIS_YEAR
```

## GROUP BY

```sql
-- Count by field
SELECT Industry, COUNT(Id) cnt
FROM Account
GROUP BY Industry

-- Multiple groupings with date functions
SELECT StageName, CALENDAR_YEAR(CloseDate) yr, COUNT(Id) cnt
FROM Opportunity
GROUP BY StageName, CALENDAR_YEAR(CloseDate)

-- GROUP BY ROLLUP (subtotals)
SELECT LeadSource, Rating, COUNT(Id)
FROM Lead
GROUP BY ROLLUP(LeadSource, Rating)

-- GROUP BY CUBE (all combinations)
SELECT Type, BillingState, COUNT(Id)
FROM Account
GROUP BY CUBE(Type, BillingState)
```

## HAVING Clause

```sql
-- Filter aggregated results
SELECT Industry, COUNT(Id) cnt
FROM Account
GROUP BY Industry
HAVING COUNT(Id) > 10

-- Complex HAVING
SELECT AccountId, SUM(Amount) total
FROM Opportunity
WHERE StageName = 'Closed Won'
GROUP BY AccountId
HAVING SUM(Amount) > 100000
```
