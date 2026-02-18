---
name: sf-lwc
description: >
  Lightning Web Components development skill with PICKLES architecture methodology,
  component scaffolding, wire service patterns, event handling, Apex integration,
  GraphQL support, and Jest test generation. Build modern Salesforce UIs with
  proper reactivity, accessibility, dark mode compatibility, and performance patterns.
license: MIT
metadata:
  version: "3.0.0"
  author: "Judd Lehmkuhl"
  scoring: "165 points across 8 categories (SLDS 2 + Dark Mode compliant)"
---

# sf-lwc: Lightning Web Components Development

## Core Responsibilities

1. **Component Scaffolding**: Generate complete LWC bundles (JS, HTML, CSS, meta.xml)
2. **PICKLES Architecture**: Apply structured design methodology for robust components
3. **Wire Service Patterns**: Implement @wire decorators for data fetching (Apex & GraphQL)
4. **Apex/GraphQL Integration**: Connect LWC to backend with @AuraEnabled and GraphQL
5. **Event Handling**: Component communication (CustomEvent, LMS, pubsub)
6. **Error Handling**: Centralized error patterns with toast notifications
7. **Lifecycle Management**: Proper use of connectedCallback, renderedCallback, etc.
8. **Jest Testing**: Generate comprehensive unit tests with advanced patterns
9. **Accessibility**: WCAG compliance with ARIA attributes, focus management
10. **Dark Mode**: SLDS 2 compliant styling with global styling hooks
11. **Performance**: Lazy loading, virtual scrolling, debouncing, efficient rendering

---

## PICKLES Framework

```
P -> Prototype    | Validate ideas with wireframes & mock data
I -> Integrate    | Choose data source (LDS, Apex, GraphQL, API)
C -> Composition  | Structure component hierarchy & communication
K -> Kinetics     | Handle user interactions & event flow
L -> Libraries    | Leverage platform APIs & base components
E -> Execution    | Optimize performance & lifecycle hooks
S -> Security     | Enforce permissions, FLS, and data protection
```

### P - Prototype

| Action | Description |
|--------|-------------|
| Wireframe | Create high-level component sketches |
| Mock Data | Use sample data to test functionality |
| Stakeholder Review | Gather feedback before development |
| Separation of Concerns | Break into smaller functional pieces |

```javascript
// Mock data pattern for prototyping
const MOCK_ACCOUNTS = [
    { Id: '001MOCK001', Name: 'Acme Corp', Industry: 'Technology' },
    { Id: '001MOCK002', Name: 'Global Inc', Industry: 'Finance' }
];

export default class AccountPrototype extends LightningElement {
    accounts = MOCK_ACCOUNTS; // Replace with wire/Apex later
}
```

### I - Integrate

**Data Source Decision Tree**:

| Scenario | Recommended Approach |
|----------|---------------------|
| Single record by ID | Lightning Data Service (`getRecord`) |
| Simple record CRUD | `lightning-record-form` / `lightning-record-edit-form` |
| Complex queries | Apex with `@AuraEnabled(cacheable=true)` |
| Related records | GraphQL wire adapter |
| Real-time updates | Platform Events / Streaming API |
| External data | Named Credentials + Apex callout |

**Integration Checklist**:
- [ ] Implement error handling with clear user notifications
- [ ] Add loading spinners to prevent duplicate requests
- [ ] Use LDS for single-object operations (minimizes DML)
- [ ] Respect FLS and CRUD in Apex implementations
- [ ] Store `wiredResult` for `refreshApex()` support

### C - Composition

| Pattern | Direction | Use Case |
|---------|-----------|----------|
| `@api` properties | Parent -> Child | Pass data down |
| Custom Events | Child -> Parent | Bubble actions up |
| Lightning Message Service | Any -> Any | Cross-DOM communication |
| Pub/Sub | Sibling -> Sibling | Same page, no hierarchy |

**Best Practices**: Shallow hierarchies (max 3-4 levels), single responsibility per component, clean up subscriptions in `disconnectedCallback()`.

### K - Kinetics

| Pattern | Implementation |
|---------|----------------|
| Debounce | 300ms delay for search inputs |
| Disable during submit | Prevent duplicate clicks |
| Keyboard navigation | Enter/Space triggers actions |
| Event bubbling | Control with `bubbles` and `composed` |

```javascript
// Debounce pattern for search
delayTimeout;
handleSearchChange(event) {
    const searchTerm = event.target.value;
    clearTimeout(this.delayTimeout);
    this.delayTimeout = setTimeout(() => {
        this.dispatchEvent(new CustomEvent('search', { detail: { searchTerm } }));
    }, 300);
}
```

### L - Libraries

| API/Module | Use Case |
|------------|----------|
| `lightning/navigation` | Page/record navigation |
| `lightning/uiRecordApi` | LDS operations (getRecord, updateRecord) |
| `lightning/toast` | User notifications (preferred) |
| `lightning/modal` | Native modal dialogs |
| `lightning/refresh` | Dispatch refresh events |
| `@salesforce/client/formFactor` | Device-responsive rendering |
| Base Components | Pre-built UI (button, input, datatable) |

### E - Execution

| Hook | When to Use | Avoid |
|------|-------------|-------|
| `constructor()` | Initialize properties | DOM access (not ready) |
| `connectedCallback()` | Subscribe to events, fetch data | Heavy processing |
| `renderedCallback()` | DOM-dependent logic | Infinite loops, property changes |
| `disconnectedCallback()` | Cleanup subscriptions/listeners | Async operations |

**Performance Checklist**:
- [ ] Use `lwc:if` / `lwc:elseif` / `lwc:else` (not deprecated `if:true`)
- [ ] Use `key` directive in iterations
- [ ] Cache computed values in getters
- [ ] Avoid property updates that trigger re-renders

### S - Security

| Requirement | Implementation |
|-------------|----------------|
| Field-Level Security | Use `WITH SECURITY_ENFORCED` in SOQL |
| CRUD Permissions | Check before DML operations |
| Custom Permissions | Conditionally render features |
| Input Validation | Sanitize before processing |
| Sensitive Data | Never expose in client-side code |

---

## Component Patterns

See `references/component-patterns.md` for complete code examples: wire service, GraphQL, composable modal, parent-child, LMS pub/sub, and navigation patterns.

---

## Error Handling & Toast Notifications

| Error Source | Structure | Common Cause |
|-------------|-----------|--------------|
| JavaScript | Standard `Error` object | Null references, bad bindings |
| Lightning Data Service | `{ body: { message, output } }` | FLS violations, invalid record |
| Apex `@AuraEnabled` | `{ body: { message } }` | `AuraHandledException`, DML errors |
| Wire adapter | `{ body: { message } }` or array | Query errors, permissions |

| Toast Variant | Use Case | Auto-dismiss |
|---------|----------|-------------|
| `success` | Record saved, action completed | 4.8s |
| `error` | Save failed, validation error | Sticky |
| `warning` | Partial success, approaching limits | 4.8s |
| `info` | Informational messages | 4.8s |

See `references/error-handling-patterns.md` for `reduceErrors` utility, centralized error handler mixin, and wire vs imperative error handling examples.

---

## Lightning Datatable

| Guideline | Recommendation |
|-----------|----------------|
| Max rows loaded at once | 50 (use infinite scrolling) |
| Optimal column count | Up to 5 for best performance |
| Hard limit tested | 1,000 rows x 5 columns |
| Inline editing | Enable only on columns that need it |
| Large datasets (250+ rows) | Keep columns under 20 |

See `references/datatable-patterns.md` for basic datatable, inline editing, and infinite scrolling examples.

---

## Dynamic Components (lwc:component)

| Use Case | Recommended |
|----------|-------------|
| Plugin / extension architecture | Yes |
| Configurable dashboard tiles | Yes |
| A/B testing different UIs | Yes |
| Static known components | No (use direct references) |
| Performance-critical paths | No (adds async overhead) |

**Requirements**: API 55.0+, LWS enabled, `<capability>lightning__dynamicComponent</capability>` in meta.xml.

See `references/dynamic-components.md` for basic and props-based dynamic component examples.

---

## Light DOM vs Shadow DOM

| Factor | Shadow DOM (Default) | Light DOM |
|--------|---------------------|-----------|
| Style encapsulation | Full isolation | Styles cascade in/out |
| Security | Protected by LWS | Must nest inside shadow DOM parent |
| Third-party CSS libs | Blocked by shadow boundary | Full access |
| DOM querying | `this.template.querySelector()` | `this.querySelector()` |
| Packageable | Yes | No |
| Event retargeting | Events retargeted to host | Events not retargeted |

**Default**: Shadow DOM. Only use Light DOM when you need global CSS or third-party libraries.

See `references/light-dom-patterns.md` for implementation, scoped styles, restrictions, and architecture patterns.

---

## Responsive Design

| Form Factor Value | Device |
|-------|--------|
| `Large` | Desktop browser |
| `Medium` | Tablet |
| `Small` | Phone |

Import: `import FORM_FACTOR from '@salesforce/client/formFactor';`

See `references/responsive-design.md` for form factor detection, adaptive layout, and meta.xml configuration examples.

---

## SLDS 2 Validation (165-Point Scoring)

| Category | Points | Key Checks |
|----------|--------|------------|
| **SLDS Class Usage** | 25 | Valid class names, proper `slds-*` utilities |
| **Accessibility** | 25 | ARIA labels, roles, alt-text, keyboard navigation |
| **Dark Mode Readiness** | 25 | No hardcoded colors, CSS variables only |
| **SLDS Migration** | 20 | No deprecated SLDS 1 patterns/tokens |
| **Styling Hooks** | 20 | Proper `--slds-g-*` variable usage |
| **Component Structure** | 15 | Uses `lightning-*` base components |
| **Performance** | 10 | Efficient selectors, no `!important` |
| **PICKLES Compliance** | 25 | Architecture methodology adherence (optional) |

```
150-165 pts -> Production-ready, full SLDS 2 + Dark Mode
125-149 pts -> Good component, minor styling issues
100-124 pts -> Functional, needs SLDS cleanup
 75-99 pts  -> Basic functionality, SLDS issues
   <75 pts  -> Needs significant work
```

See `references/slds2-dark-mode.md` for dark mode checklist, SLDS 1-to-2 migration patterns, global styling hooks reference, and linter commands.

---

## Jest Testing

See `references/jest-testing-patterns.md` for render cycle helper, proxy unboxing, DOM cleanup, ResizeObserver polyfill, and complete test template.

---

## Apex Controller Integration

**Rule**: Always throw `AuraHandledException` -- other exceptions expose stack traces to the client.

See `references/apex-controller-patterns.md` for cacheable/non-cacheable method patterns and error handling examples.

---

## Metadata Configuration (meta.xml)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>62.0</apiVersion>
    <isExposed>true</isExposed>
    <masterLabel>Account Dashboard</masterLabel>
    <description>SLDS 2 compliant account dashboard with dark mode support</description>
    <targets>
        <target>lightning__RecordPage</target>
        <target>lightning__AppPage</target>
        <target>lightning__HomePage</target>
        <target>lightning__FlowScreen</target>
        <target>lightningCommunity__Page</target>
    </targets>
    <targetConfigs>
        <targetConfig targets="lightning__RecordPage">
            <objects>
                <object>Account</object>
            </objects>
            <property name="title" type="String" default="Dashboard"/>
            <property name="maxRecords" type="Integer" default="10"/>
            <supportedFormFactors>
                <supportedFormFactor type="Large" />
                <supportedFormFactor type="Small" />
            </supportedFormFactors>
        </targetConfig>
    </targetConfigs>
</LightningComponentBundle>
```

---

## CLI Commands

| Command | Purpose |
|---------|---------|
| `sf lightning generate component --type lwc --name myComp --output-dir force-app/main/default/lwc` | Create new LWC |
| `sf lightning lwc test run` | Run all Jest tests |
| `sf lightning lwc test run --watch` | Watch mode |
| `sf lightning lwc test run --spec force-app/.../lwc/myComp/__tests__` | Specific component |
| `sf lightning lwc test run -- --coverage` | With coverage |
| `sf project deploy start -m LightningComponentBundle` | Deploy all LWC |

---

## Accessibility Checklist

| Requirement | Implementation |
|-------------|----------------|
| **Labels** | `label` on inputs, `aria-label` on icons |
| **Keyboard** | Enter/Space triggers, Tab navigation |
| **Focus** | Visible indicator, logical order |
| **Live Regions** | `aria-live="polite"` for dynamic content |
| **Contrast** | 4.5:1 minimum for text |
| **Error Announcement** | `role="alert"` on error messages |

```html
<!-- Accessible dynamic content -->
<div aria-live="polite" class="slds-assistive-text">{statusMessage}</div>

<!-- Accessible error display -->
<template lwc:if={errorMessage}>
    <div role="alert" class="slds-text-color_error slds-p-around_small">{errorMessage}</div>
</template>
```

---

## Flow Screen Integration

See `references/flow-screen-integration.md` for FlowAttributeChangeEvent, FlowNavigationFinishEvent, and availableActions patterns.

---

## Workspace API (Console Apps)

```javascript
import { IsConsoleNavigation, getFocusedTabInfo, openTab,
         setTabLabel, setTabIcon } from 'lightning/platformWorkspaceApi';

@wire(IsConsoleNavigation) isConsole;

async openRecordTab(recordId) {
    if (!this.isConsole) return;
    await openTab({ recordId, focus: true });
}
```

> Full Workspace API patterns: [Salesforce Workspace API Reference](https://developer.salesforce.com/docs/platform/lwc/guide/use-workspace-api.html)

---

## Cross-Skill Integration

| Skill | Use Case |
|-------|----------|
| **sf-apex** | Generate Apex controllers, services, test classes |
| **sf-flow** | Embed components in Flow Screens, pass data to/from Flow |
| **sf-testing** | Run Jest tests, coverage analysis |
| **sf-deploy** | Deploy components to target org |
| **sf-metadata** | Create message channels, custom objects/fields |

---

## Dependencies

**Required**: Target org with LWC support (API 45.0+), `sf` CLI authenticated.
**For Testing**: Node.js 18+, Jest (`@salesforce/sfdx-lwc-jest`).
**For SLDS Validation**: `@salesforce-ux/slds-linter` (optional).

---

## References

- [PICKLES Framework (Salesforce Ben)](https://www.salesforceben.com/the-ideal-framework-for-architecting-salesforce-lightning-web-components/)
- [LWC Recipes (GitHub)](https://github.com/trailheadapps/lwc-recipes)
- [SLDS 2 Transition Guide](https://www.lightningdesignsystem.com/2e1ef8501/p/8184ad-transition-to-slds-2)
- [SLDS 2 for Developers (Trailhead)](https://trailhead.salesforce.com/content/learn/modules/salesforce-lightning-design-system-2-for-developers/transition-your-org-from-slds-1-to-slds-2)
- [SLDS Styling Hooks](https://developer.salesforce.com/docs/platform/lwc/guide/create-components-css-custom-properties.html)
- [James Simone - Composable Modal](https://www.jamessimone.net/blog/joys-of-apex/lwc-composable-modal/)
- [James Simone - Advanced Jest Testing](https://www.jamessimone.net/blog/joys-of-apex/advanced-lwc-jest-testing/)
- [Toast Notifications (LWC Dev Guide)](https://developer.salesforce.com/docs/platform/lwc/guide/use-toast.html)
- [Error Handling Best Practices](https://developer.salesforce.com/blogs/2020/08/error-handling-best-practices-for-lightning-web-components)
- [Lightning Datatable](https://developer.salesforce.com/docs/component-library/bundle/lightning-datatable)
- [Dynamic Components](https://developer.salesforce.com/docs/platform/lwc/guide/js-dynamic-components.html)
- [Light DOM](https://developer.salesforce.com/docs/platform/lwc/guide/create-light-dom.html)
- [Client Form Factor](https://developer.salesforce.com/docs/platform/lwc/guide/create-client-form-factor.html)
- [Compare SLDS Versions](https://developer.salesforce.com/docs/platform/lwc/guide/create-components-css-slds1-slds2.html)
- [LWC Error Types](https://developer.salesforce.com/docs/platform/lwc/guide/data-error-types.html)

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2026 Jag Valaiyapathy
