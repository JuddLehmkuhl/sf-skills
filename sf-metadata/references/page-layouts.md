# Page Layout Best Practices -- Deep Dive

> Extracted from `sf-metadata/SKILL.md`. Return to [SKILL.md](../SKILL.md) for the core workflow.

## Page Layout vs Lightning Record Page

| Feature | Page Layout | Lightning Record Page |
|---------|------------|----------------------|
| **Field arrangement** | Sections with 1 or 2 columns | Dynamic Forms with conditional visibility |
| **Related lists** | Configured in layout | Can be placed anywhere on page |
| **Assignment** | Profile + Record Type | App, Record Type, Profile, or default |
| **Custom components** | No | Yes (LWC, Aura, standard components) |
| **Conditional visibility** | No | Yes (field values, device, permissions) |
| **Highlights Panel** | Configured via Compact Layout | Configured via Compact Layout |
| **Tabs** | Not available | Tabs component for organization |

## Compact Layouts

Compact Layouts control which fields appear in:
- Record highlights (top of Lightning record page)
- Lookup cards (hover over lookup fields)
- Mobile record view
- Kanban cards

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CompactLayout xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Enterprise_Compact</fullName>
    <fields>Name</fields>
    <fields>StageName</fields>
    <fields>Amount</fields>
    <fields>CloseDate</fields>
    <fields>Account.Name</fields>
    <label>Enterprise Compact Layout</label>
</CompactLayout>
```

**Rules**:
- Maximum 10 fields
- First field becomes the record title in highlights panel
- Assign to Record Type via `compactLayoutAssignment` in object metadata

## Related Lists Configuration

```xml
<relatedLists>
    <fields>FULL_NAME</fields>
    <fields>CONTACT.TITLE</fields>
    <fields>CONTACT.EMAIL</fields>
    <fields>CONTACT.PHONE1</fields>
    <relatedList>RelatedContactList</relatedList>
    <sortField>FULL_NAME</sortField>
    <sortOrder>Asc</sortOrder>
</relatedLists>
```

## Dynamic Forms (Lightning Record Pages)

Dynamic Forms allow individual fields and sections to be placed on Lightning Record Pages with visibility rules:

- **Enable**: Edit Lightning Record Page -> select field section -> "Upgrade to Dynamic Form"
- **Visibility Filters**: Show/hide fields based on:
  - Field values on the record
  - User permissions
  - Device type (desktop/mobile)
  - Record Type

**Best practice**: Migrate complex page layouts to Dynamic Forms for conditional field visibility instead of creating multiple page layouts per Record Type.

## Path Configuration

Path (Sales Path, Service Path) shows a visual progress bar for stage-based processes:

- Setup -> Path Settings -> Enable
- Create Path for each Record Type + picklist field combination
- Add key fields and guidance text per stage
- Optionally add celebration (confetti) on closed stages

**Path metadata path**: `force-app/main/default/pathAssistants/[PathName].pathAssistant-meta.xml`
