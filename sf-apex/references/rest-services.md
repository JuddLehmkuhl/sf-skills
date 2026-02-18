# Apex REST Services - Full Patterns

> Extracted from sf-apex SKILL.md for progressive disclosure.
> Return to [SKILL.md](../SKILL.md) for the workflow and scoring.

---

## Full CRUD REST Service

```apex
@RestResource(urlMapping='/api/accounts/*')
global with sharing class AccountRestService {

    /**
     * @description Retrieve account by ID.
     *              GET /services/apexrest/api/accounts/{accountId}
     */
    @HttpGet
    global static AccountDTO getAccount() {
        RestRequest req = RestContext.request;
        String accountId = req.requestURI.substringAfterLast('/');

        List<Account> accounts = [
            SELECT Id, Name, Industry, AnnualRevenue, BillingCity, BillingState
            FROM Account
            WHERE Id = :accountId
            WITH USER_MODE
            LIMIT 1
        ];

        if (accounts.isEmpty()) {
            RestContext.response.statusCode = 404;
            return null;
        }

        return new AccountDTO(accounts[0]);
    }

    /**
     * @description Create a new account.
     *              POST /services/apexrest/api/accounts
     *              Body: { "name": "Acme", "industry": "Technology" }
     */
    @HttpPost
    global static AccountDTO createAccount() {
        RestRequest req = RestContext.request;
        Map<String, Object> body = (Map<String, Object>)
            JSON.deserializeUntyped(req.requestBody.toString());

        String name = (String) body.get('name');
        if (String.isBlank(name)) {
            RestContext.response.statusCode = 400;
            throw new RestServiceException('Account name is required');
        }

        Account acc = new Account(
            Name = name,
            Industry = (String) body.get('industry')
        );
        insert acc;

        RestContext.response.statusCode = 201;
        return new AccountDTO(acc);
    }

    /**
     * @description Update an existing account.
     *              PATCH /services/apexrest/api/accounts/{accountId}
     */
    @HttpPatch
    global static AccountDTO updateAccount() {
        RestRequest req = RestContext.request;
        String accountId = req.requestURI.substringAfterLast('/');

        Map<String, Object> body = (Map<String, Object>)
            JSON.deserializeUntyped(req.requestBody.toString());

        Account acc = [
            SELECT Id, Name, Industry
            FROM Account
            WHERE Id = :accountId
            WITH USER_MODE
            LIMIT 1
        ];

        if (body.containsKey('name')) {
            acc.Name = (String) body.get('name');
        }
        if (body.containsKey('industry')) {
            acc.Industry = (String) body.get('industry');
        }

        update acc;
        return new AccountDTO(acc);
    }

    /**
     * @description Delete an account.
     *              DELETE /services/apexrest/api/accounts/{accountId}
     */
    @HttpDelete
    global static void deleteAccount() {
        RestRequest req = RestContext.request;
        String accountId = req.requestURI.substringAfterLast('/');
        delete [SELECT Id FROM Account WHERE Id = :accountId WITH USER_MODE LIMIT 1];
        RestContext.response.statusCode = 204;
    }

    /**
     * @description DTO to control JSON serialization.
     *              Never return raw SObjects from REST endpoints.
     */
    global class AccountDTO {
        public String id;
        public String name;
        public String industry;
        public Decimal annualRevenue;
        public String billingCity;

        public AccountDTO(Account acc) {
            this.id = acc.Id;
            this.name = acc.Name;
            this.industry = acc.Industry;
            this.annualRevenue = acc.AnnualRevenue;
            this.billingCity = acc.BillingCity;
        }
    }

    public class RestServiceException extends Exception {}
}
```

---

## Best Practices

- Use DTOs (wrapper classes) -- never expose raw SObjects to external consumers
- Set `RestContext.response.statusCode` explicitly (201 for create, 204 for delete, 400 for bad request, 404 for not found)
- Use `WITH USER_MODE` for FLS/CRUD enforcement
- Class must be `global` for REST exposure; use `with sharing` for row-level security
- Validate input before DML; return meaningful error responses
- URL mapping supports wildcards: `/api/accounts/*` matches `/api/accounts/001xx000003ABCD`
- Test using `RestContext.request` and `RestContext.response` in test methods

---

## Testing REST Services

```apex
@IsTest
static void testGetAccount() {
    Account testAcc = new Account(Name = 'Test REST Account');
    insert testAcc;

    RestRequest req = new RestRequest();
    req.requestURI = '/services/apexrest/api/accounts/' + testAcc.Id;
    req.httpMethod = 'GET';
    RestContext.request = req;
    RestContext.response = new RestResponse();

    Test.startTest();
    AccountRestService.AccountDTO result = AccountRestService.getAccount();
    Test.stopTest();

    Assert.areEqual(testAcc.Name, result.name,
        'Should return the correct account name');
}
```
