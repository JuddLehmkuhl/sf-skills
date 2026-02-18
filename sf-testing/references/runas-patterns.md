# System.runAs() Permission Testing Patterns

> Referenced from: `sf-testing/SKILL.md`

---

## When to Use System.runAs()

| Scenario | Why System.runAs() |
|----------|--------------------|
| Testing record sharing rules | Verify users can/cannot see records |
| Testing CRUD/FLS enforcement | Verify `WITH SECURITY_ENFORCED` or `stripInaccessible` |
| Testing profile-based logic | Verify different behavior per profile |
| Resolving MIXED_DML_OPERATION | Separate setup-object DML from non-setup |
| Testing custom permissions | Verify bypass/required permission logic |
| Testing trigger action bypasses | Verify permission-based TAF bypass mechanisms |

### Important Limitation

> **System.runAs() does NOT enforce field-level security or object CRUD permissions in Apex.**
> It only enforces **record-level sharing**. To test FLS/CRUD, your code must explicitly
> use `Schema.sObjectType.X.isAccessible()`, `WITH SECURITY_ENFORCED`, or
> `Security.stripInaccessible()` -- then System.runAs() will control what the schema
> checks return.

---

## Pattern: Testing Profile-Based Access

```apex
@IsTest
private class AccountService_Security_Test {

    @IsTest
    static void testQueryAccounts_StandardUser_RespectsSharing() {
        // Arrange - create user with Standard User profile
        User stdUser = TestDataFactory.createUser('Standard User');

        Account privateAccount = new Account(Name = 'Private Corp');
        insert privateAccount;

        // Act - query as standard user (sharing enforced)
        List<Account> results;
        System.runAs(stdUser) {
            Test.startTest();
            results = AccountService.getMyAccounts();
            Test.stopTest();
        }

        // Assert - standard user should not see account they don't own
        Assert.areEqual(0, results.size(),
            'Standard user should not see accounts owned by other users');
    }

    @IsTest
    static void testQueryAccounts_AdminUser_SeesAll() {
        // Arrange
        User adminUser = TestDataFactory.createUser('System Administrator');

        Account testAccount = new Account(Name = 'Visible Corp');
        insert testAccount;

        // Act
        List<Account> results;
        System.runAs(adminUser) {
            Test.startTest();
            results = AccountService.getMyAccounts();
            Test.stopTest();
        }

        // Assert - admin sees all
        Assert.isTrue(results.size() > 0,
            'Admin user should see all accounts');
    }
}
```

---

## Pattern: Testing Custom Permissions (TAF Bypass)

```apex
@IsTest
static void testTriggerBypass_UserWithBypassPermission_SkipsAction() {
    // Arrange - create user and assign bypass permission set
    User bypassUser = TestDataFactory.createUser('Standard User');

    PermissionSet ps = [SELECT Id FROM PermissionSet
        WHERE Name = 'Bypass_Lead_Triggers' LIMIT 1];
    insert new PermissionSetAssignment(
        AssigneeId = bypassUser.Id,
        PermissionSetId = ps.Id
    );

    Lead testLead = new Lead(
        FirstName = 'Test',
        LastName = 'Bypass',
        Company = 'Bypass Co'
    );

    // Act - insert as bypass user
    System.runAs(bypassUser) {
        Test.startTest();
        insert testLead;
        Test.stopTest();
    }

    // Assert - trigger action should not have fired
    Lead inserted = [SELECT LeadSource FROM Lead WHERE Id = :testLead.Id];
    Assert.isNull(inserted.LeadSource,
        'Trigger action should be bypassed for user with bypass permission');
}
```

---

## Pattern: Resolving MIXED_DML_OPERATION

```apex
@IsTest
static void testUserCreationWithData() {
    // Setup objects (User, PermissionSetAssignment) must be in separate
    // transaction from non-setup objects (Account, Lead, etc.)

    User testUser;
    System.runAs(new User(Id = UserInfo.getUserId())) {
        // Create user in runAs block to isolate DML
        testUser = TestDataFactory.createUser('Standard User');
    }

    // Now safely perform non-setup DML
    System.runAs(testUser) {
        Account a = new Account(Name = 'Test Account');
        insert a;

        Assert.isNotNull(a.Id, 'Account should be created by test user');
    }
}
```
