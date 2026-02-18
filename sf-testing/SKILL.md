---
name: sf-testing
description: >
  Salesforce testing skill with test execution, code coverage analysis,
  and agentic test-fix loops. Run Apex tests, analyze coverage, generate test patterns,
  and automatically fix failing tests with 120-point scoring.
license: MIT
metadata:
  version: "3.0.0"
  author: "Jag Valaiyapathy"
  scoring: "120 points across 6 categories"
  enriched: "2026-02-18"
---

# sf-testing: Salesforce Test Execution & Coverage Analysis

## Core Responsibilities

1. **Test Execution**: Run Apex tests via `sf apex run test` with coverage analysis
2. **Coverage Analysis**: Parse coverage reports, identify untested code paths, drive to 95%+
3. **Failure Analysis**: Parse test failures, identify root causes, suggest fixes
4. **Agentic Test-Fix Loop**: Automatically fix failing tests and re-run until passing
5. **Test Generation**: Create test classes using sf-apex patterns and TestDataFactory
6. **Bulk Testing**: Validate with 251+ records for governor limit safety

## Cross-Skill References

| Skill | Relationship | Key Integration Point |
|-------|-------------|----------------------|
| **salesforce-trigger-framework** | **PRIMARY** - Most tests are for TA_* actions | `TA_<Object>_<Action>_Test` naming, bypass testing |
| **sf-apex** | Generate test classes, fix failing code | `Skill(skill="sf-apex", args="Create test class for LeadService")` |
| **sf-data** | Create bulk test data (251+ records) | `Skill(skill="sf-data", args="Create 251 Leads for bulk testing")` |
| **sf-deploy** | Deploy test classes to org | `Skill(skill="sf-deploy", args="Deploy tests to sandbox")` |
| **sf-debug** | Analyze failures with debug logs | `Skill(skill="sf-debug", args="Analyze test failure logs")` |

> When testing TAF components, load `salesforce-trigger-framework/SKILL.md` first for architecture and naming conventions.

---

## Workflow (5-Phase Pattern)

### Phase 1: Test Discovery

1. Check existing tests: `Glob: **/*Test*.cls`, `Glob: **/*_Test.cls`
2. Check for Test Data Factories: `Glob: **/*TestDataFactory*.cls`
3. Check for test suites: `Glob: **/*.testSuite-meta.xml`

### Phase 2: Test Execution

```bash
# Single class
sf apex run test --class-names MyClassTest --code-coverage --result-format json --output-dir test-results --target-org [alias]

# All local tests
sf apex run test --test-level RunLocalTests --code-coverage --result-format json --output-dir test-results --target-org [alias]

# Specific methods
sf apex run test --tests MyClassTest.testMethod1 --tests MyClassTest.testMethod2 --code-coverage --result-format json --target-org [alias]

# Test suite
sf apex run test --suite-names MySuite --code-coverage --result-format json --target-org [alias]

# Synchronous (disables parallel)
sf apex run test --class-names MyClassTest --synchronous --code-coverage --result-format json --target-org [alias]
```

### Phase 3: Results Analysis

Parse `test-results/test-run-id.json` and report:
- Pass/fail/skip counts and duration
- Failed test names with line numbers and error messages
- Coverage % per class, flagging any below 95%
- Uncovered line ranges for classes below threshold

### Phase 4: Agentic Test-Fix Loop

When tests fail, automatically:
1. Parse failure message and stack trace
2. Identify root cause using decision tree below
3. Read failing test class + class under test
4. Generate fix via sf-apex skill
5. Re-run specific failing test
6. Repeat until passing (max 3 attempts)

**Auto-Fix**: `Skill(skill="sf-apex", args="Fix failing test [TestClass].[method] - Error: [message]")`

### Phase 5: Coverage Improvement

1. Run with `--detailed-coverage` to get uncovered line numbers
2. Categorize uncovered lines (exception handlers, null guards, branches, bulk edge cases, permission checks, async callbacks)
3. Write targeted test methods: `test<Method>_<Scenario>_<Expected>`
4. Re-run and iterate until 95%+

**Coverage math**: `Lines needed = (Target% * Total Lines) - Currently Covered Lines`

---

## Failure Analysis Decision Tree

| Error Type | Root Cause | Auto-Fix Strategy |
|------------|------------|-------------------|
| `System.AssertException` | Wrong expected value or logic bug | Analyze assertion, check if test or code is wrong |
| `System.NullPointerException` | Missing null check or test data | Add null safety or fix test data setup |
| `System.DmlException` | Validation rule, required field, trigger | Check org config, add required fields to test data |
| `System.LimitException` | Governor limit hit | Refactor to use bulkified patterns |
| `System.QueryException` | No rows returned | Add test data or adjust query |
| `System.TypeException` | Type mismatch | Fix type casting or data format |
| `System.MathException` | Division by zero, overflow | Add boundary checks |

---

## TAF Test Naming Convention

| Component | Naming Pattern | Example |
|-----------|---------------|---------|
| Action Class | `TA_<Object>_<Action>` | `TA_Lead_ValidateRequiredFields` |
| Test Class | `TA_<Object>_<Action>_Test` | `TA_Lead_ValidateRequiredFields_Test` |
| Service Test | `<Object>Service_Test` | `LeadService_Test` |
| DAL Test | `DAL_<Object>_Test` | `DAL_Lead_Test` |

> Full TAF test patterns (DML path, bypass, service layer): `Read: references/taf-test-patterns.md`

---

## Test Patterns Quick Reference

**TestDataFactory**: Use canonical template at `sf-apex/templates/test-data-factory.cls`. Do NOT duplicate.

**Test method naming**: `test<Method>_<Scenario>_<Expected>` (e.g., `testProcessAccounts_NullInput_ReturnsEmpty`)

**Always test**:
- Happy path (valid input)
- Negative path (null, empty, invalid)
- Bulk (251+ records crossing batch boundary)
- Exception handlers (force the exception with bad data)

> Full test patterns (Given-When-Then, bulk, exception): `Read: references/test-patterns.md`

---

## Mocking & Stubbing

**HttpCalloutMock**: Inner class implementing `HttpCalloutMock` with configurable status code and body.

**StubProvider (UniversalMock)**: `System.StubProvider` implementation with return value configuration and call logging. Use when isolating from DML, callouts, or SOQL dependencies.

**DML Abstraction (IDml/MockDml)**: Interface-based DML layer. `DatabaseDml` for production, `MockDml` for tests. Up to 35x speedup by avoiding database hits.

> Full code for all mocking patterns: `Read: references/mocking-patterns.md`

---

## @TestVisible

Use `@TestVisible` for: dependency injection, testing private calculations, asserting against private constants. Do NOT use on everything -- only expose what cannot be tested through public methods.

> Full patterns and anti-patterns: `Read: references/test-visible-patterns.md`

---

## System.runAs()

Use for: sharing rule tests, CRUD/FLS enforcement, profile-based logic, MIXED_DML_OPERATION resolution, custom permission testing.

**Limitation**: `System.runAs()` only enforces record-level sharing, not FLS/CRUD. Your code must explicitly use `Schema.sObjectType.X.isAccessible()`, `WITH SECURITY_ENFORCED`, or `Security.stripInaccessible()`.

> Full patterns (profile access, custom permissions, MIXED_DML fix): `Read: references/runas-patterns.md`

---

## Test Suites

Organize tests into `ApexTestSuite` metadata for CI/CD. Run feature-aligned suites (`--suite-names LeadTests`) instead of all tests for faster feedback.

> Suite creation, organization, and CI/CD patterns: `Read: references/test-suites.md`

---

## Parallel Execution & Lock Rows

If `UNABLE_TO_LOCK_ROW`: isolate test data, use `Crypto.getRandomLong()` for unique values, run `--synchronous` as fallback.

> Full lock row decision tree and prevention strategies: `Read: references/parallel-testing.md`

---

## Best Practices (120-Point Scoring)

| Category | Points | Key Rules |
|----------|--------|-----------|
| **Test Coverage** | 25 | 95%+ class coverage; all public methods tested; edge cases covered |
| **Assertion Quality** | 25 | Assert class used; meaningful messages; positive AND negative tests |
| **Bulk Testing** | 20 | Test with 251+ records; verify no SOQL/DML in loops under load |
| **Test Data** | 20 | TestDataFactory used; no hardcoded IDs; @TestSetup for efficiency |
| **Isolation** | 15 | SeeAllData=false; no org dependencies; mock external callouts |
| **Documentation** | 15 | `test<Method>_<Scenario>_<Expected>` naming convention |

**Thresholds**: 108+ = Production Ready | 96-107 = Good | 84-95 = Acceptable | <84 = Blocked

---

## TESTING GUARDRAILS (MANDATORY)

**BEFORE running tests, verify:**

| Check | Command | Why |
|-------|---------|-----|
| Org authenticated | `sf org display --target-org [alias]` | Tests need valid org connection |
| Classes deployed | `sf project deploy report --target-org [alias]` | Cannot test undeployed code |
| Test data exists | Check @TestSetup or TestDataFactory | Tests need data to operate on |

**NEVER do these:**

| Anti-Pattern | Problem | Correct Pattern |
|--------------|---------|-----------------|
| `@IsTest(SeeAllData=true)` | Tests depend on org data | Always `SeeAllData=false` (default) |
| Hardcoded Record IDs | IDs differ between orgs | Query or create in test |
| No assertions | Tests pass without validating | Assert every expected outcome |
| Single record tests only | Misses bulk trigger issues | Always test with 200+ records |
| `Test.startTest()` without `Test.stopTest()` | Async code won't execute | Always pair start/stop |
| Duplicate TestDataFactory | Maintenance burden | Use `sf-apex/templates/test-data-factory.cls` |
| `@TestVisible` on everything | Breaks encapsulation | Only for DI and true private logic |
| Ignoring UNABLE_TO_LOCK_ROW | Flaky CI/CD pipeline | Use unique values and data isolation |

---

## Common Test Failures & Fixes

| Failure | Likely Cause | Fix |
|---------|--------------|-----|
| `MIXED_DML_OPERATION` | User + non-setup in same txn | `System.runAs()` to separate transactions |
| `CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY` | Trigger or flow error | Check trigger logic with debug logs |
| `REQUIRED_FIELD_MISSING` | Test data incomplete | Add required fields to TestDataFactory |
| `DUPLICATE_VALUE` | Unique field conflict | `Crypto.getRandomLong()` for dynamic values |
| `FIELD_CUSTOM_VALIDATION_EXCEPTION` | Validation rule fired | Meet validation criteria in test data |
| `UNABLE_TO_LOCK_ROW` | Parallel record lock | Isolated data; unique values; `--synchronous` |
| `TOO_MANY_SOQL_QUERIES` | SOQL in loops | Bulkify code; check recursive triggers |
| `ENTITY_IS_DELETED` | References deleted record | Verify record lifecycle in test |

---

## CLI Command Reference

| Command | Purpose |
|---------|---------|
| `sf apex run test --class-names X` | Run specific test class |
| `sf apex run test --tests X.method` | Run specific test method |
| `sf apex run test --suite-names X` | Run test suite |
| `sf apex run test --test-level RunLocalTests` | All local tests |
| `sf apex get test --test-run-id X` | Get async test status |
| `sf apex list log` | List debug logs |
| `sf apex tail log` | Stream logs real-time |

| Flag | Purpose |
|------|---------|
| `--code-coverage` | Include coverage in results |
| `--detailed-coverage` | Line-by-line coverage |
| `--result-format json` | Machine-parseable output |
| `--output-dir` | Save results to directory |
| `--synchronous` | Wait; disables parallel execution |
| `--suite-names` | Run a named test suite |

---

## Dependencies

**Required**: Target org with `sf` CLI authenticated
**Recommended**: sf-apex, sf-data, sf-debug, salesforce-trigger-framework

---

MIT License - Copyright (c) 2024-2026 Jag Valaiyapathy
