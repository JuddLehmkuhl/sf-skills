# Test Patterns & Templates

> Referenced from: `sf-testing/SKILL.md`

---

## TestDataFactory Usage

> **IMPORTANT**: Do NOT duplicate the TestDataFactory inline. Use the canonical template at:
> `sf-apex/templates/test-data-factory.cls`

```apex
@TestSetup
static void makeData() {
    List<Account> accounts = TestDataFactory.createAccounts(5);
    List<Contact> contacts = TestDataFactory.createContacts(3, accounts[0].Id);
}

// Pass false to skip insert - useful for testing before-insert logic
List<Account> accounts = TestDataFactory.createAccounts(5, false);
```

---

## Pattern: Basic Test Class (Given-When-Then)

```apex
@IsTest
private class AccountServiceTest {

    @TestSetup
    static void setupTestData() {
        List<Account> accounts = TestDataFactory.createAccounts(5);
    }

    @IsTest
    static void testCreateAccount_ValidInput_ReturnsId() {
        // Given
        Account testAccount = new Account(Name = 'Test Account');

        // When
        Test.startTest();
        Id accountId = AccountService.createAccount(testAccount);
        Test.stopTest();

        // Then
        Assert.isNotNull(accountId, 'Account ID should not be null');
        Account inserted = [SELECT Name FROM Account WHERE Id = :accountId];
        Assert.areEqual('Test Account', inserted.Name, 'Account name should match');
    }

    @IsTest
    static void testCreateAccount_NullInput_ThrowsException() {
        // Given
        Account nullAccount = null;

        // When/Then
        try {
            Test.startTest();
            AccountService.createAccount(nullAccount);
            Test.stopTest();
            Assert.fail('Expected IllegalArgumentException was not thrown');
        } catch (IllegalArgumentException e) {
            Assert.isTrue(e.getMessage().contains('cannot be null'),
                'Error message should mention null: ' + e.getMessage());
        }
    }
}
```

---

## Pattern: Bulk Test (251+ Records)

```apex
@IsTest
static void testBulkInsert_251Records_NoGovernorLimits() {
    // Given - 251 records crosses the 200-record batch boundary
    List<Account> accounts = TestDataFactory.createAccounts(251, false);

    // When
    Test.startTest();
    insert accounts;  // Triggers fire in batches of 200, then 51
    Test.stopTest();

    // Then
    Integer count = [SELECT COUNT() FROM Account WHERE Id IN :accounts];
    Assert.areEqual(251, count, 'All 251 accounts should be inserted');

    // Verify no governor limits approached
    Assert.isTrue(Limits.getQueries() < 100,
        'Should not approach SOQL limit: ' + Limits.getQueries());
}
```
