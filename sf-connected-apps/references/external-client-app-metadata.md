# External Client App Metadata Structure

> Extracted from `sf-connected-apps/SKILL.md` for progressive disclosure.

## ExternalClientApplication (Header File)

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

## ExtlClntAppGlobalOauthSettings (Global OAuth)

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

## ExtlClntAppOauthSettings (Instance OAuth)

**File**: `[AppName].ecaOauth-meta.xml`

> **Note**: OAuth flows are configured via Admin UI or `ExtlClntAppConfigurablePolicies`.

## ExtlClntAppConfigurablePolicies (Admin Policies)

**File**: `[AppName].ecaPolicy-meta.xml` (auto-generated, admin-configurable)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExtlClntAppConfigurablePolicies xmlns="http://soap.sforce.com/2006/04/metadata">
    <ipRelaxation>ENFORCE</ipRelaxation>
    <refreshTokenPolicy>infinite</refreshTokenPolicy>
    <sessionTimeout>120</sessionTimeout>
</ExtlClntAppConfigurablePolicies>
```

## ECA Distribution States

| State | Description | Use Case |
|-------|-------------|----------|
| `Local` | Available only in creating org | Development, single-org integrations |
| `Packageable` | Can be included in 2GP packages | ISV apps, multi-org distribution |
