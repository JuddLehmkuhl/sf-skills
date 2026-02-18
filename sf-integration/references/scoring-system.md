# Integration Scoring System (120 Points)

## Category Breakdown

| Category | Points | Evaluation Criteria |
|----------|--------|---------------------|
| **Security** | 30 | Named Credentials used (no hardcoded secrets), OAuth scopes minimized, certificate auth where applicable, mTLS for high-security |
| **Error Handling** | 25 | Retry logic present, timeout handling (120s max), specific exception types, logging implemented, circuit breaker for critical integrations |
| **Bulkification** | 20 | Batch callouts considered, CDC bulk handling, event batching for Platform Events |
| **Architecture** | 20 | Async patterns for DML-triggered callouts, proper service layer separation, single responsibility |
| **Best Practices** | 15 | Governor limit awareness, proper HTTP methods, idempotency for retries, rate limit handling |
| **Testing** | 10 | HttpCalloutMock implemented, error scenarios covered, 95%+ coverage, WebServiceMock for SOAP |

## Scoring Thresholds

```
Score: XX/120 Rating
  108-120  Excellent:  Production-ready, follows all best practices
   90-107  Very Good:  Minor improvements suggested
   72-89   Good:       Acceptable with noted improvements
   54-71   Needs Work: Address issues before deployment
    <54    Block:      CRITICAL issues, do not deploy
```

## Scoring Output Format

```
INTEGRATION SCORE: XX/120 Rating
================================================

Security           XX/30  ||||||||..  XX%
  Named Credentials used: [Y/N]
  No hardcoded secrets: [Y/N]
  OAuth scopes minimal: [Y/N]
  mTLS where required: [Y/N]

Error Handling     XX/25  ||||||||..  XX%
  Retry logic: [Y/N]
  Timeout handling: [Y/N]
  Circuit breaker: [Y/N]
  Logging: [Y/N]

Bulkification      XX/20  ||||||||..  XX%
  Batch callouts: [Y/N]
  Event batching: [Y/N]

Architecture       XX/20  ||||||||..  XX%
  Async patterns: [Y/N]
  Service separation: [Y/N]

Best Practices     XX/15  ||||||||..  XX%
  Governor limits: [Y/N]
  Idempotency: [Y/N]
  Rate limiting: [Y/N]

Testing            XX/10  ||||||||..  XX%
  HttpCalloutMock: [Y/N]
  Error scenarios: [Y/N]
  95%+ coverage: [Y/N]

================================================
```
