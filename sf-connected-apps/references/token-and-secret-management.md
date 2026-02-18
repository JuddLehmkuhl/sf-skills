# Token Refresh & Consumer Secret Rotation

> Extracted from `sf-connected-apps/SKILL.md` for progressive disclosure.

## Token Refresh Strategies

### Refresh Token Policies

| Policy | Behavior | Use Case |
|--------|----------|----------|
| `infinite` | Refresh token valid until explicitly revoked | Long-running integrations, background jobs |
| `specific_lifetime` | Expires after configured duration | Regulated environments, time-bound access |
| `immediate_expiration` | Token expires immediately (no refresh) | One-time access, high-security scenarios |
| `rotate_on_each_refresh` | New refresh token issued with each use | Mobile apps, SPAs (Spring '24+) |

### Access Token Lifetime

- Default access token lifetime: **2 hours** (session timeout setting)
- Access token expiration does NOT end an active user session
- Each Connected App / ECA supports up to **5 concurrent access+refresh token pairs** per user
- When a 6th token is issued, the oldest pair is automatically revoked

### Refresh Token Flow Implementation

**Token Endpoint**: `POST https://login.salesforce.com/services/oauth2/token`
(Use `https://test.salesforce.com/services/oauth2/token` for sandboxes)

**Request Parameters**:

| Parameter | Value |
|-----------|-------|
| `grant_type` | `refresh_token` |
| `refresh_token` | The refresh token from original authorization |
| `client_id` | Consumer Key of the Connected App |
| `client_secret` | Consumer Secret (if app requires it) |

**Example curl**:
```bash
curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=refresh_token" \
  -d "refresh_token=YOUR_REFRESH_TOKEN" \
  -d "client_id=YOUR_CONSUMER_KEY" \
  -d "client_secret=YOUR_CONSUMER_SECRET"
```

**Success Response**:
```json
{
  "access_token": "00D...",
  "instance_url": "https://myorg.my.salesforce.com",
  "id": "https://login.salesforce.com/id/00D.../005...",
  "token_type": "Bearer",
  "issued_at": "1234567890",
  "signature": "..."
}
```

### Best Practices for Token Management

1. **Cache access tokens** -- Do not request a new token for every API call
2. **Handle 401 responses** -- Refresh the token when a 401 is returned, then retry
3. **Use `instance_url`** -- Always use the `instance_url` from the token response, never hardcode it
4. **Monitor token limits** -- Track active tokens per user to avoid unexpected revocations
5. **Rotate refresh tokens** -- Enable `rotate_on_each_refresh` for public clients (mobile, SPA)
6. **Store securely** -- Never store tokens in browser localStorage; use HttpOnly cookies or server-side sessions

---

## Consumer Secret Rotation

### Connected Apps (Manual Rotation)

Connected Apps require manual rotation through the Salesforce UI:

1. Navigate to **Setup > App Manager** > find the Connected App > **Manage**
2. Click **Edit Policies** > **Rotate Consumer Secret**
3. Salesforce generates a new secret; the old secret remains valid for a grace period
4. Update all external systems with the new Consumer Secret
5. Verify all integrations are working with the new secret
6. The old secret is automatically invalidated after the grace period

### External Client Apps (API-Driven Rotation)

ECAs support programmatic key and secret rotation via REST API, which is the preferred approach for automated DevOps workflows:

**Step 1: Stage a new secret** (does not invalidate the current one)
```bash
# Stage new consumer secret -- both old and new are valid during staging
sf org api POST /services/data/v62.0/external-client-apps/MY_APP/oauth-settings/rotate-secret \
  --target-org [alias]
```

**Step 2: Activate the staged secret** (invalidates the previous one)
```bash
sf org api POST /services/data/v62.0/external-client-apps/MY_APP/oauth-settings/activate-secret \
  --target-org [alias]
```

> During the staging window, both the old and new secrets are accepted for authentication requests. This allows zero-downtime rotation by updating external systems before activating.

### Rotation Schedule Recommendations

| Environment | Rotation Frequency | Rationale |
|-------------|-------------------|-----------|
| Production | Every 90 days | Security compliance, industry standard |
| Sandbox | After each refresh | Sandbox refresh resets credentials |
| After incident | Immediately | Potential compromise mitigation |
| Personnel change | Within 24 hours | Departing employees may have access |

### Rotation Checklist

1. Identify all systems consuming the Connected App / ECA credentials
2. Stage the new secret (ECA) or generate new secret (Connected App)
3. Update all external systems (secrets managers, CI/CD variables, Named Credentials)
4. Verify all integrations authenticate successfully with the new secret
5. Activate the new secret (ECA) or wait for grace period expiry (Connected App)
6. Audit login history for any failures using the old credentials
7. Document the rotation date and next scheduled rotation
