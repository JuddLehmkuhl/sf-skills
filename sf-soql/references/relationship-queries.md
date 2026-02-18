# Relationship Queries

> Back to [SKILL.md](../SKILL.md)

## Child-to-Parent (Dot Notation)

```sql
-- Access parent fields via lookup/master-detail
SELECT Id, Name, Account.Name, Account.Industry
FROM Contact
WHERE Account.AnnualRevenue > 1000000

-- Up to 5 levels deep
SELECT Id, Contact.Account.Owner.Manager.Name
FROM Case

-- Custom relationship: use __r suffix
SELECT Id, Name, Custom_Lookup__r.Name, Custom_Lookup__r.Custom_Field__c
FROM Another_Object__c
```

## Parent-to-Child (Subquery)

```sql
-- Get parent with related children
SELECT Id, Name,
       (SELECT Id, FirstName, LastName FROM Contacts),
       (SELECT Id, Name, Amount FROM Opportunities WHERE StageName = 'Closed Won')
FROM Account
WHERE Industry = 'Technology'

-- Custom child relationship: use __r suffix (plural)
SELECT Id, Name,
       (SELECT Id, Name FROM Custom_Children__r)
FROM Parent_Object__c
```

## Common Relationship Names

| Parent Object | Child Relationship | Subquery Example |
|---------------|-------------------|------------------|
| Account | Contacts | `(SELECT Id FROM Contacts)` |
| Account | Opportunities | `(SELECT Id FROM Opportunities)` |
| Account | Cases | `(SELECT Id FROM Cases)` |
| Contact | Cases | `(SELECT Id FROM Cases)` |
| Opportunity | OpportunityLineItems | `(SELECT Id FROM OpportunityLineItems)` |
| Opportunity | OpportunityContactRoles | `(SELECT Id FROM OpportunityContactRoles)` |

> **Tip**: Use `sf-metadata` to discover custom relationship names. Run `sf sobject describe --sobject ObjectName` to see both `childRelationships` and `fields[].relationshipName`.
