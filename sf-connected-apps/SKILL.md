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
  author: "Judd Lehmkuhl"
  scoring: "120 points across 6 categories"
  last-updated: "2026-02-18"
---

# sf-connected-apps: Salesforce Connected Apps & External Client Apps

## Core Responsibilities

1. **Connected App Generation**: Create Connected Apps with OAuth 2.0 configuration, scopes, and callbacks
2. **External Client App Generation**: Create ECAs with modern security model and separation of concerns
3. **Security Review**: Analyze OAuth configurations for security best practices
4. **Validation & Scoring**: Score apps against 6 categories (0-120 points)
5. **Migration Guidance**: Help migrate from Connected Apps to External Client Apps
6. **OAuth Troubleshooting**: Diagnose and resolve OAuth flow errors
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

**Then**: Check existing apps: `Glob: **/*.connectedApp-meta.xml`, `Glob: **/*.eca-meta.xml`

### Phase 2: App Type Selection

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
1. `~/.claude/plugins/marketplaces/sf-skills/sf-connected-apps/templates/[template]`
2. `[project-root]/sf-connected-apps/templates/[template]`

**File Locations**:
- Connected Apps: `force-app/main/default/connectedApps/`
- External Client Apps: `force-app/main/default/externalClientApps/`

### Phase 4: Security Validation & Scoring

```
Score: XX/120 Rating
|- Security: XX/30
|- OAuth Configuration: XX/25
|- Metadata Compliance: XX/20
|- Best Practices: XX/20
|- Scopes: XX/15
|- Documentation: XX/10
```

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

See `shared/docs/scoring-overview.md` for thresholds. Block deployment if score < 54.

### Phase 5: Deployment & Documentation

```
Skill(skill="sf-deploy", args="Deploy connected apps at force-app/main/default/connectedApps/ to [target-org] with --dry-run")
```

---

## Connected App Metadata Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ConnectedApp xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>My Integration App</label>
    <contactEmail>admin@company.com</contactEmail>
    <description>Integration for external system</description>
    <oauthConfig>
        <callbackUrl>https://app.example.com/oauth/callback</callbackUrl>
        <certificate>MyCertificate</certificate>
        <isAdminApproved>true</isAdminApproved>
        <scopes>Api</scopes>
        <scopes>RefreshToken</scopes>
    </oauthConfig>
    <oauthPolicy>
        <ipRelaxation>ENFORCE</ipRelaxation>
        <refreshTokenPolicy>infinite</refreshTokenPolicy>
    </oauthPolicy>
</ConnectedApp>
```

### Key Fields

| Field | Required | Description |
|-------|----------|-------------|
| `label` | Yes | Display name of the app |
| `contactEmail` | Yes | Admin contact email |
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
| Manage user data via APIs | `ManageUserData` | Manage user data (API 61+) |
| Manage user data via web browsers | `ManageUserDataWeb` | Manage user data via browser (API 61+) |

---

## External Client App Metadata Structure

> Full XML examples and field details: `Read: references/external-client-app-metadata.md`

ECA metadata is split across multiple files per app:

| Component | File Suffix | Purpose |
|-----------|-------------|---------|
| Header | `.eca-meta.xml` | Label, contact, distribution state |
| Global OAuth | `.ecaGlblOauth-meta.xml` | Callback URL, PKCE, secret settings |
| Instance OAuth | `.ecaOauth-meta.xml` | Per-org scopes |
| Policies | `.ecaPolicy-meta.xml` | IP relaxation, token policy, timeout |

**IMPORTANT**: Global OAuth file suffix is `.ecaGlblOauth` (abbreviated), NOT `.ecaGlobalOauth`.

**ECA Required Fields**: `externalClientApplication` (parent ref), `label`, `callbackUrl` (global) or `commaSeparatedOauthScopes` (instance -- NOT individual `<scopes>` tags).

| Distribution State | Use Case |
|-------------------|----------|
| `Local` | Single-org integrations |
| `Packageable` | ISV apps, multi-org (2GP) |

---

## OAuth Flow Decision Matrix

| Use Case | Recommended Flow | PKCE | Refresh Token |
|----------|-----------------|------|---------------|
| Web Server Application | Authorization Code | Optional | Yes |
| Single Page Application | Authorization Code | Required | Yes (rotate) |
| Mobile Application | Authorization Code | Required | Yes (rotate) |
| Server-to-Server | JWT Bearer | N/A | No |
| CI/CD Pipeline | JWT Bearer | N/A | No |
| Headless Service Account | Client Credentials | N/A | No |
| Device (TV, CLI) | Device Authorization | N/A | Yes |
| Legacy (avoid) | Username-Password | N/A | Yes |

> **Cross-reference**: Use `sf-diagram` to visualize flows. Templates at `sf-diagram/templates/oauth/`.

---

## Token Refresh & Secret Rotation

> Full implementation details, curl examples, and rotation checklists: `Read: references/token-and-secret-management.md`

**Refresh Token Policies**: `infinite` | `specific_lifetime` | `immediate_expiration` | `rotate_on_each_refresh`

**Key facts**:
- Default access token lifetime: 2 hours
- Max 5 concurrent token pairs per user per app (6th revokes oldest)
- JWT Bearer flow does NOT return a refresh token

**ECA secret rotation** (zero-downtime via REST API):
```bash
# Stage (both old and new valid)
sf org api POST /services/data/v62.0/external-client-apps/MY_APP/oauth-settings/rotate-secret --target-org [alias]
# Activate (old invalidated)
sf org api POST /services/data/v62.0/external-client-apps/MY_APP/oauth-settings/activate-secret --target-org [alias]
```

---

## OAuth Troubleshooting

> Full error table, flow-specific troubleshooting, and diagnostic steps: `Read: references/oauth-troubleshooting.md`

**Quick-reference errors**:

| Error | Likely Cause | Quick Fix |
|-------|-------------|-----------|
| `invalid_grant` / `authentication failure` | Bad credentials | Verify username + password + security token |
| `invalid_grant` / `no valid scopes` | Missing scopes (Winter '26+) | Add `Api` scope to Connected App |
| `invalid_client_id` | Wrong key or app not installed | Verify key; install app in target org |
| `redirect_uri_mismatch` | Callback URL mismatch | Exact match required (protocol, host, port, path) |
| `unauthorized_client` | Grant type not enabled | Enable the flow on the Connected App |

**Winter '26 Breaking Change**: Client Credentials flow now requires explicit scopes.
**Sept 2025 Change**: Connected Apps must be installed in the org.

---

## Connected App Handler Classes (ConnectedAppPlugin)

> Full Apex example, method signatures, and configuration steps: `Read: references/connected-app-handlers.md`

Handler classes customize OAuth behavior via `Auth.ConnectedAppPlugin`:

| Method | Purpose |
|--------|---------|
| `customAttributes` | Inject custom claims into ID token / introspection response |
| `authorize` | Custom authorization logic (business hours, IP checks) |
| `refresh` | Allow/deny token refresh (e.g., check user active status) |

Configure in **Setup > App Manager > [App] > Manage > Custom Connected App Handler**.

> ConnectedAppPlugin is supported only on Connected Apps, not ECAs (as of API 62.0).

---

## Security Anti-Patterns

| Anti-Pattern | Risk | Fix |
|--------------|------|-----|
| Wildcard callback URL | Token hijacking | Use specific, fully-qualified URLs |
| `Full` scope everywhere | Over-privileged access | Use minimal scopes (`Api`, `RefreshToken`) |
| No token expiration | Long-term compromise | Set expiration policy (e.g., 90 days) |
| Consumer secret in code | Credential leak | Use Named Credentials or secrets manager |
| PKCE disabled for mobile/SPA | Code interception | Enable PKCE for all public clients |
| No IP restrictions | Unauthorized access | Configure IP ranges or enforce restrictions |
| Shared Consumer Key across envs | Cross-env token leakage | Unique keys per environment |
| Infinite refresh token for public clients | Permanent access on theft | Use `rotate_on_each_refresh` |
| Hardcoded instance URL | Fails after org migration | Use `instance_url` from token response |

---

## JWT Bearer Flow Setup

> Full step-by-step with certificate generation and sf CLI auth: `Read: references/jwt-bearer-setup.md`

**Quick summary**: Generate cert/key with OpenSSL, upload cert to Connected App, pre-authorize user via Profile/PermSet, POST JWT assertion to `/services/oauth2/token`.

```bash
# sf CLI JWT auth (CI/CD)
sf org login jwt --client-id CONSUMER_KEY --jwt-key-file server.key --username user@example.com --instance-url https://login.salesforce.com --alias my-org
```

---

## Migration: Connected App to External Client App

> Full 5-step migration process: `Read: references/migration-guide.md`

**Key steps**: Assess current apps, create ECA equivalents, update integrations with new credentials, run both in parallel, deprecate old app. Note: ConnectedAppPlugin handlers cannot migrate to ECAs.

---

## Scratch Org Configuration (ECAs)

```json
{
  "orgName": "ECA Development Org",
  "edition": "Developer",
  "features": ["ExternalClientApps", "ExtlClntAppSecretExposeCtl"]
}
```

---

## Common Commands

```bash
# List Connected Apps
sf org list metadata --metadata-type ConnectedApp --target-org [alias]

# Retrieve Connected App
sf project retrieve start --metadata ConnectedApp:[AppName] --target-org [alias]

# Deploy Connected App
sf project deploy start --source-dir force-app/main/default/connectedApps --target-org [alias]

# List ECAs
sf org list metadata --metadata-type ExternalClientApplication --target-org [alias]

# Retrieve ECA (all components)
sf project retrieve start --metadata ExternalClientApplication:[AppName] \
  --metadata ExtlClntAppGlobalOauthSettings:[AppName] \
  --metadata ExtlClntAppOauthSettings:[AppName] --target-org [alias]

# Check Connected App OAuth Usage
sf data query --query "SELECT AppName, UserId, NumUses, LastUseDate FROM OAuthToken ORDER BY LastUseDate DESC LIMIT 20" --target-org [alias]
```

---

## Cross-Skill Integration

| Skill | When to Use |
|-------|-------------|
| **sf-integration** | Create Named Credentials that reference a Connected App/ECA for OAuth |
| **sf-diagram** | Visualize OAuth flows (templates at `sf-diagram/templates/oauth/`) |
| **sf-metadata** | Create Permission Sets for Connected App access |
| **sf-deploy** | Deploy Connected App or ECA metadata to org |
| **sf-apex** | Create ConnectedAppPlugin handler classes |
| **sf-testing** | Test ConnectedAppPlugin handler classes |

**Integration chain**: Connected App/ECA -> External Credential -> Named Credential -> Apex Callout

---

## Notes

- **API Version**: 62.0+ recommended, 61.0+ required for ECAs
- **Scoring**: Block deployment if score < 54
- **ECAs**: Preferred for new development (modern security model)
- **Consumer Secret**: Never commit to version control

---

## Sources

- [OAuth 2.0 JWT Bearer Flow](https://help.salesforce.com/s/articleView?id=xcloud.remoteaccess_oauth_jwt_flow.htm&language=en_US&type=5)
- [Refresh Token Flow](https://help.salesforce.com/s/articleView?id=xcloud.remoteaccess_oauth_refresh_token_flow.htm&language=en_US&type=5)
- [External Client Apps](https://help.salesforce.com/s/articleView?id=xcloud.external_client_apps.htm&language=en_US&type=5)
- [OAuth Flow Error Codes](https://help.salesforce.com/s/articleView?id=xcloud.remoteaccess_oauth_flow_errors.htm&language=en_US&type=5)
- [ConnectedAppPlugin Apex Class](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_class_Auth_ConnectedAppPlugin.htm)
- [ConnectedApp Metadata](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_connectedapp.htm)
- [ECA Key and Secret Rotation via REST API](https://lekkimworld.com/2025/09/24/salesforce-external-client-app-key-and-secret-rotation-via-rest-api/)

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2026 Jag Valaiyapathy
