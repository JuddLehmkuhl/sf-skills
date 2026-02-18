# Parallel Test Execution Gotchas

> Referenced from: `sf-testing/SKILL.md`

---

## UNABLE_TO_LOCK_ROW: Root Causes

| Cause | Example | Solution |
|-------|---------|----------|
| **Shared record contention** | Two tests update the same Account | Each test creates its own data |
| **Duplicate unique field values** | Tests insert records with same Email | Use dynamic unique values (`Crypto.getRandomLong()`) |
| **Custom Settings access** | Parallel tests read/write same Custom Setting | Use `@TestSetup` or avoid shared Custom Settings |
| **Standard Price Book** | Multiple tests access `Test.getStandardPricebookId()` | Use `FOR UPDATE` or serialize tests |
| **Trigger on shared metadata** | Triggers updating shared config records | Isolate with `@IsTest(SeeAllData=false)` |

---

## Prevention Strategies

### Strategy 1: Create all data in test (no org data dependency)
```apex
@IsTest(SeeAllData=false)  // This is the default, but be explicit
private class MyTest {
    @TestSetup
    static void makeData() {
        TestDataFactory.createAccounts(5);
    }
}
```

### Strategy 2: Use unique values to avoid index collisions
```apex
public static List<Contact> createContacts(Integer count, Id accountId) {
    String uniqueKey = String.valueOf(Crypto.getRandomLong());
    List<Contact> contacts = new List<Contact>();
    for (Integer i = 0; i < count; i++) {
        contacts.add(new Contact(
            FirstName = 'Test',
            LastName = 'Contact_' + uniqueKey + '_' + i,
            Email = 'test_' + uniqueKey + '_' + i + '@example.com'
        ));
    }
    return contacts;
}
```

### Strategy 3: Run specific test class synchronously
```bash
sf apex run test --class-names ProblematicTest --synchronous --code-coverage --result-format json --target-org [alias]
```

### Strategy 4: Mark a test class as safe for parallel
```apex
@IsTest(isParallel=true)
private class FastUnitTest {
    // Explicitly safe for parallel execution
    // Use for tests that create all their own data and have no shared state
}
```

### Strategy 5: Disable parallel testing org-wide (last resort)
```
Setup > Apex Test Execution > Options > Disable Parallel Apex Testing
```

---

## Lock Row Decision Tree

```
Test fails with UNABLE_TO_LOCK_ROW?
  |
  +-- Does the test use SeeAllData=true?
  |     YES -> Remove SeeAllData, create test data
  |
  +-- Do multiple tests insert records with the same unique field value?
  |     YES -> Add random/unique suffixes to field values
  |
  +-- Does the test access Custom Settings?
  |     YES -> Create test-specific Custom Settings in @TestSetup
  |
  +-- Does the test access Standard Price Book?
  |     YES -> Run synchronously with --synchronous flag
  |
  +-- None of the above?
        -> Run with --synchronous as workaround
        -> File a case if it only happens in parallel
```
