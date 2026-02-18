# JWT Bearer Flow Setup (Step-by-Step)

> Extracted from `sf-connected-apps/SKILL.md` for progressive disclosure.

## Prerequisites

- Admin access to create Connected Apps
- OpenSSL for certificate generation (or use Salesforce Certificate and Key Management)

## Step 1: Generate Certificate and Private Key

```bash
# Generate private key
openssl genrsa -out server.key 2048

# Generate certificate (self-signed, valid 1 year)
openssl req -new -x509 -key server.key -out server.crt -days 365 \
  -subj "/CN=MyIntegration/O=MyCompany/C=US"
```

## Step 2: Create Connected App

1. Setup > App Manager > New Connected App
2. Enable OAuth Settings
3. Callback URL: `https://login.salesforce.com/services/oauth2/callback` (or `https://oauthdebugger.com/debug` for testing)
4. Check "Use digital signatures" and upload `server.crt`
5. Select scopes: `Api`, `RefreshToken` (or `Full` if absolutely necessary)
6. Save

## Step 3: Pre-Authorize the User

1. Setup > App Manager > find the app > Manage
2. Under Profiles or Permission Sets, add the integration user's profile/perm set
3. Set IP Relaxation policy as needed

## Step 4: Request Access Token

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

## Step 5: Verify in sf CLI (for CI/CD)

```bash
# Authenticate sf CLI using JWT
sf org login jwt \
  --client-id YOUR_CONSUMER_KEY \
  --jwt-key-file server.key \
  --username user@example.com \
  --instance-url https://login.salesforce.com \
  --alias my-org
```
