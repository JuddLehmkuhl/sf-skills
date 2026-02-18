# Custom Exceptions - Full Patterns

> Extracted from sf-apex SKILL.md for progressive disclosure.
> Return to [SKILL.md](../SKILL.md) for the workflow and scoring.

---

## Exception Hierarchy Pattern

```apex
/**
 * @description Base exception for all application-level errors.
 *              Extend this for domain-specific exceptions.
 */
public class ApplicationException extends Exception {}

/**
 * @description Thrown when a service layer operation fails due to
 *              business rule violations.
 */
public class ServiceException extends ApplicationException {}

/**
 * @description Thrown when required data is not found.
 */
public class DataNotFoundException extends ApplicationException {}

/**
 * @description Thrown when an external integration fails.
 */
public class IntegrationException extends ApplicationException {
    public Integer statusCode { get; private set; }
    public String endpoint { get; private set; }

    public IntegrationException(String message, Integer statusCode, String endpoint) {
        this(message);
        this.statusCode = statusCode;
        this.endpoint = endpoint;
    }
}
```

---

## Service Layer Usage

```apex
public with sharing class OpportunityService {

    public class OpportunityServiceException extends Exception {}

    public static void closeOpportunities(List<Id> oppIds) {
        if (oppIds == null || oppIds.isEmpty()) {
            throw new OpportunityServiceException(
                'Cannot close opportunities: no IDs provided'
            );
        }

        Savepoint sp = Database.setSavepoint();
        try {
            List<Opportunity> opps = [
                SELECT Id, StageName, IsClosed
                FROM Opportunity
                WHERE Id IN :oppIds
                WITH USER_MODE
            ];

            if (opps.size() != oppIds.size()) {
                throw new DataNotFoundException(
                    'Expected ' + oppIds.size() + ' opportunities but found ' + opps.size()
                );
            }

            for (Opportunity opp : opps) {
                if (opp.IsClosed) {
                    throw new OpportunityServiceException(
                        'Opportunity ' + opp.Id + ' is already closed'
                    );
                }
                opp.StageName = 'Closed Won';
            }

            update opps;
        } catch (OpportunityServiceException e) {
            Database.rollback(sp);
            throw e; // Re-throw business exceptions
        } catch (Exception e) {
            Database.rollback(sp);
            throw new OpportunityServiceException(
                'Failed to close opportunities: ' + e.getMessage(), e
            );
        }
    }
}
```

---

## Best Practices

- Class name MUST end with `Exception` (Apex compiler requirement)
- Use `Savepoint` and `Database.rollback()` in service methods for transactional integrity
- Catch specific exceptions before generic `Exception`
- Re-throw or wrap exceptions -- never swallow them silently
- Include context (record IDs, field values) in exception messages
- Nest exceptions in service classes for locality: `public class MyServiceException extends Exception {}`
