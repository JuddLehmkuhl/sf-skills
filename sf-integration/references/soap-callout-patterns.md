# SOAP Callout Patterns

## WSDL2Apex Process

**Step 1**: Generate Apex from WSDL
1. Setup -> Apex Classes -> Generate from WSDL
2. Upload WSDL file
3. Salesforce generates Apex classes

**Step 2**: Configure Remote Site Setting or Named Credential

**Step 3**: Use generated classes in Apex

**Template**: `templates/soap/soap-callout-service.cls` (full implementation with async Queueable wrapper)

```apex
public with sharing class {{ServiceName}}SoapService {

    public static {{ResponseType}} callService({{RequestType}} request) {
        try {
            {{WsdlGeneratedClass}}.{{PortType}} stub =
                new {{WsdlGeneratedClass}}.{{PortType}}();
            stub.endpoint_x = 'callout:{{NamedCredentialName}}';
            stub.timeout_x = 120000;

            return stub.{{OperationName}}(request);
        } catch (Exception e) {
            throw new CalloutException('SOAP service error: ' + e.getMessage());
        }
    }
}
```

## Testing SOAP Callouts

See [callout-testing-patterns.md](callout-testing-patterns.md) for `WebServiceMock` implementation.
