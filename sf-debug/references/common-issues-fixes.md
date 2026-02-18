# Common Issues & Fixes (Full Examples)

> Parent: [SKILL.md](../SKILL.md) -- Common Issues & Solutions section

## 1. SOQL Query in Loop

**Detection**:
```
|SOQL_EXECUTE_BEGIN|[line 45]
|SOQL_EXECUTE_END|[1 row]
... (repeats 50+ times)
```

**Analysis Output**:
```
CRITICAL: SOQL Query in Loop Detected
   Location: AccountService.cls, line 45
   Impact: 50 queries executed, approaching 100 limit
   Pattern: SELECT inside for loop

RECOMMENDED FIX:
   Move query BEFORE loop, use Map for lookups:

   // Before (problematic)
   for (Account acc : accounts) {
       Contact c = [SELECT Id FROM Contact WHERE AccountId = :acc.Id LIMIT 1];
   }

   // After (bulkified)
   Map<Id, Contact> contactsByAccount = new Map<Id, Contact>();
   for (Contact c : [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds]) {
       contactsByAccount.put(c.AccountId, c);
   }
   for (Account acc : accounts) {
       Contact c = contactsByAccount.get(acc.Id);
   }
```

## 2. Non-Selective Query

**Detection**:
```
|SOQL_EXECUTE_BEGIN|[line 23]|SELECT Id FROM Lead WHERE Status = 'Open'
|SOQL_EXECUTE_END|[250000 rows queried]
```

**Analysis Output**:
```
WARNING: Non-Selective Query Detected
   Location: LeadService.cls, line 23
   Rows Scanned: 250,000
   Filter Field: Status (not indexed)

RECOMMENDED FIX:
   Option 1: Add indexed field to WHERE clause
   Option 2: Create custom index on Status field (file a Salesforce Support case)
   Option 3: Add LIMIT clause if not all records needed

   // Before
   List<Lead> leads = [SELECT Id FROM Lead WHERE Status = 'Open'];

   // After (with additional selective filter)
   List<Lead> leads = [SELECT Id FROM Lead
                       WHERE Status = 'Open'
                       AND CreatedDate = LAST_N_DAYS:30
                       LIMIT 10000];
```

> **Cross-reference**: Use **sf-soql** skill for deep query optimization, composite index strategies, and SOQL rewriting.

## 3. CPU Time Limit

**Detection**:
```
|LIMIT_USAGE_FOR_NS|CPU_TIME|9500|10000
```

**Analysis Output**:
```
CRITICAL: CPU Time Limit Approaching (95%)
   Used: 9,500 ms
   Limit: 10,000 ms (sync) / 60,000 ms (async)

ANALYSIS:
   Top CPU consumers:
   1. StringUtils.formatAll() - 3,200 ms (line 89)
   2. CalculationService.compute() - 2,800 ms (line 156)
   3. ValidationHelper.validateAll() - 1,500 ms (line 45)

RECOMMENDED FIX:
   1. Move heavy computation to @future or Queueable
   2. Optimize algorithms (O(n^2) -> O(n))
   3. Cache repeated calculations
   4. Use formula fields instead of Apex where possible
   5. Avoid String concatenation in loops (use List<String> + String.join)
```

## 4. Heap Size Limit

**Detection**:
```
|HEAP_ALLOCATE|[5800000]
|LIMIT_USAGE_FOR_NS|HEAP_SIZE|5800000|6000000
```

**Analysis Output**:
```
CRITICAL: Heap Size Limit Approaching (97%)
   Used: 5.8 MB
   Limit: 6 MB (sync) / 12 MB (async)

ANALYSIS:
   Large allocations detected:
   1. Line 34: List<Account> - 2.1 MB (50,000 records)
   2. Line 78: Map<Id, String> - 1.8 MB
   3. Line 112: String concatenation - 1.2 MB

RECOMMENDED FIX:
   1. Use SOQL FOR loops instead of querying all at once
   2. Process in batches of 200 records
   3. Use transient keyword for variables not needed in view state
   4. Clear collections when no longer needed (list.clear())
   5. Select only needed fields (not SELECT *)

   // Before
   List<Account> allAccounts = [SELECT Id, Name FROM Account];

   // After (SOQL FOR loop -- doesn't load all into heap)
   for (Account acc : [SELECT Id, Name FROM Account]) {
       // Process one at a time
   }
```

## 5. Exception Analysis

**Detection**:
```
|EXCEPTION_THROWN|[line 67]|System.NullPointerException: Attempt to de-reference a null object
|FATAL_ERROR|System.NullPointerException: Attempt to de-reference a null object
```

**Analysis Output**:
```
EXCEPTION: System.NullPointerException
   Location: ContactService.cls, line 67
   Message: Attempt to de-reference a null object

STACK TRACE ANALYSIS:
   ContactService.getContactDetails() - line 67
       AccountController.loadData() - line 34
           trigger AccountTrigger - line 5

ROOT CAUSE:
   Variable 'contact' is null when accessing 'contact.Email'
   Likely scenario: Query returned no results

RECOMMENDED FIX:
   // Before
   Contact contact = [SELECT Email FROM Contact WHERE AccountId = :accId LIMIT 1];
   String email = contact.Email;  // FAILS if no contact found

   // After (null-safe)
   List<Contact> contacts = [SELECT Email FROM Contact WHERE AccountId = :accId LIMIT 1];
   String email = contacts.isEmpty() ? null : contacts[0].Email;

   // Or using safe navigation (API 62.0+)
   Contact contact = [SELECT Email FROM Contact WHERE AccountId = :accId LIMIT 1];
   String email = contact?.Email;
```

## 6. Mixed DML Error

**Detection**:
```
|EXCEPTION_THROWN|System.DmlException: MIXED_DML_OPERATION
```

**Analysis Output**:
```
EXCEPTION: System.DmlException - MIXED_DML_OPERATION
   Cannot perform DML on setup and non-setup objects in the same transaction.
   Setup objects: User, PermissionSetAssignment, GroupMember
   Non-setup objects: Account, Contact, Custom__c

RECOMMENDED FIX:
   // Isolate setup DML in a @future method
   @future
   public static void assignPermissionSet(Id userId, Id permSetId) {
       insert new PermissionSetAssignment(
           AssigneeId = userId,
           PermissionSetId = permSetId
       );
   }

   // Or use System.runAs() in tests
   System.runAs(new User(Id = testUser.Id)) {
       // DML on non-setup objects here
   }
```

## 7. Uncommitted Work Pending

**Detection**:
```
|EXCEPTION_THROWN|System.CalloutException: You have uncommitted work pending. Please commit or rollback before calling out.
```

**Analysis Output**:
```
EXCEPTION: System.CalloutException
   DML was performed before an HTTP callout in the same transaction.
   Salesforce requires callouts to happen BEFORE any DML.

RECOMMENDED FIX:
   Option 1: Reorder -- do callouts first, then DML
   Option 2: Move callout to @future(callout=true) method
   Option 3: Use Queueable with AllowsCallouts interface

   public class CalloutQueueable implements Queueable, Database.AllowsCallouts {
       public void execute(QueueableContext ctx) {
           // Callout here, then DML
       }
   }
```
