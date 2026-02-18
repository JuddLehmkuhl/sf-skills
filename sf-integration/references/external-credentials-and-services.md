# External Credentials & External Services

## External Credentials (API 61+)

### OAuth External Credential

**Use Case**: Modern OAuth 2.0 with per-user or named principal authentication

**Template**: `templates/external-credentials/oauth-external-credential.externalCredential-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExternalCredential xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>{{CredentialLabel}}</label>
    <authenticationProtocol>Oauth</authenticationProtocol>
    <externalCredentialParameters>
        <parameterName>clientId</parameterName>
        <parameterType>AuthProviderClientId</parameterType>
        <parameterValue>{{ClientId}}</parameterValue>
    </externalCredentialParameters>
    <externalCredentialParameters>
        <parameterName>clientSecret</parameterName>
        <parameterType>AuthProviderClientSecret</parameterType>
        <parameterValue>{{ClientSecret}}</parameterValue>
    </externalCredentialParameters>
    <principals>
        <principalName>{{PrincipalName}}</principalName>
        <principalType>NamedPrincipal</principalType>
        <sequenceNumber>1</sequenceNumber>
    </principals>
</ExternalCredential>
```

**Permission Set Assignment** (required for External Credentials):
```xml
<!-- In permissionset-meta.xml -->
<externalCredentialPrincipalAccesses>
    <enabled>true</enabled>
    <externalCredentialPrincipal>{{CredentialName}} - {{PrincipalName}}</externalCredentialPrincipal>
</externalCredentialPrincipalAccesses>
```

---

## External Services (OpenAPI/Swagger)

### Generating from OpenAPI Spec

**Process**:
1. Obtain OpenAPI 2.0 (Swagger) or 3.0 spec from external API
2. Create Named Credential for authentication
3. Register External Service in Salesforce
4. Salesforce auto-generates Apex classes

**Template**: `templates/external-services/openapi-registration.externalServiceRegistration-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ExternalServiceRegistration xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>{{ServiceLabel}}</label>
    <namedCredential>{{NamedCredentialName}}</namedCredential>
    <schema>{{OpenAPISchemaContent}}</schema>
    <schemaType>OpenApi3</schemaType>
    <serviceBinding>{{ServiceBindingName}}</serviceBinding>
    <status>Complete</status>
</ExternalServiceRegistration>
```

### Using Auto-Generated Apex

External Services generate Apex classes like:
- `ExternalService.{{ServiceName}}`
- `ExternalService.{{ServiceName}}_{{OperationName}}`

```apex
// Auto-generated class usage
ExternalService.Stripe stripe = new ExternalService.Stripe();
ExternalService.Stripe_createCustomer_Request req =
    new ExternalService.Stripe_createCustomer_Request();
req.email = 'customer@example.com';
ExternalService.Stripe_createCustomer_Response resp = stripe.createCustomer(req);
```
