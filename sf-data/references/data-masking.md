# Data Masking & Anonymization (Sandbox Refreshes)

> Referenced from `SKILL.md` -- Data Masking section

---

When refreshing sandboxes from production, sensitive data must be masked or anonymized to comply with GDPR, CCPA, HIPAA, and FINRA regulations.

## Masking Strategy

| Data Category | Fields | Masking Technique | Example |
|--------------|--------|-------------------|---------|
| **Names** | FirstName, LastName | Pseudonymization | `User_00042`, `Contact_00042` |
| **Email** | Email, PersonEmail | Pattern replacement | `masked_00042@example.com` |
| **Phone** | Phone, MobilePhone | Format-preserving | `555-000-0042` |
| **SSN/Tax ID** | SSN__c, TaxId__c | Full deletion or hash | `XXX-XX-0042` |
| **Financial** | AnnualRevenue, CreditLimit__c | Range bucketing | Round to nearest $100K |
| **Address** | BillingStreet, MailingStreet | Generalization | `123 Test Street` |
| **Free text** | Description, Comments__c | Truncation/replacement | `[MASKED]` |

## Salesforce Data Mask (Native Tool)

Salesforce offers Data Mask as a managed package for automated post-refresh masking:

```
Setup -> Data Mask -> Configure Masking Rules
  - Object: Contact
  - Field: Email -> Pattern: masked_{SEQUENCE}@example.com
  - Field: Phone -> Random (format-preserving)
  - Field: SSN__c -> Delete
```

## Post-Refresh Apex Script (Alternative)

```apex
// Run via sf apex run --file mask-sandbox.apex --target-org sandbox
List<Contact> contacts = [SELECT Id, Email, Phone, FirstName, LastName FROM Contact LIMIT 10000];
for (Integer i = 0; i < contacts.size(); i++) {
    contacts[i].Email = 'masked_' + i + '@example.com';
    contacts[i].Phone = '555-000-' + String.valueOf(i).leftPad(4, '0');
    contacts[i].FirstName = 'User';
    contacts[i].LastName = 'Contact_' + i;
}
update contacts;
```

## Key Rules

- **Never skip masking** - Even "dev" sandboxes may be accessed by contractors
- **Mask before testing** - Run masking scripts immediately after sandbox refresh
- **Preserve referential integrity** - Mask values consistently across objects (e.g., same Contact ID -> same masked email everywhere)
- **Document your masking rules** - Store in Custom Metadata or a data dictionary
- **Test the masking** - Verify no real PII leaks through formula fields, reports, or related lists
