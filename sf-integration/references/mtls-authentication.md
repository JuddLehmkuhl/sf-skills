# Mutual TLS (mTLS) Authentication

## When to Use mTLS

- High-security integrations (financial, healthcare, government)
- Regulatory compliance requirements (PCI-DSS, HIPAA)
- Zero-trust network architectures
- When the external system requires client certificate authentication

## Setup Steps

**Step 1: Obtain or generate certificates**
- Obtain a client certificate signed by a Certificate Authority (CA) trusted by the external system
- You need: private key + certificate chain in JKS (Java KeyStore) format

**Step 2: Import certificate into Salesforce**
- Setup -> Certificate and Key Management -> Import from Keystore
- Upload the JKS file containing private key and certificate chain
- Note the certificate label for use in Named Credentials

**Step 3: Configure Named Credential with client certificate**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<NamedCredential xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>{{ServiceName}} mTLS</label>
    <endpoint>https://{{ExternalHost}}/api</endpoint>
    <principalType>NamedUser</principalType>
    <protocol>Ssl</protocol>
    <certificate>{{CertificateLabel}}</certificate>
</NamedCredential>
```

**Step 4: Use in Apex callout**
```apex
HttpRequest req = new HttpRequest();
req.setEndpoint('callout:{{ServiceName}}_mTLS/resource');
req.setMethod('GET');
// The certificate is automatically sent during TLS handshake
// No additional code needed - Named Credential handles it
```

**Step 5 (Inbound mTLS)**: For external systems calling INTO Salesforce:
- Setup -> Certificate and Key Management -> Mutual Authentication Certificates
- Upload the external system's CA certificate
- Create an API-only integration user with "Enforce SSL/TLS Mutual Authentication" permission

## mTLS Checklist

| Step | Action | Verified |
|------|--------|----------|
| 1 | Client certificate obtained from trusted CA | |
| 2 | JKS keystore created with private key + chain | |
| 3 | Certificate imported in Salesforce Certificate Management | |
| 4 | Named Credential configured with `protocol=Ssl` and certificate | |
| 5 | Remote Site Setting or CSP Trusted Site allows endpoint | |
| 6 | Test connection succeeds from Salesforce | |
| 7 | Certificate expiry monitoring configured | |
