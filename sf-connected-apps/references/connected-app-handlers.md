# Connected App Handler Classes (ConnectedAppPlugin)

> Extracted from `sf-connected-apps/SKILL.md` for progressive disclosure.

## Overview

The `Auth.ConnectedAppPlugin` Apex class allows you to customize Connected App behavior during OAuth flows. Use handler classes to inject custom claims into tokens, control authorization logic, or implement custom login experiences.

## When to Use

- Inject custom attributes (claims) into ID tokens or introspection responses
- Implement custom authorization logic beyond standard OAuth
- Customize token refresh behavior
- Add org-specific data to OAuth responses without follow-up API calls
- Build custom login flows for community/Experience Cloud users

## ConnectedAppPlugin Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `authorize` | `Auth.AuthProviderTokenResponse authorize(Id userId, Id connectedAppId, Boolean isAdminApproved, Auth.InvocationContext context)` | Called during the authorization phase. Override to implement custom authorization logic. |
| `customAttributes` | `Map<String, String> customAttributes(Id userId, Id connectedAppId, Map<String, String> formulaDefinedAttributes, Auth.InvocationContext context)` | Returns custom attributes to include in the OAuth response or ID token. |
| `refresh` | `Boolean refresh(Id userId, Id connectedAppId, Auth.InvocationContext context)` | Called when a token refresh is requested. Return `true` to allow the refresh, `false` to deny it. |

## Example: Custom Claims Plugin

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

## Configuring the Handler

1. Deploy the Apex class to the org
2. Navigate to **Setup > App Manager** > find the Connected App > **Manage**
3. Under **Custom Connected App Handler**:
   - **Apex Plugin Class**: Enter the class name (e.g., `CustomClaimsPlugin`)
   - **Run As**: Select the user context for the plugin execution
4. Save and test the OAuth flow

## Best Practices

- Always call `super` or return defaults for methods you do not customize
- Keep SOQL queries minimal (governor limits apply)
- Cache results when possible to avoid redundant queries on token refresh
- Test thoroughly: handler errors can block all OAuth flows for the Connected App
- Use Custom Metadata Types for configurable behavior instead of hardcoding

> **Note**: ConnectedAppPlugin handler classes are supported only on Connected Apps, not on External Client Apps (as of API 62.0).
