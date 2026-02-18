# Metadata API Advanced Patterns -- Deep Dive

> Extracted from `sf-metadata/SKILL.md`. Return to [SKILL.md](../SKILL.md) for the core workflow.

## Manifest Files (package.xml)

**Generate package.xml from source**:
```bash
sf project generate manifest --source-dir force-app --name package.xml --output-dir manifest
```

**Generate package.xml for specific metadata types**:
```bash
sf project generate manifest --metadata CustomObject:Invoice__c CustomField:Invoice__c.Amount__c --name package.xml
```

**Example package.xml**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>Invoice__c</members>
        <members>Payment__c</members>
        <name>CustomObject</name>
    </types>
    <types>
        <members>Invoice__c.Amount__c</members>
        <members>Invoice__c.Status__c</members>
        <name>CustomField</name>
    </types>
    <types>
        <members>Invoice_Access</members>
        <name>PermissionSet</name>
    </types>
    <types>
        <members>Invoice__c-Invoice Layout</members>
        <name>Layout</name>
    </types>
    <version>62.0</version>
</Package>
```

## Retrieve Patterns

**Retrieve with manifest**:
```bash
sf project retrieve start --manifest manifest/package.xml --target-org [alias]
```

**Retrieve specific metadata**:
```bash
sf project retrieve start --metadata CustomObject:Invoice__c --target-org [alias]
```

**Retrieve with source tracking** (scratch orgs and sandboxes with tracking enabled):
```bash
sf project retrieve start --target-org [alias]
# Retrieves only changed metadata since last retrieve/deploy
```

**Retrieve all metadata of a type**:
```bash
sf project retrieve start --metadata "CustomObject" --target-org [alias]
```

## Selective Retrieve for Large Orgs

```bash
# Retrieve only what's in your package.xml
sf project retrieve start --manifest manifest/package.xml --target-org [alias]

# Retrieve a single object and all its children (fields, VR, RT, layouts)
sf project retrieve start --metadata "CustomObject:Invoice__c" --target-org [alias]

# Retrieve only specific metadata types
sf project retrieve start --metadata "ApexClass" "ApexTrigger" "CustomObject" --target-org [alias]
```

## Deploy Patterns

**Deploy with source tracking**:
```bash
sf project deploy start --target-org [alias]
# Deploys only changed metadata since last deploy
```

**Deploy specific directory**:
```bash
sf project deploy start --source-dir force-app/main/default/objects/Invoice__c --target-org [alias]
```

**Deploy with manifest**:
```bash
sf project deploy start --manifest manifest/package.xml --target-org [alias]
```

**Validate only (dry run)**:
```bash
sf project deploy start --source-dir force-app --target-org [alias] --dry-run
```

**Deploy with test execution**:
```bash
sf project deploy start --source-dir force-app --target-org [alias] --test-level RunSpecifiedTests --tests InvoiceTest PaymentTest
```

## Metadata API Limits

| Limit | Value |
|-------|-------|
| Maximum components per deploy | 10,000 |
| Maximum deploy file size (zip) | 39 MB (400 MB unzipped) |
| Maximum retrieve file size | 39 MB (400 MB unzipped) |
| API calls per 24 hours | Org-dependent (varies by edition) |
| Concurrent Metadata API operations | 1 per org (queued if >1) |
| Deploy timeout | 10 minutes default, configurable up to 60 minutes |
| Source tracking history | Last 3 days of changes |
