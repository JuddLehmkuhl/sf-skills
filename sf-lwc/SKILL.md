---
name: sf-lwc
description: >
  Lightning Web Components development skill with component scaffolding, wire service
  patterns, event handling, Apex integration, and Jest test generation. Build modern
  Salesforce UIs with proper reactivity, accessibility, and performance patterns.
license: MIT
metadata:
  version: "1.1.0"
  author: "Jag Valaiyapathy"
  scoring: "140 points across 7 categories (SLDS 2 compliant)"
---

# sf-lwc: Lightning Web Components Development

Expert frontend engineer specializing in Lightning Web Components for Salesforce. Generate production-ready LWC components with proper data binding, Apex integration, event handling, and comprehensive Jest tests.

## Core Responsibilities

1. **Component Scaffolding**: Generate complete LWC bundles (JS, HTML, CSS, meta.xml)
2. **Wire Service Patterns**: Implement @wire decorators for data fetching
3. **Apex Integration**: Connect LWC to Apex controllers with @AuraEnabled methods
4. **Event Handling**: Implement component communication (CustomEvent, LMS, pubsub)
5. **Lifecycle Management**: Proper use of connectedCallback, renderedCallback, etc.
6. **Jest Testing**: Generate comprehensive unit tests for components
7. **Accessibility**: Ensure WCAG compliance with proper ARIA attributes
8. **Performance**: Implement lazy loading, virtual scrolling, efficient rendering

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- Component purpose (data display, form, navigation, etc.)
- Data source (Apex, wire adapters, static, external)
- Parent/child relationships
- Event communication needs
- Accessibility requirements

**Then**:
1. Analyze existing components in the project
2. Identify reusable patterns
3. Create TodoWrite tasks

### Phase 2: Component Design

**Component Structure Decision Tree**:

| Requirement | Component Type | Pattern |
|-------------|----------------|---------|
| Display record data | Data component | @wire with getRecord |
| Edit record | Form component | lightning-record-edit-form |
| Custom UI | Custom component | @wire with Apex |
| List with actions | Datatable | lightning-datatable |
| Navigation | Navigation component | NavigationMixin |
| Modal/Overlay | Modal component | lightning-modal |

**File Structure**:
```
myComponent/
├── myComponent.js           // Component logic
├── myComponent.html         // Template
├── myComponent.css          // Styles (optional)
├── myComponent.js-meta.xml  // Metadata configuration
└── __tests__/
    └── myComponent.test.js  // Jest tests
```

### Phase 3: Implementation

**Core LWC Patterns**:

```javascript
// Basic component with reactive properties
import { LightningElement, api, wire, track } from 'lwc';
import getAccounts from '@salesforce/apex/AccountController.getAccounts';

export default class AccountList extends LightningElement {
    @api recordId;           // Public property from parent
    @track accounts = [];    // Reactive array (track optional in newer versions)
    error;
    isLoading = true;

    // Wire service for data fetching
    @wire(getAccounts, { accountId: '$recordId' })
    wiredAccounts({ error, data }) {
        this.isLoading = false;
        if (data) {
            this.accounts = data;
            this.error = undefined;
        } else if (error) {
            this.error = error;
            this.accounts = [];
        }
    }

    // Lifecycle hooks
    connectedCallback() {
        // Component inserted into DOM
    }

    renderedCallback() {
        // DOM rendered (careful with infinite loops)
    }

    disconnectedCallback() {
        // Component removed from DOM - cleanup here
    }

    // Event handler
    handleClick(event) {
        const accountId = event.target.dataset.id;
        this.dispatchEvent(new CustomEvent('accountselected', {
            detail: { accountId },
            bubbles: true,
            composed: true
        }));
    }
}
```

### Phase 4: Testing

**Jest Test Pattern**:

```javascript
import { createElement } from 'lwc';
import AccountList from 'c/accountList';
import getAccounts from '@salesforce/apex/AccountController.getAccounts';

// Mock Apex method
jest.mock('@salesforce/apex/AccountController.getAccounts', () => ({
    default: jest.fn()
}), { virtual: true });

const MOCK_ACCOUNTS = [
    { Id: '001xx000003DGFAAA4', Name: 'Test Account 1' },
    { Id: '001xx000003DGFBBB4', Name: 'Test Account 2' }
];

describe('c-account-list', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('displays accounts when data is returned', async () => {
        getAccounts.mockResolvedValue(MOCK_ACCOUNTS);

        const element = createElement('c-account-list', { is: AccountList });
        document.body.appendChild(element);

        // Wait for async operations
        await Promise.resolve();

        const items = element.shadowRoot.querySelectorAll('lightning-card');
        expect(items.length).toBe(2);
    });

    it('displays error when fetch fails', async () => {
        getAccounts.mockRejectedValue(new Error('Failed'));

        const element = createElement('c-account-list', { is: AccountList });
        document.body.appendChild(element);

        await Promise.resolve();

        const error = element.shadowRoot.querySelector('.error');
        expect(error).not.toBeNull();
    });
});
```

### Phase 5: Validation & Deployment

1. **Run Jest tests**: `sf lightning lwc test run`
2. **Lint check**: `sf lightning lint`
3. **Deploy**: Use sf-deploy skill
4. **Verify in org**: Test in browser

---

## SLDS 2 Validation (140-Point Scoring)

The sf-lwc skill includes automated SLDS 2 (Salesforce Lightning Design System 2) validation that runs on every Write/Edit operation. This ensures your components are dark mode compatible, accessible, and use modern styling hooks.

| Category | Points | Key Checks |
|----------|--------|------------|
| **SLDS Class Usage** | 25 | Valid class names, proper `slds-*` utilities |
| **Accessibility** | 25 | ARIA labels, roles, alt-text, keyboard navigation |
| **Dark Mode** | 25 | No hardcoded colors, CSS variables only |
| **SLDS Migration** | 20 | No deprecated SLDS 1 patterns/tokens |
| **Styling Hooks** | 20 | Proper `--slds-g-*` variable usage |
| **Component Structure** | 15 | Uses `lightning-*` base components |
| **Performance** | 10 | Efficient selectors, no `!important` |

**Scoring Thresholds**:
```
⭐⭐⭐⭐⭐ 125-140 pts → Production-ready, SLDS 2 compliant
⭐⭐⭐⭐   110-124 pts → Good component, minor SLDS issues
⭐⭐⭐     90-109 pts → Functional, needs SLDS cleanup
⭐⭐       70-89 pts  → Basic functionality, SLDS issues
⭐         <70 pts   → Needs significant SLDS work
```

### Sample Validation Output

```
🎨 SLDS 2 Validation: myComponent.html
════════════════════════════════════════════════════════════════
📊 Score: 125/140 ⭐⭐⭐⭐ Good

📋 Category Breakdown:
   ✅ SLDS Class Usage: 25/25
   ✅ Accessibility: 25/25
   ⚠️ Dark Mode: 20/25 (-5)
   ✅ SLDS Migration: 20/20
   ⚠️ Styling Hooks: 15/20 (-5)
   ✅ Component Structure: 15/15
   ✅ Performance: 10/10

⚠️ Issues Found (2):
   🟠 L45 Hardcoded color #333333 - use --slds-g-color-on-surface
   🟡 L78 Deprecated --lwc-colorBackground - use --slds-g-color-surface-1
════════════════════════════════════════════════════════════════
```

### SLDS 2 Key Concepts

**Dark Mode Compatibility (Critical)**:
- Never use hardcoded hex colors (`#FFFFFF`, `#333333`)
- Never use hardcoded RGB/RGBA values
- Always use CSS variables: `var(--slds-g-color-surface-1)`

**SLDS 1 → SLDS 2 Migration**:
| SLDS 1 (Deprecated) | SLDS 2 (Use Instead) |
|---------------------|----------------------|
| `$color-background` | `--slds-g-color-surface-1` |
| `--lwc-colorBackground` | `--slds-g-color-surface-1` |
| `$spacing-medium` | `--slds-g-spacing-5` |
| `--lwc-spacingMedium` | `--slds-g-spacing-5` |

**Global Styling Hooks** (`--slds-g-*`):
- **Surface colors**: `--slds-g-color-surface-1` to `-4`, `-container-1` to `-3`
- **Text colors**: `--slds-g-color-on-surface`, `-on-surface-1`, `-on-surface-2`
- **Border colors**: `--slds-g-color-border-1`, `-border-2`, `-border-brand-1`
- **Spacing**: `--slds-g-spacing-0` to `--slds-g-spacing-12`
- **Font sizes**: `--slds-g-font-size-1` to `--slds-g-font-size-10`
- **Border radius**: `--slds-g-radius-border-1` to `-4`, `-circle`

### Optional: SLDS Linter Integration

For additional validation, install the official Salesforce SLDS Linter:

```bash
npm install -g @salesforce-ux/slds-linter
```

When installed, the validator will automatically use it for enhanced HTML template and CSS styling hooks validation. The custom Python validators still run regardless, providing comprehensive coverage.

---

## Best Practices (Component Quality)

Beyond SLDS validation, ensure your components follow these patterns:

| Category | Key Rules |
|----------|-----------|
| **Component Structure** | Proper file organization, naming conventions |
| **Data Handling** | Correct wire usage, error handling, loading states |
| **Event Architecture** | Proper event bubbling, composed flags |
| **Accessibility** | ARIA labels, keyboard navigation, screen reader |
| **Performance** | Lazy loading, efficient rendering, no memory leaks |
| **Test Coverage** | Jest tests for all scenarios |

---

## Component Patterns

### 1. Basic Data Display Component

```javascript
// accountCard.js
import { LightningElement, api } from 'lwc';

export default class AccountCard extends LightningElement {
    @api account;

    get formattedRevenue() {
        return this.account?.AnnualRevenue
            ? new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
              }).format(this.account.AnnualRevenue)
            : 'N/A';
    }
}
```

```html
<!-- accountCard.html -->
<template>
    <lightning-card title={account.Name} icon-name="standard:account">
        <div class="slds-p-horizontal_small">
            <p><strong>Industry:</strong> {account.Industry}</p>
            <p><strong>Revenue:</strong> {formattedRevenue}</p>
        </div>
        <div slot="footer">
            <lightning-button
                label="View Details"
                onclick={handleViewDetails}
                data-id={account.Id}>
            </lightning-button>
        </div>
    </lightning-card>
</template>
```

### 2. Wire Service with Apex

```javascript
// contactList.js
import { LightningElement, api, wire } from 'lwc';
import getContacts from '@salesforce/apex/ContactController.getContacts';
import { refreshApex } from '@salesforce/apex';

export default class ContactList extends LightningElement {
    @api recordId;
    contacts;
    error;
    wiredContactsResult;

    @wire(getContacts, { accountId: '$recordId' })
    wiredContacts(result) {
        this.wiredContactsResult = result;
        const { error, data } = result;
        if (data) {
            this.contacts = data;
            this.error = undefined;
        } else if (error) {
            this.error = error;
            this.contacts = undefined;
        }
    }

    async handleRefresh() {
        await refreshApex(this.wiredContactsResult);
    }
}
```

### 3. Imperative Apex Call

```javascript
// orderCreator.js
import { LightningElement, api } from 'lwc';
import createOrder from '@salesforce/apex/OrderController.createOrder';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

export default class OrderCreator extends LightningElement {
    @api accountId;
    isLoading = false;

    async handleCreateOrder() {
        this.isLoading = true;
        try {
            const result = await createOrder({
                accountId: this.accountId,
                items: this.selectedItems
            });

            this.dispatchEvent(new ShowToastEvent({
                title: 'Success',
                message: `Order ${result.OrderNumber} created`,
                variant: 'success'
            }));

            this.dispatchEvent(new CustomEvent('ordercreated', {
                detail: { orderId: result.Id }
            }));
        } catch (error) {
            this.dispatchEvent(new ShowToastEvent({
                title: 'Error',
                message: error.body?.message || 'Unknown error',
                variant: 'error'
            }));
        } finally {
            this.isLoading = false;
        }
    }
}
```

### 4. Parent-Child Communication

```javascript
// parent.js
import { LightningElement } from 'lwc';

export default class Parent extends LightningElement {
    selectedAccountId;

    handleAccountSelected(event) {
        this.selectedAccountId = event.detail.accountId;
    }
}
```

```html
<!-- parent.html -->
<template>
    <c-account-list onaccountselected={handleAccountSelected}></c-account-list>
    <template if:true={selectedAccountId}>
        <c-account-detail account-id={selectedAccountId}></c-account-detail>
    </template>
</template>
```

### 5. Lightning Message Service (Cross-DOM)

```javascript
// publisher.js
import { LightningElement, wire } from 'lwc';
import { publish, MessageContext } from 'lightning/messageService';
import ACCOUNT_SELECTED_CHANNEL from '@salesforce/messageChannel/AccountSelected__c';

export default class Publisher extends LightningElement {
    @wire(MessageContext)
    messageContext;

    handleSelect(event) {
        const payload = { accountId: event.target.dataset.id };
        publish(this.messageContext, ACCOUNT_SELECTED_CHANNEL, payload);
    }
}
```

```javascript
// subscriber.js
import { LightningElement, wire } from 'lwc';
import { subscribe, unsubscribe, MessageContext } from 'lightning/messageService';
import ACCOUNT_SELECTED_CHANNEL from '@salesforce/messageChannel/AccountSelected__c';

export default class Subscriber extends LightningElement {
    subscription = null;
    accountId;

    @wire(MessageContext)
    messageContext;

    connectedCallback() {
        this.subscribeToMessageChannel();
    }

    disconnectedCallback() {
        this.unsubscribeToMessageChannel();
    }

    subscribeToMessageChannel() {
        if (!this.subscription) {
            this.subscription = subscribe(
                this.messageContext,
                ACCOUNT_SELECTED_CHANNEL,
                (message) => this.handleMessage(message)
            );
        }
    }

    unsubscribeToMessageChannel() {
        unsubscribe(this.subscription);
        this.subscription = null;
    }

    handleMessage(message) {
        this.accountId = message.accountId;
    }
}
```

### 6. Navigation

```javascript
// navigator.js
import { LightningElement } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';

export default class Navigator extends NavigationMixin(LightningElement) {

    navigateToRecord(recordId) {
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: {
                recordId: recordId,
                objectApiName: 'Account',
                actionName: 'view'
            }
        });
    }

    navigateToList() {
        this[NavigationMixin.Navigate]({
            type: 'standard__objectPage',
            attributes: {
                objectApiName: 'Account',
                actionName: 'list'
            },
            state: {
                filterName: 'Recent'
            }
        });
    }

    navigateToCustomTab() {
        this[NavigationMixin.Navigate]({
            type: 'standard__navItemPage',
            attributes: {
                apiName: 'CustomTab'
            }
        });
    }
}
```

---

## Apex Controller Patterns

### Basic @AuraEnabled Controller

```apex
public with sharing class AccountController {

    @AuraEnabled(cacheable=true)
    public static List<Account> getAccounts(String searchTerm) {
        String searchKey = '%' + String.escapeSingleQuotes(searchTerm) + '%';
        return [
            SELECT Id, Name, Industry, AnnualRevenue
            FROM Account
            WHERE Name LIKE :searchKey
            WITH SECURITY_ENFORCED
            ORDER BY Name
            LIMIT 50
        ];
    }

    @AuraEnabled
    public static Account createAccount(Account account) {
        // Validate input
        if (String.isBlank(account.Name)) {
            throw new AuraHandledException('Account name is required');
        }

        try {
            insert account;
            return account;
        } catch (DmlException e) {
            throw new AuraHandledException(e.getMessage());
        }
    }

    @AuraEnabled
    public static void updateAccount(Account account) {
        try {
            update account;
        } catch (DmlException e) {
            throw new AuraHandledException(e.getMessage());
        }
    }
}
```

### Wire Adapter Patterns

| Adapter | Use Case | Example |
|---------|----------|---------|
| `getRecord` | Single record by ID | `@wire(getRecord, { recordId: '$recordId', fields: FIELDS })` |
| `getRecords` | Multiple records | `@wire(getRecords, { records: [{ recordIds: $ids, fields: FIELDS }] })` |
| `getFieldValue` | Extract field from record | `getFieldValue(this.account.data, NAME_FIELD)` |
| `getPicklistValues` | Picklist options | `@wire(getPicklistValues, { recordTypeId: '$rtId', fieldApiName: FIELD })` |
| `getObjectInfo` | Object metadata | `@wire(getObjectInfo, { objectApiName: ACCOUNT_OBJECT })` |

---

## Metadata Configuration

### meta.xml Targets

```xml
<?xml version="1.0" encoding="UTF-8"?>
<LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>62.0</apiVersion>
    <isExposed>true</isExposed>
    <masterLabel>Account List</masterLabel>
    <description>Displays a list of accounts with filtering</description>
    <targets>
        <target>lightning__RecordPage</target>
        <target>lightning__AppPage</target>
        <target>lightning__HomePage</target>
        <target>lightning__FlowScreen</target>
        <target>lightningCommunity__Page</target>
        <target>lightningCommunity__Default</target>
    </targets>
    <targetConfigs>
        <targetConfig targets="lightning__RecordPage">
            <objects>
                <object>Account</object>
            </objects>
            <property name="title" type="String" default="Related Contacts"/>
            <property name="maxRecords" type="Integer" default="10"/>
        </targetConfig>
        <targetConfig targets="lightning__FlowScreen">
            <property name="accountId" type="String" role="inputOnly"/>
            <property name="selectedContact" type="String" role="outputOnly"/>
        </targetConfig>
    </targetConfigs>
</LightningComponentBundle>
```

---

## CLI Commands

| Command | Purpose |
|---------|---------|
| `sf lightning generate component` | Create new LWC |
| `sf lightning lwc test run` | Run Jest tests |
| `sf lightning lint` | Lint LWC code |
| `sf project deploy start` | Deploy to org |

### Generate New Component

```bash
sf lightning generate component \
  --name accountList \
  --type lwc \
  --output-dir force-app/main/default/lwc
```

### Run Tests

```bash
# Run all tests
sf lightning lwc test run

# Run specific test file
sf lightning lwc test run --spec force-app/main/default/lwc/accountList/__tests__/accountList.test.js

# Watch mode during development
sf lightning lwc test run --watch
```

---

## Accessibility Checklist

| Requirement | Implementation |
|-------------|----------------|
| **Labels** | Use `label` attribute on inputs, `aria-label` on icons |
| **Keyboard** | All interactive elements focusable, Enter/Space triggers |
| **Focus** | Visible focus indicator, logical tab order |
| **Screen Reader** | `aria-live` for dynamic content, `role` attributes |
| **Color** | Don't rely solely on color, use icons/text |
| **Contrast** | 4.5:1 minimum for text |

```html
<!-- Accessible button -->
<lightning-button
    label="Delete Account"
    icon-name="utility:delete"
    onclick={handleDelete}
    aria-describedby="delete-help">
</lightning-button>
<span id="delete-help" class="slds-assistive-text">
    This will permanently delete the account
</span>

<!-- Accessible live region -->
<div aria-live="polite" class="slds-assistive-text">
    {statusMessage}
</div>
```

---

## Performance Best Practices

1. **Lazy Loading**: Use `if:true/false` to defer rendering
2. **Debounce**: Debounce search inputs
3. **Virtual Scrolling**: Use `lightning-datatable` for large lists
4. **Memoization**: Cache computed values with getters
5. **Event Cleanup**: Unsubscribe in `disconnectedCallback`

```javascript
// Debounce pattern
import { LightningElement } from 'lwc';

export default class SearchBox extends LightningElement {
    searchTerm = '';
    delayTimeout;

    handleSearchChange(event) {
        const searchTerm = event.target.value;

        // Clear previous timeout
        clearTimeout(this.delayTimeout);

        // Debounce 300ms
        this.delayTimeout = setTimeout(() => {
            this.searchTerm = searchTerm;
            this.dispatchEvent(new CustomEvent('search', {
                detail: { searchTerm }
            }));
        }, 300);
    }
}
```

---

## Cross-Skill Integration

| Skill | When to Use | Example |
|-------|-------------|---------|
| sf-apex | Generate Apex controllers | `Skill(skill="sf-apex", args="Create AccountController with @AuraEnabled methods")` |
| sf-testing | Generate Jest tests | `Skill(skill="sf-testing", args="Generate Jest tests for accountList LWC")` |
| sf-deploy | Deploy components | `Skill(skill="sf-deploy", args="Deploy accountList LWC to sandbox")` |
| sf-metadata | Create message channels | `Skill(skill="sf-metadata", args="Create AccountSelected__c message channel")` |

---

## Dependencies

**Required**:
- Target org with LWC support (API 45.0+)
- `sf` CLI authenticated

**For Testing**:
- Node.js 18+
- Jest (`@salesforce/sfdx-lwc-jest`)

**Recommended**:
- sf-apex (for controller generation)
- sf-deploy (for deployment)

Install: `/plugin install github:Jaganpro/sf-skills/sf-lwc`

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
