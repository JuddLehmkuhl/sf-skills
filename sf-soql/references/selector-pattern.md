# Selector Pattern (DAL Architecture)

> Back to [SKILL.md](../SKILL.md)

When using the `salesforce-trigger-framework`, consolidate all SOQL for an object into a Selector (Data Access Layer) class:

```apex
/**
 * @description Selector/DAL for Account queries. All Account SOQL
 *              lives here to avoid scattered queries and simplify testing.
 */
public with sharing class AccountSelector {

    // Standard fields queried by default
    private static final List<String> DEFAULT_FIELDS = new List<String>{
        'Id', 'Name', 'Industry', 'AnnualRevenue', 'OwnerId'
    };

    /**
     * @description Query accounts by Id set
     */
    public static List<Account> selectById(Set<Id> accountIds) {
        return [
            SELECT Id, Name, Industry, AnnualRevenue, OwnerId
            FROM Account
            WHERE Id IN :accountIds
            WITH USER_MODE
        ];
    }

    /**
     * @description Query accounts with contacts by Id set
     */
    public static List<Account> selectWithContactsById(Set<Id> accountIds) {
        return [
            SELECT Id, Name, Industry,
                   (SELECT Id, FirstName, LastName, Email FROM Contacts)
            FROM Account
            WHERE Id IN :accountIds
            WITH USER_MODE
        ];
    }

    /**
     * @description Dynamic query with caller-specified fields and filters
     */
    public static List<Account> selectDynamic(
        Set<String> fields,
        String whereClause,
        Map<String, Object> binds,
        Integer recordLimit
    ) {
        String query = 'SELECT ' + String.join(new List<String>(fields), ', ')
            + ' FROM Account';
        if (String.isNotBlank(whereClause)) {
            query += ' WHERE ' + whereClause;
        }
        query += ' LIMIT ' + recordLimit;
        return Database.queryWithBinds(query, binds, AccessLevel.USER_MODE);
    }
}
```

> See `salesforce-trigger-framework/SKILL.md` for the full `Trigger > MetadataTriggerHandler > TA_* > Services > DAL` architecture pattern.
