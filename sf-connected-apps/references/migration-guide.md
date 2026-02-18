# Migration: Connected App to External Client App

> Extracted from `sf-connected-apps/SKILL.md` for progressive disclosure.

## Step 1: Assess Current State

```
Glob: **/*.connectedApp-meta.xml
```
Review existing Connected Apps and their configurations.

## Step 2: Create ECA Equivalent

- Map OAuth settings to ECA structure
- Create all required ECA metadata files (`.eca`, `.ecaGlblOauth`, `.ecaOauth`, `.ecaPolicy`)
- Set `distributionState` based on needs
- Note: ConnectedAppPlugin handler classes cannot be migrated to ECAs

## Step 3: Update Integrations

- Generate new Consumer Key/Secret
- Update Named Credentials to reference the new ECA
- Update external systems with new credentials
- Test OAuth flows in sandbox before production

## Step 4: Parallel Run

- Keep both Connected App and ECA active during transition
- Monitor both apps' login history for any issues
- Gradually migrate external systems to the ECA

## Step 5: Deprecate Old App

- Remove from Connected App policies
- Revoke all active tokens for the old Connected App
- Archive or delete Connected App metadata
