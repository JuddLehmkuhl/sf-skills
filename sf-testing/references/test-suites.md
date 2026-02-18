# Test Suite Management (ApexTestSuite)

> Referenced from: `sf-testing/SKILL.md`

---

## Creating a Test Suite (Metadata)

**File path**: `force-app/main/default/testSuites/<SuiteName>.testSuite-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ApexTestSuite xmlns="http://soap.sforce.com/2006/04/metadata">
    <testClassName>TA_Lead_SetDefaults_Test</testClassName>
    <testClassName>TA_Lead_ValidateRequiredFields_Test</testClassName>
    <testClassName>LeadService_Test</testClassName>
    <testClassName>DAL_Lead_Test</testClassName>
</ApexTestSuite>
```

## Recommended Suite Organization

| Suite Name | Contents | Use Case |
|------------|----------|----------|
| `SmokeTests` | Critical path tests, one per major feature | Pre-deployment sanity check |
| `LeadTests` | All Lead-related TA_*, Service, DAL tests | After Lead changes |
| `OpportunityTests` | All Opportunity-related tests | After Opp changes |
| `IntegrationTests` | Callout mocks, platform event tests | After integration changes |
| `FullRegression` | All test classes | Release validation |

## Running Suites

```bash
# Run a named test suite
sf apex run test --suite-names LeadTests --code-coverage --result-format json --target-org [alias]

# Run multiple suites
sf apex run test --suite-names LeadTests --suite-names OpportunityTests --code-coverage --result-format json --target-org [alias]
```

## Deploying Test Suites

```bash
sf project deploy start --source-dir force-app/main/default/testSuites --target-org [alias]
```

## CI/CD Best Practice

Run only the tests that cover changed components:

```bash
# After changing Lead trigger actions, run only Lead suite
sf apex run test --suite-names LeadTests --code-coverage --result-format json --target-org [alias]

# For full deployment validation, run all local tests
sf apex run test --test-level RunLocalTests --code-coverage --result-format json --target-org [alias]
```
