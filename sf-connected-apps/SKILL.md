---
name: sf-connected-apps
description: >
  Creates and manages Salesforce Connected Apps and External Client Apps with
  120-point scoring. Use when configuring OAuth flows, creating connected apps,
  setting up JWT bearer auth, managing API access policies, troubleshooting
  OAuth errors, or rotating consumer secrets.
license: MIT
allowed-tools: Bash Read Write Edit Glob Grep WebFetch AskUserQuestion TodoWrite
metadata:
  version: "2.0.0"
  author: "Jag Valaiyapathy"
  scoring: "120 points across 6 categories"
  last-updated: "2026-02-18"
---

# sf-connected-apps: Salesforce Connected Apps & External Client Apps

Expert in creating and managing Salesforce Connected Apps and External Client Apps (ECAs) with OAuth configuration, security best practices, troubleshooting, and metadata compliance.

## Core Responsibilities

1. **Connected App Generation**: Create Connected Apps with OAuth 2.0 configuration, scopes, and callbacks
2. **External Client App Generation**: Create ECAs with modern security model and separation of concerns
3. **Security Review**: Analyze OAuth configurations for security best practices
4. **Validation & Scoring**: Score apps against 6 categories (0-120 points)
5. **Migration Guidance**: Help migrate from Connected Apps to External Client Apps
6. **OAuth Troubleshooting**: Diagnose and resolve OAuth flow errors (invalid_grant, redirect_uri_mismatch, etc.)
7. **Secret Rotation**: Manage consumer key/secret lifecycle and rotation procedures

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:

| # | Question | Options |
|---|----------|---------|
| 1 | App Type | Connected App / External Client App |
| 2 | OAuth Flow | Web Server (Authorization Code), User-Agent, JWT Bearer, Device, Client Credentials, Refresh Token |
| 3 | Primary Use Case | API Integration, SSO, Canvas App, Mobile App, CI/CD |
| 4 | Scopes Required | api, refresh_token, full, web, chatter_api, etc. |
| 5 | Distribution | Local (single org) / Packageable (multi-org) |

**Then**:
1. Check existing apps: `Glob: **/*.connectedApp-meta.xml`, `Glob: **/*.eca-meta.xml`
2. Check for existing OAuth configurations
3. Create TodoWrite tasks

### Phase 2: App Type Selection

**Decision Matrix**:

| Criteria | Connected App | External Client App (ECA) |
|----------|--------------|--------------------------|
| Single Org | Good | Good |
| Multi-Org Distribution | Manual recreation | Native packaging (2GP) |
| Secret Management | Visible in sandboxes | Hidden in sandboxes |
| Key Rotation | Manual (UI only) | Automatable via REST API |
| Metadata Compliance | Partial | Full |
| Audit Trail | Limited | MFA + audit logging |
| Setup Complexity | Low | Medium |
| Minimum API Version | Any | 61.0+ |
| Custom Handler Classes | Supported | Not yet supported |

**Recommendation Logic**:
- **Multi-org or ISV**: Always use External Client App
- **Regulated industry**: Use External Client App (audit requirements)
- **Simple single-org**: Connected App is sufficient
- **Automated DevOps**: Use External Client App (key rotation via API)
- **Custom login flows needed**: Connected App (handler classes required)

### Phase 3: Template Selection & Generation

**Select template based on app type**:

| App Type | Template File |
|----------|---------------|
| Connected App (Basic) | `templates/connected-app-basic.xml` |
| Connected App (Full OAuth) | `templates/connected-app-oauth.xml` |
| Connected App (JWT Bearer) | `templates/connected-app-jwt.xml` |
| Connected App (Canvas) | `templates/connected-app-canvas.xml` |
| External Client App | `templates/external-client-app.xml` |
| ECA Global OAuth | `templates/eca-global-oauth.xml` |
| ECA OAuth Settings | `templates/eca-oauth-settings.xml` |
| ECA Policies | `templates/eca-policies.xml` |

**Template Path Resolution** (try in order):
1. **Marketplace folder**: `~/.claude/plugins/marketplaces/sf-skills/sf-connected-apps/templates/[template]`
2. **Project folder**: `[project-root]/sf-connected-apps/templates/[template]`

**Example**: `Read: ~/.claude/plugins/marketplaces/sf-skills/sf-connected-apps/templates/connected-app-jwt.xml`

**File Locations**:
- Connected Apps: `force-app/main/default/connectedApps/`
- External Client Apps: `force-app/main/default/externalClientApps/`

### Phase 4: Security Validation & Scoring

**Run Validation**:
```
Score: XX/120 Rating
|- Security: XX/30
|- OAuth Configuration: XX/25
|- Metadata Compliance: XX/20
|- Best Practices: XX/20
|- Scopes: XX/15
|- Documentation: XX/10
```

**Scoring Criteria**:

#### Security (30 points)
- PKCE enabled for public clients (+10)
- Refresh token rotation enabled (+5)
- IP restrictions configured (+5)
- Certificate-based auth where applicable (+5)
- No wildcard callback URLs (+5)

#### OAuth Configuration (25 points)
- Valid callback URLs (+10)
- Appropriate OAuth flow for use case (+5)
- Token expiration configured (+5)
- ID token enabled for OpenID Connect (+5)

#### Metadata Compliance (20 points)
- All required fields present (+10)
- Valid API version (+5)
- Proper file naming convention (+5)

#### Best Practices (20 points)
- Minimal scopes (least privilege) (+10)
- Named Principal for integrations (+5)
- Admin pre-authorization configured (+5)

#### Scopes (15 points)
- Only necessary scopes selected (+10)
- No deprecated scopes (+5)

#### Documentation (10 points)
- Description provided (+5)
- Contact email valid (+5)

### Scoring Thresholds

See `shared/docs/scoring-overview.md` (project root). Block deployment if score < 54.

### Phase 5: Deployment & Documentation

**Deployment**:
```
Skill(skill="sf-deploy", args="Deploy connected apps at force-app/main/default/connectedApps/ to [target-org] with --dry-run")
```

**Completion Summary**:
```
App Created: [AppName]
  Type: [Connected App | External Client App]
  API: 62.0
  Location: force-app/main/default/[connectedApps|externalClientApps]/[AppName].*
  OAuth Flow: [flow type]
  Scopes: [scope list]
  Validation: PASSED (Score: XX/120)

Next Steps:
- For Connected App: Retrieve Consumer Key from Setup after deployment
- For ECA: Configure policies in subscriber org
- Test OAuth flow with Postman or curl
```

---

## Connected App Metadata Structure

### ConnectedApp XML Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ConnectedApp xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>My Integration App</label>
    <contactEmail>admin@company.com</contactEmail>
    <description>Integration for external system</description>

    <!-- OAuth Configuration -->
    <oauthConfig>
        <callbackUrl>https://app.example.com/oauth/callback</callbackUrl>
        <certificate>MyCertificate</certificate>
        <consumerKey>AUTO_GENERATED</consumerKey>
        <isAdminApproved>true</isAdminApproved>
        <isConsumerSecretOptional>false</isConsumerSecretOptional>
        <isIntrospectAllTokens>false</isIntrospectAllTokens>
        <scopes>Api</scopes>
        <scopes>RefreshToken</scopes>
    </oauthConfig>

    <!-- OAuth Policy -->
    <oauthPolicy>
        <ipRelaxation>ENFORCE</ipRelaxation>
        <refreshTokenPolicy>infinite</refreshTokenPolicy>
    </oauthPolicy>

    <!-- Custom Connected App Handler (optional) -->
    <plugin>MyConnectedAppPlugin</plugin>
</ConnectedApp>
```

### Key Fields

| Field | Required | Description |
|-------|----------|-------------|
| `label` | Yes | Display name of the app |
| `contactEmail` | Yes | Admin contact email |
| `description` | No | App description |
| `oauthConfig` | No | OAuth settings (required for API access) |
| `oauthPolicy` | No | Token and IP policies |
| `samlConfig` | No | SAML SSO settings |
| `canvasConfig` | No | Canvas app settings |
| `plugin` | No | Custom ConnectedAppPlugin Apex class name |

### OAuth Scopes Reference

| Scope | API Name | Description |
|-------|----------|-------------|
| Access and manage your data | `Api` | REST/SOAP API access |
| Perform requests at any time | `RefreshToken` | Offline access via refresh token |
| Full access | `Full` | Complete access (use sparingly) |
| Access your basic information | `OpenID` | OpenID Connect |
| Web access | `Web` | Access via web browser |
| Access Chatter | `ChatterApi` | Chatter REST API |
| Access custom permissions | `CustomPermissions` | Custom permission access |
| Access Einstein Analytics | `Wave` | Analytics API access |
| Content access | `Content` | Content delivery |
| Access custom applications | `VisualForce` | Visualforce pages |
| Manage user data via APIs | `ManageUserData` | Manage user data (API 61+) |
| Manage user data via web browsers | `ManageUserDataWeb` | Manage user data via browser (API 61+) |

---

## External Client App Metadata Structure

### ExternalClientApplication (Header File)

**File**: `[AppName].eca-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExternalClientApplication xmlns="http://soap.sforce.com/2006/04/metadata">
    <contactEmail>admin@company.com</contactEmail>
    <description>External integration with modern security</description>
    <distributionState>Local</distributionState>
    <iconUrl>https://example.com/icon.png</iconUrl>
    <isProtected>false</isProtected>
    <label>My External Client App</label>
    <logoUrl>https://example.com/logo.png</logoUrl>
</ExternalClientApplication>
```

### ExtlClntAppGlobalOauthSettings (Global OAuth)

**File**: `[AppName].ecaGlblOauth-meta.xml`

> **IMPORTANT**: File suffix is `.ecaGlblOauth` (abbreviated), NOT `.ecaGlobalOauth`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExtlClntAppGlobalOauthSettings xmlns="http://soap.sforce.com/2006/04/metadata">
    <callbackUrl>https://app.example.com/oauth/callback</callbackUrl>
    <externalClientApplication>My_App_Name</externalClientApplication>
    <isConsumerSecretOptional>false</isConsumerSecretOptional>
    <isIntrospectAllTokens>false</isIntrospectAllTokens>
    <isPkceRequired>true</isPkceRequired>
    <isSecretRequiredForRefreshToken>true</isSecretRequiredForRefreshToken>
    <label>My App Global OAuth Settings</label>
    <shouldRotateConsumerKey>false</shouldRotateConsumerKey>
    <shouldRotateConsumerSecret>false</shouldRotateConsumerSecret>
</ExtlClntAppGlobalOauthSettings>
```

**ECA Required Fields** (both GlobalOauth and OauthSettings):
- `externalClientApplication` - Reference to parent ECA (must match .eca file name)
- `label` - Display label
- Global: `callbackUrl` | Instance: `commaSeparatedOauthScopes` (NOT individual `<scopes>` tags)

### ExtlClntAppOauthSettings (Instance OAuth)

**File**: `[AppName].ecaOauth-meta.xml`

> **Note**: OAuth flows are configured via Admin UI or `ExtlClntAppConfigurablePolicies`.

### ExtlClntAppConfigurablePolicies (Admin Policies)

**File**: `[AppName].ecaPolicy-meta.xml` (auto-generated, admin-configurable)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExtlClntAppConfigurablePolicies xmlns="http://soap.sforce.com/2006/04/metadata">
    <ipRelaxation>ENFORCE</ipRelaxation>
    <refreshTokenPolicy>infinite</refreshTokenPolicy>
    <sessionTimeout>120</sessionTimeout>
</ExtlClntAppConfigurablePolicies>
```

### ECA Distribution States

| State | Description | Use Case |
|-------|-------------|----------|
| `Local` | Available only in creating org | Development, single-org integrations |
| `Packageable` | Can be included in 2GP packages | ISV apps, multi-org distribution |

---

## OAuth Flow Decision Matrix

| Use Case | Recommended Flow | PKCE | Refresh Token | Handler Class |
|----------|-----------------|------|---------------|---------------|
| Web Server Application | Authorization Code | Optional | Yes | Optional |
| Single Page Application | Authorization Code | Required | Yes (rotate) | N/A |
| Mobile Application | Authorization Code | Required | Yes (rotate) | Optional |
| Server-to-Server | JWT Bearer | N/A | No | N/A |
| CI/CD Pipeline | JWT Bearer | N/A | No | N/A |
| Headless Service Account | Client Credentials | N/A | No | N/A |
| Device (TV, CLI) | Device Authorization | N/A | Yes | N/A |
| Legacy (avoid) | Username-Password | N/A | Yes | N/A |

> **Cross-reference**: Use `sf-diagram` to visualize any of these flows. Templates exist for Authorization Code, JWT Bearer, Client Credentials, Device, and Refresh Token flows. See `sf-diagram/templates/oauth/`.

---

## Token Refresh Strategies

### Refresh Token Policies

Configure refresh token behavior in the Connected App or ECA policy settings:

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

---

## OAuth Troubleshooting

### Common OAuth Errors

| Error Code | Error Description | Common Cause | Fix |
|------------|-------------------|--------------|-----|
| `invalid_grant` | `authentication failure` | Wrong username, password, or security token | Verify credentials; append security token to password if IP not whitelisted |
| `invalid_grant` | `no valid scopes defined` | Connected App missing required OAuth scopes (enforced Winter '26+) | Add at least one valid OAuth scope to the Connected App (e.g., `Api`) |
| `invalid_grant` | `expired access/refresh token` | Refresh token revoked or expired per policy | Re-authorize the user; check refresh token policy setting |
| `invalid_grant` | `user hasn't approved this consumer` | User has not authorized the Connected App | Set policy to "All users may self-authorize" or pre-authorize via Permission Sets |
| `invalid_grant` | `ip restricted` | Request IP not in Connected App's trusted IP range | Add the calling IP to the Connected App's IP restrictions, or set IP Relaxation to "Relax IP restrictions" |
| `invalid_client_id` | `client identifier invalid` | Wrong Consumer Key or app not installed in org | Verify Consumer Key; ensure the Connected App is installed in the target org |
| `invalid_client` | `invalid client credentials` | Wrong Consumer Secret | Verify Consumer Secret; check if it was recently rotated |
| `redirect_uri_mismatch` | `redirect_uri must match configuration` | Callback URL in request does not match Connected App | Ensure the `redirect_uri` parameter exactly matches a callback URL configured in the Connected App (protocol, host, port, path) |
| `invalid_scope` | `the requested scope is invalid` | Requesting scopes not enabled on the Connected App | Add the requested scopes to the Connected App's OAuth configuration |
| `unsupported_response_type` | N/A | Using a response_type not supported by the Connected App | Verify the OAuth flow matches the Connected App configuration (e.g., `code` for Authorization Code flow) |
| `unauthorized_client` | N/A | Connected App not authorized for this grant type | Enable the appropriate OAuth flow on the Connected App |
| `access_denied` | `end-user denied authorization` | User clicked "Deny" on the OAuth consent screen | User must click "Allow"; verify the app is trusted |
| `inactive_user` | N/A | The Salesforce user is deactivated or frozen | Reactivate or unfreeze the user in Setup |
| `inactive_org` | N/A | The Salesforce org is locked or inactive | Contact Salesforce Support to restore the org |

### Winter '26 Scope Enforcement (October 2025)

Salesforce tightened OAuth scope enforcement in Winter '26. The `/services/oauth2/token` endpoint now **rejects** any Client Credentials flow request that does not include at least one supported scope. Previously, Salesforce might issue an opaque access token even without valid scopes.

**Impact**: Integrations using Client Credentials flow that previously worked without explicitly specifying scopes will receive `invalid_grant` with `no valid scopes defined`.

**Fix**: Add the required scopes both to the Connected App definition and to the token request.

### Connected App Installation Requirement (September 2025)

Since September 2025, Connected Apps must either be:
- **Installed** into the org (via "Install" button in Setup > Connected Apps > Manage Connected Apps), OR
- The user must have special permissions to use uninstalled Connected Apps

**Symptom**: `invalid_client_id` error even though the Consumer Key is correct.

**Fix**: Navigate to **Setup > Connected Apps > Manage Connected Apps** and install the Connected App.

### JWT Bearer Flow Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `invalid_grant` on JWT token request | Certificate mismatch | Ensure the certificate uploaded to the Connected App matches the private key signing the JWT |
| `invalid_grant` with `user not found` | Wrong `sub` claim in JWT | Use the Salesforce username (not email) in the `sub` field |
| `invalid_grant` with `audience` error | Wrong `aud` claim | Use `https://login.salesforce.com` or `https://test.salesforce.com` (not instance URL) |
| `invalid_grant` after sandbox refresh | Sandbox URL changed | Update the `aud` claim to `https://test.salesforce.com` and verify the user exists in the sandbox |
| Token request times out | Network/firewall blocking | Ensure outbound HTTPS (port 443) to login.salesforce.com is allowed |
| `invalid_client_id` | App not pre-authorized for user | Pre-authorize the Connected App for the user's profile or permission set |

### Client Credentials Flow Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `invalid_grant` | No "Run As" user assigned | Assign a user in the Connected App's "Run As" field under Client Credentials |
| `invalid_grant` with `no valid scopes` | Missing scopes (Winter '26+) | Add `Api` or other required scopes to the Connected App |
| `unauthorized_client` | Client Credentials flow not enabled | Enable "Enable Client Credentials Flow" in the Connected App's OAuth settings |
| Insufficient permissions | Run As user lacks object access | Grant the Run As user the necessary Permission Sets and object permissions |

### Diagnostic Steps

When an OAuth error occurs, follow this sequence:

1. **Check the error response body** -- Parse the JSON for `error` and `error_description`
2. **Verify the Connected App status** -- Is it active? Is it installed in the target org?
3. **Check the user status** -- Is the user active, unfrozen, and has login access?
4. **Verify credentials** -- Consumer Key, Consumer Secret, callback URL (exact match)
5. **Check IP restrictions** -- Is the calling IP allowed?
6. **Review login history** -- Setup > Login History shows failed attempts with reason codes
7. **Check Connected App login history** -- Setup > Connected Apps OAuth Usage
8. **Verify scopes** -- Do the requested scopes match what is configured on the Connected App?
9. **Test with minimal request** -- Use curl to isolate the issue from application code
10. **Check Salesforce Trust** -- Visit https://status.salesforce.com for platform issues

---

## Connected App Handler Classes (ConnectedAppPlugin)

### Overview

The `Auth.ConnectedAppPlugin` Apex class allows you to customize Connected App behavior during OAuth flows. Use handler classes to inject custom claims into tokens, control authorization logic, or implement custom login experiences.

### When to Use

- Inject custom attributes (claims) into ID tokens or introspection responses
- Implement custom authorization logic beyond standard OAuth
- Customize token refresh behavior
- Add org-specific data to OAuth responses without follow-up API calls
- Build custom login flows for community/Experience Cloud users

### ConnectedAppPlugin Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `authorize` | `Auth.AuthProviderTokenResponse authorize(Id userId, Id connectedAppId, Boolean isAdminApproved, Auth.InvocationContext context)` | Called during the authorization phase. Override to implement custom authorization logic. |
| `customAttributes` | `Map<String, String> customAttributes(Id userId, Id connectedAppId, Map<String, String> formulaDefinedAttributes, Auth.InvocationContext context)` | Returns custom attributes to include in the OAuth response or ID token. |
| `refresh` | `Boolean refresh(Id userId, Id connectedAppId, Auth.InvocationContext context)` | Called when a token refresh is requested. Return `true` to allow the refresh, `false` to deny it. |

### Example: Custom Claims Plugin

```apex
/**
 * ConnectedAppPlugin that injects custom attributes into the OAuth response.
 * Assign this class in Connected App > Manage > Custom Connected App Handler.
 */
public class CustomClaimsPlugin extends Auth.ConnectedAppPlugin {

    /**
     * Inject custom attributes (claims) into the ID token / introspection response.
     */
    public override Map<String, String> customAttributes(
        Id userId,
        Id connectedAppId,
        Map<String, String> formulaDefinedAttributes,
        Auth.InvocationContext context
    ) {
        // Start with existing formula-defined attributes
        Map<String, String> attrs = new Map<String, String>(formulaDefinedAttributes);

        // Query additional user data
        User u = [
            SELECT Id, Department, Title, Contact.Account.Name
            FROM User
            WHERE Id = :userId
            LIMIT 1
        ];

        // Add custom claims
        attrs.put('department', u.Department);
        attrs.put('title', u.Title);
        if (u.Contact?.Account?.Name != null) {
            attrs.put('company', u.Contact.Account.Name);
        }

        return attrs;
    }

    /**
     * Custom authorization logic. Return null to use default behavior.
     */
    public override Auth.AuthProviderTokenResponse authorize(
        Id userId,
        Id connectedAppId,
        Boolean isAdminApproved,
        Auth.InvocationContext context
    ) {
        // Return null for default authorization behavior
        // Override to implement custom checks (e.g., business hours, IP ranges)
        return null;
    }

    /**
     * Control refresh token behavior.
     * Return true to allow refresh, false to deny.
     */
    public override Boolean refresh(
        Id userId,
        Id connectedAppId,
        Auth.InvocationContext context
    ) {
        // Example: Deny refresh for inactive department users
        User u = [SELECT IsActive, Department FROM User WHERE Id = :userId LIMIT 1];
        return u.IsActive;
    }
}
```

### Configuring the Handler

1. Deploy the Apex class to the org
2. Navigate to **Setup > App Manager** > find the Connected App > **Manage**
3. Under **Custom Connected App Handler**:
   - **Apex Plugin Class**: Enter the class name (e.g., `CustomClaimsPlugin`)
   - **Run As**: Select the user context for the plugin execution
4. Save and test the OAuth flow

### Handler Class Best Practices

- Always call `super` or return defaults for methods you do not customize
- Keep SOQL queries minimal (governor limits apply)
- Cache results when possible to avoid redundant queries on token refresh
- Test thoroughly: handler errors can block all OAuth flows for the Connected App
- Use Custom Metadata Types for configurable behavior instead of hardcoding

> **Note**: ConnectedAppPlugin handler classes are supported only on Connected Apps, not on External Client Apps (as of API 62.0).

---

## Security Best Practices

> Scoring details: See Phase 4 Scoring Criteria above for point breakdown.

### Anti-Patterns

| Anti-Pattern | Risk | Fix |
|--------------|------|-----|
| Wildcard callback URL | Token hijacking | Use specific, fully-qualified URLs |
| `Full` scope everywhere | Over-privileged access | Use minimal scopes (`Api`, `RefreshToken`) |
| No token expiration | Long-term compromise | Set expiration policy (e.g., 90 days) |
| Consumer secret in code | Credential leak | Use Named Credentials or secrets manager |
| PKCE disabled for mobile/SPA | Authorization code interception | Enable PKCE for all public clients |
| No IP restrictions | Unauthorized access from any location | Configure IP ranges or use "Enforce IP restrictions" |
| Shared Consumer Key across environments | Cross-environment token leakage | Generate unique keys per environment |
| Infinite refresh token for public clients | Token theft leads to permanent access | Use `rotate_on_each_refresh` policy |
| Hardcoded instance URL | Fails after org migration | Use `instance_url` from token response |
| No login history monitoring | Missed breach detection | Review Connected App OAuth Usage regularly |

---

## Scratch Org Configuration

For **External Client Apps**, add these features to your scratch org definition:

```json
{
  "orgName": "ECA Development Org",
  "edition": "Developer",
  "features": [
    "ExternalClientApps",
    "ExtlClntAppSecretExposeCtl"
  ],
  "settings": {
    "securitySettings": {
      "enableAdminLoginAsAnyUser": true
    }
  }
}
```

---

## Cross-Skill Integration

| Skill | When to Use | Example |
|-------|-------------|---------|
| **sf-integration** | Create Named Credentials that depend on a Connected App for OAuth auth | `Skill(skill="sf-integration")` -- "Create Named Credential using JWT Bearer Connected App" |
| **sf-diagram** | Visualize OAuth flows for documentation or architecture review | `Skill(skill="sf-diagram")` -- "Generate JWT Bearer Flow sequence diagram" |
| **sf-metadata** | Create Named Credentials or Permission Sets for Connected App access | `Skill(skill="sf-metadata")` -- "Create Permission Set for Connected App access" |
| **sf-deploy** | Deploy Connected App or ECA metadata to org | `Skill(skill="sf-deploy", args="Deploy to [org]")` |
| **sf-apex** | Create Apex for ConnectedAppPlugin handler classes or token management | `Skill(skill="sf-apex")` -- "Create ConnectedAppPlugin handler class" |
| **sf-testing** | Test ConnectedAppPlugin handler classes | `Skill(skill="sf-testing")` -- "Run tests for CustomClaimsPlugin" |

### Integration with sf-integration (Named Credentials)

Connected Apps and ECAs are the authentication foundation for Named Credentials. The relationship is:

```
Connected App (defines OAuth config, scopes, policies)
  |
  +-- External Credential (references Connected App for auth)
        |
        +-- Named Credential (endpoint URL + External Credential)
              |
              +-- Apex Callout / External Service (uses Named Credential)
```

When creating an integration, always:
1. Create the Connected App / ECA first (this skill)
2. Then create the External Credential and Named Credential (`sf-integration`)
3. Then create the Apex callout code (`sf-apex` + `sf-integration`)

### Integration with sf-diagram (OAuth Flow Visualization)

The `sf-diagram` skill has pre-built Mermaid templates for all major OAuth flows:

| Flow | Template Path |
|------|---------------|
| Authorization Code | `sf-diagram/templates/oauth/authorization-code.md` |
| Authorization Code + PKCE | `sf-diagram/templates/oauth/authorization-code-pkce.md` |
| JWT Bearer | `sf-diagram/templates/oauth/jwt-bearer.md` |
| Client Credentials | `sf-diagram/templates/oauth/client-credentials.md` |
| Device Authorization | `sf-diagram/templates/oauth/device-authorization.md` |
| Refresh Token | `sf-diagram/templates/oauth/refresh-token.md` |

Use these when documenting integration architecture or explaining OAuth flows to stakeholders.

---

## Migration: Connected App to External Client App

**Step 1: Assess Current State**
```
Glob: **/*.connectedApp-meta.xml
```
Review existing Connected Apps and their configurations.

**Step 2: Create ECA Equivalent**
- Map OAuth settings to ECA structure
- Create all required ECA metadata files (`.eca`, `.ecaGlblOauth`, `.ecaOauth`, `.ecaPolicy`)
- Set `distributionState` based on needs
- Note: ConnectedAppPlugin handler classes cannot be migrated to ECAs

**Step 3: Update Integrations**
- Generate new Consumer Key/Secret
- Update Named Credentials to reference the new ECA
- Update external systems with new credentials
- Test OAuth flows in sandbox before production

**Step 4: Parallel Run**
- Keep both Connected App and ECA active during transition
- Monitor both apps' login history for any issues
- Gradually migrate external systems to the ECA

**Step 5: Deprecate Old App**
- Remove from Connected App policies
- Revoke all active tokens for the old Connected App
- Archive or delete Connected App metadata

---

## Common Commands

**List Connected Apps in Org**:
```bash
sf org list metadata --metadata-type ConnectedApp --target-org [alias]
```

**Retrieve Connected App**:
```bash
sf project retrieve start --metadata ConnectedApp:[AppName] --target-org [alias]
```

**Deploy Connected App**:
```bash
sf project deploy start --source-dir force-app/main/default/connectedApps --target-org [alias]
```

**List External Client Apps in Org**:
```bash
sf org list metadata --metadata-type ExternalClientApplication --target-org [alias]
```

**Retrieve External Client App (all components)**:
```bash
sf project retrieve start --metadata ExternalClientApplication:[AppName] \
  --metadata ExtlClntAppGlobalOauthSettings:[AppName] \
  --metadata ExtlClntAppOauthSettings:[AppName] \
  --target-org [alias]
```

**Check Connected App OAuth Usage**:
```bash
sf data query --query "SELECT AppName, UserId, NumUses, LastUseDate FROM OAuthToken ORDER BY LastUseDate DESC LIMIT 20" --target-org [alias]
```

---

## JWT Bearer Flow Setup (Step-by-Step)

### Prerequisites
- Admin access to create Connected Apps
- OpenSSL for certificate generation (or use Salesforce Certificate and Key Management)

### Step 1: Generate Certificate and Private Key

```bash
# Generate private key
openssl genrsa -out server.key 2048

# Generate certificate (self-signed, valid 1 year)
openssl req -new -x509 -key server.key -out server.crt -days 365 \
  -subj "/CN=MyIntegration/O=MyCompany/C=US"
```

### Step 2: Create Connected App

1. Setup > App Manager > New Connected App
2. Enable OAuth Settings
3. Callback URL: `https://login.salesforce.com/services/oauth2/callback` (or `https://oauthdebugger.com/debug` for testing)
4. Check "Use digital signatures" and upload `server.crt`
5. Select scopes: `Api`, `RefreshToken` (or `Full` if absolutely necessary)
6. Save

### Step 3: Pre-Authorize the User

1. Setup > App Manager > find the app > Manage
2. Under Profiles or Permission Sets, add the integration user's profile/perm set
3. Set IP Relaxation policy as needed

### Step 4: Request Access Token

```bash
# Create JWT assertion
# iss = Consumer Key
# sub = Salesforce username
# aud = login URL
# exp = expiration (max 5 minutes from now)

curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer" \
  -d "assertion=YOUR_JWT_ASSERTION"
```

> **Note**: JWT Bearer flow does NOT return a refresh token. When the access token expires, generate and sign a new JWT to obtain a fresh access token.

### Step 5: Verify in sf CLI (for CI/CD)

```bash
# Authenticate sf CLI using JWT
sf org login jwt \
  --client-id YOUR_CONSUMER_KEY \
  --jwt-key-file server.key \
  --username user@example.com \
  --instance-url https://login.salesforce.com \
  --alias my-org
```

---

## Notes

- **API Version**: 62.0+ recommended, 61.0+ required for External Client Apps
- **Scoring**: Block deployment if score < 54
- **External Client Apps**: Preferred for new development (modern security model)
- **Consumer Secret**: Never commit to version control
- **Winter '26 Breaking Change**: Client Credentials flow now requires explicit scopes
- **Connected App Installation**: Required since September 2025 for non-installed apps

---

## Sources

- [Salesforce Help: OAuth 2.0 JWT Bearer Flow](https://help.salesforce.com/s/articleView?id=xcloud.remoteaccess_oauth_jwt_flow.htm&language=en_US&type=5)
- [Salesforce Help: Refresh Token Flow](https://help.salesforce.com/s/articleView?id=xcloud.remoteaccess_oauth_refresh_token_flow.htm&language=en_US&type=5)
- [Salesforce Help: External Client Apps](https://help.salesforce.com/s/articleView?id=xcloud.external_client_apps.htm&language=en_US&type=5)
- [Salesforce Help: Configure a JWT Bearer Flow (ECA)](https://help.salesforce.com/s/articleView?id=xcloud.configure_oauth_jwt_flow_external_client_apps.htm&language=en_US&type=5)
- [Salesforce Help: Manage OAuth Access Policies](https://help.salesforce.com/s/articleView?id=sf.connected_app_manage_oauth.htm&language=en_US&type=5)
- [Salesforce Help: Create a Custom Connected App Handler](https://help.salesforce.com/s/articleView?id=sf.connected_app_create_custom_handler.htm&language=en_US&type=5)
- [Salesforce Help: Configure Packageable External Client Apps](https://help.salesforce.com/s/articleView?id=sf.configure_packageable_external_client_apps.htm&language=en_US&type=5)
- [Salesforce Help: OAuth Flow Error Codes](https://help.salesforce.com/s/articleView?id=xcloud.remoteaccess_oauth_flow_errors.htm&language=en_US&type=5)
- [Salesforce Developers: ConnectedAppPlugin Apex Class](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_class_Auth_ConnectedAppPlugin.htm)
- [Salesforce Developers: Authorize Org Using JWT Flow](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_auth_jwt_flow.htm)
- [Salesforce Developers: ConnectedApp Metadata](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_connectedapp.htm)
- [Salesforce Ben: External Client vs Connected Apps](https://www.salesforceben.com/external-client-vs-connected-apps-comparing-salesforces-next-gen-integration/)
- [Trailhead: Build Integrations with External Client Apps](https://trailhead.salesforce.com/content/learn/projects/build-integrations-with-external-client-apps/create-and-configure-an-external-client-app)
- [Trailhead: Create an External Client App Using Metadata API](https://trailhead.salesforce.com/content/learn/projects/create-an-external-client-app-using-metadata-api/create-an-external-client-app)
- [Salesforce Security Advisory: Connected App Restrictions (Oct 2025)](https://www.concret.io/blog/salesforce-connected-app-restrictions-oct-2025)
- [ECA Key and Secret Rotation via REST API](https://lekkimworld.com/2025/09/24/salesforce-external-client-app-key-and-secret-rotation-via-rest-api/)
- [Salesforce Release Notes: Rotate Consumer Key and Secret](https://help.salesforce.com/s/articleView?id=release-notes.rn_security_consumer_details_rotate.htm&language=en_US&release=238&type=5)

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2026 Jag Valaiyapathy
