# OAuth Troubleshooting

> Extracted from `sf-connected-apps/SKILL.md` for progressive disclosure.

## Common OAuth Errors

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

## Winter '26 Scope Enforcement (October 2025)

Salesforce tightened OAuth scope enforcement in Winter '26. The `/services/oauth2/token` endpoint now **rejects** any Client Credentials flow request that does not include at least one supported scope. Previously, Salesforce might issue an opaque access token even without valid scopes.

**Impact**: Integrations using Client Credentials flow that previously worked without explicitly specifying scopes will receive `invalid_grant` with `no valid scopes defined`.

**Fix**: Add the required scopes both to the Connected App definition and to the token request.

## Connected App Installation Requirement (September 2025)

Since September 2025, Connected Apps must either be:
- **Installed** into the org (via "Install" button in Setup > Connected Apps > Manage Connected Apps), OR
- The user must have special permissions to use uninstalled Connected Apps

**Symptom**: `invalid_client_id` error even though the Consumer Key is correct.

**Fix**: Navigate to **Setup > Connected Apps > Manage Connected Apps** and install the Connected App.

## JWT Bearer Flow Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `invalid_grant` on JWT token request | Certificate mismatch | Ensure the certificate uploaded to the Connected App matches the private key signing the JWT |
| `invalid_grant` with `user not found` | Wrong `sub` claim in JWT | Use the Salesforce username (not email) in the `sub` field |
| `invalid_grant` with `audience` error | Wrong `aud` claim | Use `https://login.salesforce.com` or `https://test.salesforce.com` (not instance URL) |
| `invalid_grant` after sandbox refresh | Sandbox URL changed | Update the `aud` claim to `https://test.salesforce.com` and verify the user exists in the sandbox |
| Token request times out | Network/firewall blocking | Ensure outbound HTTPS (port 443) to login.salesforce.com is allowed |
| `invalid_client_id` | App not pre-authorized for user | Pre-authorize the Connected App for the user's profile or permission set |

## Client Credentials Flow Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `invalid_grant` | No "Run As" user assigned | Assign a user in the Connected App's "Run As" field under Client Credentials |
| `invalid_grant` with `no valid scopes` | Missing scopes (Winter '26+) | Add `Api` or other required scopes to the Connected App |
| `unauthorized_client` | Client Credentials flow not enabled | Enable "Enable Client Credentials Flow" in the Connected App's OAuth settings |
| Insufficient permissions | Run As user lacks object access | Grant the Run As user the necessary Permission Sets and object permissions |

## Diagnostic Steps

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
