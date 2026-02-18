---
name: sf-apex
description: >
  Generates and reviews Salesforce Apex code with 2025-2026 best practices and 150-point
  scoring. Use when writing Apex classes, triggers, test classes, batch jobs, queueable
  chains, schedulable jobs, REST services, or reviewing existing Apex code for
  bulkification, security, and SOLID principles.
license: MIT
metadata:
  version: "2.0.0"
  author: "Judd Lehmkuhl"
  scoring: "150 points across 8 categories"
---

# sf-apex: Salesforce Apex Code Generation and Review

## Core Responsibilities

1. **Code Generation**: Create Apex classes, triggers (TAF), tests, async jobs, REST services
2. **Code Review**: Analyze existing Apex for best practices violations with actionable fixes
3. **Validation & Scoring**: Score code against 8 categories (0-150 points)
4. **Deployment Integration**: Validate and deploy via sf-deploy skill

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- Class type (Trigger, Service, Selector, Batch, Queueable, Schedulable, Test, Controller, REST Service)
- Primary purpose (one sentence)
- Target object(s)
- Test requirements

**Then**:
1. Check existing code: `Glob: **/*.cls`, `Glob: **/*.trigger`
2. Check for existing TAF setup: `Glob: **/*TriggerAction*.cls`
3. Create TodoWrite tasks

### Phase 2: Design & Template Selection

| Class Type | Template |
|------------|----------|
| Trigger | `templates/trigger.trigger` |
| Trigger Action | `templates/trigger-action.cls` |
| Service | `templates/service.cls` |
| Selector | `templates/selector.cls` |
| Batch | `templates/batch.cls` |
| Queueable | `templates/queueable.cls` |
| Test | `templates/test-class.cls` |
| Test Data Factory | `templates/test-data-factory.cls` |
| Standard Class | `templates/apex-class.cls` |

**Template Path Resolution** (try in order):
1. `~/.claude/plugins/marketplaces/sf-skills/sf-apex/templates/[template]`
2. `[project-root]/sf-apex/templates/[template]`

### Phase 3: Code Generation/Review

**For Generation**:
1. Create class file in `force-app/main/default/classes/`
2. Apply naming conventions (see [docs/naming-conventions.md](docs/naming-conventions.md))
3. Include ApexDoc comments
4. Create corresponding test class

**For Review**:
1. Read existing code
2. Run validation against best practices
3. Generate improvement report with specific fixes

**Validation Output**:
```
Score: XX/150 Rating
|- Bulkification: XX/25
|- Security: XX/25
|- Testing: XX/25
|- Architecture: XX/20
|- Clean Code: XX/20
|- Error Handling: XX/15
|- Performance: XX/10
|- Documentation: XX/10
```

### Generation Guardrails (Mandatory)

If ANY anti-pattern would be generated, **STOP and ask the user**:
> "I noticed [pattern]. This will cause [problem]. Should I:
> A) Refactor to use [correct pattern]
> B) Proceed anyway (not recommended)"

| Anti-Pattern | Detection | Correct Pattern |
|--------------|-----------|-----------------|
| SOQL inside loop | `for(...) { [SELECT...] }` | Query BEFORE loop, use `Map<Id, SObject>` |
| DML inside loop | `for(...) { insert/update }` | Collect in `List<>`, single DML after loop |
| Missing sharing | `class X {` without keyword | Always use `with sharing` or `inherited sharing` |
| Hardcoded ID | 15/18-char ID literal | Use Custom Metadata, Custom Labels, or queries |
| Empty catch | `catch(e) { }` | Log with `System.debug()` or rethrow |
| String concat in SOQL | `'SELECT...WHERE Name = \'' + var` | Use bind variables `:variableName` |
| Test without assertions | `@IsTest` with no `Assert.*` | Use `Assert.areEqual()` with message |

**DO NOT generate anti-patterns even if explicitly requested.**

### Phase 4: Deployment

```
Skill(skill="sf-deploy", args="Deploy classes at force-app/main/default/classes/ to [target-org] with --dry-run")
```
Then if validation succeeds:
```
Skill(skill="sf-deploy", args="Proceed with actual deployment to [target-org]")
```

### Phase 5: Completion Summary

```
Apex Code Complete: [ClassName]
  Type: [type] | API: 62.0
  Location: force-app/main/default/classes/[ClassName].cls
  Test Class: [TestClassName].cls
  Validation: PASSED (Score: XX/150)

Next Steps: Run tests, verify behavior, monitor logs
```

---

## Best Practices (150-Point Scoring)

| Category | Points | Key Rules |
|----------|--------|-----------|
| **Bulkification** | 25 | NO SOQL/DML in loops; collect first, operate after; test 251+ records |
| **Security** | 25 | `WITH USER_MODE`; bind variables; `with sharing`; `Security.stripInaccessible()` |
| **Testing** | 25 | 95%+ coverage; Assert class; positive/negative/bulk tests; Test Data Factory |
| **Architecture** | 20 | TAF triggers; Service/Domain/Selector layers; SOLID; dependency injection |
| **Clean Code** | 20 | Meaningful names; self-documenting; no `!= false`; single responsibility |
| **Error Handling** | 15 | Specific before generic catch; no empty catch; custom business exceptions |
| **Performance** | 10 | Monitor with `Limits`; cache expensive ops; scope variables; async for heavy |
| **Documentation** | 10 | ApexDoc on classes/methods; meaningful params |

Block deployment if score < 67 points.

---

## Trigger Actions Framework (TAF) - Cross-Reference

> Full TAF documentation: `Skill(skill="salesforce-trigger-framework")`

- One logic-less trigger per object: `new MetadataTriggerHandler().run();`
- Action classes implement `TriggerAction.BeforeInsert`, `.AfterUpdate`, etc.
- Naming: `TA_<ObjectName>_<ActionDescription>` with test `_Test` suffix
- Custom Metadata uses context-specific fields (`Before_Insert__c`, `After_Update__c`)
- Order spacing: increments of 10

**If TAF is NOT installed**, use the Standard Trigger Pattern:

```apex
trigger LeadTrigger on Lead (before insert, before update) {
    LeadScoringService scoringService = new LeadScoringService();
    if (Trigger.isBefore) {
        if (Trigger.isInsert) {
            scoringService.calculateScores(Trigger.new);
        } else if (Trigger.isUpdate) {
            scoringService.recalculateIfChanged(Trigger.new, Trigger.oldMap);
        }
    }
}
```

---

## Async Apex Patterns

### Decision Matrix

| Scenario | Use | Governor Limits |
|----------|-----|-----------------|
| Simple callout, fire-and-forget | `@future(callout=true)` | 50 calls/txn, 200 queued |
| Complex logic, needs chaining | `Queueable` | 50 enqueued/txn, 1 chain depth (async) |
| Process millions of records | `Batch Apex` | 50M records, 2K scope default |
| Scheduled/recurring job | `Schedulable` | 100 scheduled jobs |
| Post-queueable cleanup/retry | `Queueable Finalizer` | 1 finalizer per Queueable |

> Full implementations (Batch, Queueable, Finalizer, Schedulable) with best practices and test examples:
> `Read: references/async-apex-patterns.md`

---

## Custom Exceptions

- Class name MUST end with `Exception`
- Use `Savepoint` + `Database.rollback()` in service methods
- Catch specific exceptions before generic `Exception`
- Re-throw or wrap -- never swallow silently
- Include context (record IDs, field values) in messages

> Full hierarchy pattern and service layer usage:
> `Read: references/custom-exceptions.md`

---

## Apex REST Services

Key rules:
- Use DTOs -- never expose raw SObjects
- Set `RestContext.response.statusCode` explicitly (201/204/400/404)
- Class must be `global with sharing`
- Use `WITH USER_MODE` for FLS/CRUD
- Validate input before DML

> Full CRUD example with DTO pattern and test:
> `Read: references/rest-services.md`

---

## Platform Cache

Key rules:
- Always handle `Cache.Org.OrgCacheException`
- Org Cache for shared data; Session Cache for user-specific
- Use `CacheBuilder` for automatic cache-miss handling
- Do NOT cache PII/credentials unless encrypted

> Full CacheManager and CacheBuilder implementations:
> `Read: references/platform-cache.md`

---

## Code Review Red Flags

| Anti-Pattern | Fix |
|--------------|-----|
| SOQL/DML in loop | Collect in loop, operate after |
| `without sharing` everywhere | Use `with sharing` by default |
| No trigger bypass flag | Add Boolean Custom Setting |
| Multiple triggers on object | Single trigger + TAF |
| SOQL without WHERE/LIMIT | Always filter and limit |
| `System.debug()` everywhere | Control via Custom Metadata |
| `isEmpty()` before DML | Remove - empty list = 0 DMLs |
| Generic Exception only | Catch specific types first |
| Hard-coded Record IDs | Query dynamically |
| No Test Data Factory | Implement Factory pattern |
| Raw SObject in REST response | Use DTO wrapper classes |
| No Savepoint in service methods | Use `Database.setSavepoint()` / `rollback()` |

---

## Modern Apex Features (API 62.0+)

- **Null coalescing**: `value ?? defaultValue`
- **Safe navigation**: `record?.Field__c`
- **User mode**: `WITH USER_MODE` in SOQL
- **Assert class**: `Assert.areEqual()`, `Assert.isTrue()`
- **Queueable Finalizers**: `System.attachFinalizer()` for post-transaction cleanup
- **Transaction Finalizers**: `FinalizerContext.getResult()`, `getException()`

**Breaking Change (API 62.0)**: Cannot modify Set while iterating -- throws `System.FinalException`

---

## Flow Integration (@InvocableMethod)

| Annotation | Purpose |
|------------|---------|
| `@InvocableMethod` | Makes method callable from Flow |
| `@InvocableVariable` | Exposes properties in Request/Response wrappers |

Use `templates/invocable-method.cls` for the complete pattern. Minimal example:

```apex
public with sharing class RecordProcessor {
    @InvocableMethod(label='Process Record' category='Custom')
    public static List<Response> execute(List<Request> requests) {
        List<Response> responses = new List<Response>();
        for (Request req : requests) {
            Response res = new Response();
            res.isSuccess = true;
            res.processedId = req.recordId;
            responses.add(res);
        }
        return responses;
    }

    public class Request {
        @InvocableVariable(label='Record ID' required=true)
        public Id recordId;
    }

    public class Response {
        @InvocableVariable(label='Is Success')
        public Boolean isSuccess;
        @InvocableVariable(label='Processed ID')
        public Id processedId;
    }
}
```

**See Also**: [docs/flow-integration.md](docs/flow-integration.md)

---

## Common Exception Types Reference

| Exception Type | When to Use |
|----------------|-------------|
| `DmlException` | Insert/update/delete failures |
| `QueryException` | SOQL query failures |
| `NullPointerException` | Null reference access |
| `ListException` | Index out of bounds |
| `MathException` | Division by zero |
| `TypeException` | Invalid type casting |
| `LimitException` | Governor limit exceeded |
| `CalloutException` | HTTP callout failures |
| `JSONException` | Malformed JSON |
| `InvalidParameterValueException` | Bad input values |

**Test pattern** -- always assert on the exception message:
```apex
@IsTest
static void testShouldThrowExceptionForMissingRequiredField() {
    try {
        insert new Account(); // Missing Name
        Assert.fail('Expected DmlException was not thrown');
    } catch (DmlException e) {
        Assert.isTrue(e.getMessage().contains('REQUIRED_FIELD_MISSING'),
            'Expected REQUIRED_FIELD_MISSING but got: ' + e.getMessage());
    }
}
```

---

## LSP-Based Validation

Optional auto-fix loop using Salesforce's Apex Language Server. Requires VS Code Salesforce Extension Pack + Java 11+. Falls back to 150-point semantic validation if unavailable.

> Full details on setup, validation flow, and sample output:
> `Read: references/lsp-validation.md`

---

## Cross-Skill Integration

| Skill | When to Use |
|-------|-------------|
| sf-metadata | Discover object/fields before coding |
| sf-data | Generate 251+ test records after deploy |
| sf-deploy | Deploy to org -- see Phase 4 |
| sf-flow | Create Flow that calls your Apex |
| sf-lwc | Create LWC that calls your Apex (`@AuraEnabled`) |
| salesforce-trigger-framework | Full TAF patterns, bypass, Flow integration |

## Cross-Skill Dependency Checklist

| Prerequisite | Check Command | Required For |
|--------------|---------------|--------------|
| TAF Package | `sf package installed list --target-org alias` | TAF trigger pattern |
| Custom Fields | `sf sobject describe --sobject Lead --target-org alias` | Field references in code |
| Permission Sets | `sf org list metadata --metadata-type PermissionSet` | FLS for custom fields |
| Trigger_Action__mdt | Check Setup > Custom Metadata Types | TAF trigger execution |

**Deployment Order**:
```
1. sf-metadata  → Create custom fields + Permission Sets
2. sf-deploy    → Deploy fields + Permission Sets
3. sf-apex      → Deploy Apex classes/triggers
4. sf-data      → Create test data
```

---

## Reference

**Docs**: `~/.claude/plugins/marketplaces/sf-skills/sf-apex/docs/` -- best-practices, trigger-actions-framework, security-guide, testing-guide, naming-conventions, solid-principles, design-patterns, code-review-checklist

**Deep-dive references**: `references/` folder:
- `async-apex-patterns.md` -- Batch, Queueable, Finalizer, Schedulable full implementations
- `custom-exceptions.md` -- Exception hierarchy and service layer patterns
- `rest-services.md` -- Full CRUD REST service with DTO and tests
- `platform-cache.md` -- CacheManager and CacheBuilder patterns
- `lsp-validation.md` -- LSP auto-fix loop setup and usage

---

## Notes

- **API Version**: 62.0 required
- **TAF Optional**: Prefer TAF when installed, standard trigger pattern as fallback
- **Scoring**: Block deployment if score < 67
- **LSP**: Optional but recommended for real-time syntax validation

---

## Sources

- [Future vs Queueable vs Batch vs Schedulable - SFDC Prep](https://sfdcprep.com/salesforce-apex-future-vs-queueable-vs-batch-vs-schedulable/)
- [Simple Guide to Batch Apex - Salesforce Ben](https://www.salesforceben.com/batch-apex/)
- [Master Queueable Apex - Salesforce Ben](https://www.salesforceben.com/master-queueable-apex-when-why-and-how-to-use-it/)
- [Apex Scheduler - Salesforce Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_scheduler.htm)
- [Transaction Finalizers - Salesforce Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_transaction_finalizers.htm)
- [Apex REST Methods - Salesforce Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_rest_methods.htm)
- [Platform Cache Best Practices - Salesforce Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_platform_cache_best_practices.htm)
- [Custom Exceptions - Salesforce Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_exception_custom.htm)

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2026 Jag Valaiyapathy
