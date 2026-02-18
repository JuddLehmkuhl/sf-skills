# SOSL: Salesforce Object Search Language

> Back to [SKILL.md](../SKILL.md)

## SOSL Syntax

```sql
FIND {searchExpression}
  [IN searchGroup]
  [RETURNING objectType (fieldList [WHERE condition] [ORDER BY field] [LIMIT n])]
  [WITH snippetOptions]
  [LIMIT n]
```

**Search Groups**:
- `ALL FIELDS` -- searches all searchable fields (default)
- `NAME FIELDS` -- searches only Name fields
- `EMAIL FIELDS` -- searches only Email fields
- `PHONE FIELDS` -- searches only Phone fields
- `SIDEBAR FIELDS` -- searches fields displayed in sidebar search

## SOSL in Apex

```apex
// Basic multi-object search
List<List<SObject>> results = [
    FIND 'Acme*' IN NAME FIELDS
    RETURNING Account(Id, Name, Industry),
              Contact(Id, FirstName, LastName, Email),
              Opportunity(Id, Name, Amount)
];

List<Account> accounts = (List<Account>) results[0];
List<Contact> contacts = (List<Contact>) results[1];
List<Opportunity> opps = (List<Opportunity>) results[2];

// With WHERE filtering on returned objects
List<List<SObject>> results = [
    FIND 'cloud' IN ALL FIELDS
    RETURNING
        Account(Id, Name WHERE Industry = 'Technology' ORDER BY Name LIMIT 10),
        Contact(Id, Name, Email WHERE MailingState = 'CA')
    LIMIT 100
];
```

## Dynamic SOSL

```apex
// Dynamic SOSL uses Search.query()
String searchTerm = String.escapeSingleQuotes(userInput);
String soslQuery = 'FIND {' + searchTerm + '} IN ALL FIELDS '
    + 'RETURNING Account(Id, Name), Contact(Id, Name, Email) LIMIT 50';
List<List<SObject>> results = Search.query(soslQuery);
```

## SOSL Governor Limits

```
- Maximum 20 SOSL queries per transaction (sync and async)
- Maximum 2,000 records returned per object in RETURNING clause
- Maximum 200 characters in search term
- Minimum 2 characters in search term (unless using * wildcard)
- Search terms are tokenized; short common words may be ignored
```
