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
  author: "Jag Valaiyapathy"
  scoring: "165 points across 8 categories (SLDS 2 + Dark Mode compliant)"
---

# sf-lwc: Lightning Web Components Development

Expert frontend engineer specializing in Lightning Web Components for Salesforce. Generate production-ready LWC components using the **PICKLES Framework** for architecture, with proper data binding, Apex/GraphQL integration, event handling, SLDS 2 styling, error handling, and comprehensive Jest tests.

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
12. **Responsive Design**: Form factor detection and adaptive layouts

---

## PICKLES Framework (Architecture Methodology)

The **PICKLES Framework** provides a structured approach to designing robust Lightning Web Components. Apply each principle during component design and implementation.

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

**Purpose**: Validate ideas early before full implementation.

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

**Purpose**: Determine how components interact with data systems.

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

**Purpose**: Structure how LWCs nest and communicate.

**Communication Patterns**:

| Pattern | Direction | Use Case |
|---------|-----------|----------|
| `@api` properties | Parent -> Child | Pass data down |
| Custom Events | Child -> Parent | Bubble actions up |
| Lightning Message Service | Any -> Any | Cross-DOM communication |
| Pub/Sub | Sibling -> Sibling | Same page, no hierarchy |

**Best Practices**:
- Maintain shallow component hierarchies (max 3-4 levels)
- Single responsibility per component
- Clean up subscriptions in `disconnectedCallback()`
- Use custom events purposefully, not for every interaction

### K - Kinetics

**Purpose**: Manage user interaction and event responsiveness.

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
        this.dispatchEvent(new CustomEvent('search', {
            detail: { searchTerm }
        }));
    }, 300);
}
```

### L - Libraries

**Purpose**: Leverage Salesforce-provided and platform tools.

| API/Module | Use Case |
|------------|----------|
| `lightning/navigation` | Page/record navigation |
| `lightning/uiRecordApi` | LDS operations (getRecord, updateRecord) |
| `lightning/toast` | User notifications (preferred) |
| `lightning/modal` | Native modal dialogs |
| `lightning/refresh` | Dispatch refresh events |
| `@salesforce/client/formFactor` | Device-responsive rendering |
| Base Components | Pre-built UI (button, input, datatable) |

**Avoid reinventing** what base components already provide!

### E - Execution

**Purpose**: Optimize performance and resource efficiency.

**Lifecycle Hook Guidance**:

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
- [ ] Use browser DevTools Performance tab

### S - Security

**Purpose**: Enforce access control and data protection.

| Requirement | Implementation |
|-------------|----------------|
| Field-Level Security | Use `WITH SECURITY_ENFORCED` in SOQL |
| CRUD Permissions | Check before DML operations |
| Custom Permissions | Conditionally render features |
| Input Validation | Sanitize before processing |
| Sensitive Data | Never expose in client-side code |

---

## Component Patterns

### 1. Basic Data Display (Wire Service)

```javascript
// accountCard.js
import { LightningElement, api, wire } from 'lwc';
import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
import NAME_FIELD from '@salesforce/schema/Account.Name';
import INDUSTRY_FIELD from '@salesforce/schema/Account.Industry';

const FIELDS = [NAME_FIELD, INDUSTRY_FIELD];

export default class AccountCard extends LightningElement {
    @api recordId;

    @wire(getRecord, { recordId: '$recordId', fields: FIELDS })
    account;

    get name() {
        return getFieldValue(this.account.data, NAME_FIELD);
    }

    get industry() {
        return getFieldValue(this.account.data, INDUSTRY_FIELD);
    }

    get isLoading() {
        return !this.account.data && !this.account.error;
    }
}
```

### 2. Wire Service with Apex

```javascript
// contactList.js
import { LightningElement, api, wire } from 'lwc';
import getContacts from '@salesforce/apex/ContactController.getContacts';
import { refreshApex } from '@salesforce/apex';

export default class ContactList extends LightningElement {
    @api recordId;
    wiredContactsResult;

    @wire(getContacts, { accountId: '$recordId' })
    wiredContacts(result) {
        this.wiredContactsResult = result; // Store for refreshApex
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

### 3. GraphQL Wire Pattern

```javascript
// graphqlContacts.js
import { LightningElement, wire } from 'lwc';
import { gql, graphql } from 'lightning/uiGraphQLApi';

const CONTACTS_QUERY = gql`
    query ContactsQuery($first: Int, $after: String) {
        uiapi {
            query {
                Contact(first: $first, after: $after) {
                    edges {
                        node {
                            Id
                            Name { value }
                            Email { value }
                            Account {
                                Name { value }
                            }
                        }
                        cursor
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
    }
`;

export default class GraphqlContacts extends LightningElement {
    contacts;
    pageInfo;
    error;

    @wire(graphql, {
        query: CONTACTS_QUERY,
        variables: '$queryVariables'
    })
    wiredContacts({ data, error }) {
        if (data) {
            const result = data.uiapi.query.Contact;
            this.contacts = result.edges.map(edge => ({
                id: edge.node.Id,
                name: edge.node.Name.value,
                email: edge.node.Email?.value,
                accountName: edge.node.Account?.Name?.value
            }));
            this.pageInfo = result.pageInfo;
        } else if (error) {
            this.error = error;
        }
    }

    get queryVariables() {
        return { first: 10, after: this._cursor };
    }

    loadMore() {
        if (this.pageInfo?.hasNextPage) {
            this._cursor = this.pageInfo.endCursor;
        }
    }
}
```

### 4. Modal Component Pattern (Composable)

Based on [James Simone's composable modal pattern](https://www.jamessimone.net/blog/joys-of-apex/lwc-composable-modal/).

```javascript
// composableModal.js
import { LightningElement, api } from 'lwc';

const OUTER_MODAL_CLASS = 'outerModalContent';

export default class ComposableModal extends LightningElement {
    @api modalHeader;
    @api modalTagline;
    @api modalSaveHandler;

    _isOpen = false;
    _focusableElements = [];

    @api
    toggleModal() {
        this._isOpen = !this._isOpen;
        if (this._isOpen) {
            this._focusableElements = [...this.querySelectorAll('.focusable')];
            this._focusFirstElement();
            window.addEventListener('keyup', this._handleKeyUp);
        } else {
            window.removeEventListener('keyup', this._handleKeyUp);
        }
    }

    get modalAriaHidden() {
        return !this._isOpen;
    }

    get modalClass() {
        return this._isOpen
            ? 'slds-modal slds-visible slds-fade-in-open'
            : 'slds-modal slds-hidden';
    }

    get backdropClass() {
        return this._isOpen ? 'slds-backdrop slds-backdrop_open' : 'slds-backdrop';
    }

    _handleKeyUp = (event) => {
        if (event.code === 'Escape') {
            this.toggleModal();
        } else if (event.code === 'Tab') {
            this._handleTabNavigation(event);
        }
    }

    _handleTabNavigation(event) {
        const activeEl = this.template.activeElement;
        const lastIndex = this._focusableElements.length - 1;
        const currentIndex = this._focusableElements.indexOf(activeEl);

        if (event.shiftKey && currentIndex === 0) {
            this._focusableElements[lastIndex]?.focus();
        } else if (!event.shiftKey && currentIndex === lastIndex) {
            this._focusFirstElement();
        }
    }

    _focusFirstElement() {
        if (this._focusableElements.length > 0) {
            this._focusableElements[0].focus();
        }
    }

    handleBackdropClick(event) {
        if (event.target.classList.contains(OUTER_MODAL_CLASS)) {
            this.toggleModal();
        }
    }

    handleSave() {
        if (this.modalSaveHandler) {
            this.modalSaveHandler();
        }
        this.toggleModal();
    }

    disconnectedCallback() {
        window.removeEventListener('keyup', this._handleKeyUp);
    }
}
```

```html
<!-- composableModal.html -->
<template>
    <div class={backdropClass}></div>
    <div class={modalClass}
         role="dialog"
         aria-modal="true"
         aria-hidden={modalAriaHidden}
         aria-labelledby="modal-heading">
        <div class="slds-modal__container outerModalContent"
             onclick={handleBackdropClick}>
            <div class="slds-modal__content slds-p-around_medium">
                <template lwc:if={modalHeader}>
                    <h2 id="modal-heading" class="slds-text-heading_medium">
                        {modalHeader}
                    </h2>
                </template>
                <template lwc:if={modalTagline}>
                    <p class="slds-m-top_x-small slds-text-color_weak">
                        {modalTagline}
                    </p>
                </template>
                <div class="slds-m-top_medium">
                    <slot name="modalContent"></slot>
                </div>
                <div class="slds-m-top_medium slds-text-align_right">
                    <lightning-button
                        label="Cancel"
                        onclick={toggleModal}
                        class="slds-m-right_x-small focusable">
                    </lightning-button>
                    <lightning-button
                        variant="brand"
                        label="Save"
                        onclick={handleSave}
                        class="focusable">
                    </lightning-button>
                </div>
            </div>
        </div>
    </div>
    <div aria-hidden={_isOpen}>
        <slot name="body"></slot>
    </div>
</template>
```

### 5. Parent-Child Communication

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
    <template lwc:if={selectedAccountId}>
        <c-account-detail account-id={selectedAccountId}></c-account-detail>
    </template>
</template>
```

### 6. Lightning Message Service (Cross-DOM)

```javascript
// publisher.js
import { LightningElement, wire } from 'lwc';
import { publish, MessageContext } from 'lightning/messageService';
import ACCOUNT_SELECTED_CHANNEL from '@salesforce/messageChannel/AccountSelected__c';

export default class Publisher extends LightningElement {
    @wire(MessageContext) messageContext;

    handleSelect(event) {
        const payload = { accountId: event.target.dataset.id };
        publish(this.messageContext, ACCOUNT_SELECTED_CHANNEL, payload);
    }
}
```

```javascript
// subscriber.js
import { LightningElement, wire } from 'lwc';
import { subscribe, unsubscribe, MessageContext,
         APPLICATION_SCOPE } from 'lightning/messageService';
import ACCOUNT_SELECTED_CHANNEL from '@salesforce/messageChannel/AccountSelected__c';

export default class Subscriber extends LightningElement {
    subscription = null;
    accountId;

    @wire(MessageContext) messageContext;

    connectedCallback() {
        this.subscribeToChannel();
    }

    disconnectedCallback() {
        this.unsubscribeFromChannel();
    }

    subscribeToChannel() {
        if (!this.subscription) {
            this.subscription = subscribe(
                this.messageContext,
                ACCOUNT_SELECTED_CHANNEL,
                (message) => this.handleMessage(message),
                { scope: APPLICATION_SCOPE }
            );
        }
    }

    unsubscribeFromChannel() {
        unsubscribe(this.subscription);
        this.subscription = null;
    }

    handleMessage(message) {
        this.accountId = message.accountId;
    }
}
```

### 7. Navigation

```javascript
// navigator.js
import { LightningElement } from 'lwc';
import { NavigationMixin } from 'lightning/navigation';

export default class Navigator extends NavigationMixin(LightningElement) {

    navigateToRecord(recordId, objectApiName = 'Account') {
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: {
                recordId,
                objectApiName,
                actionName: 'view'
            }
        });
    }

    navigateToList(objectApiName, filterName = 'Recent') {
        this[NavigationMixin.Navigate]({
            type: 'standard__objectPage',
            attributes: {
                objectApiName,
                actionName: 'list'
            },
            state: { filterName }
        });
    }

    navigateToNewRecord(objectApiName, defaultValues = {}) {
        this[NavigationMixin.Navigate]({
            type: 'standard__objectPage',
            attributes: {
                objectApiName,
                actionName: 'new'
            },
            state: {
                defaultFieldValues: Object.entries(defaultValues)
                    .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
                    .join(',')
            }
        });
    }
}
```

---

## Error Handling & Toast Notifications

Centralized error handling is critical for production LWC. Use the `reduceErrors` utility pattern from LWC Recipes for consistent error display.

### Error Types in LWC

| Error Source | Structure | Common Cause |
|-------------|-----------|--------------|
| JavaScript | Standard `Error` object | Null references, bad bindings |
| Lightning Data Service | `{ body: { message, output } }` | FLS violations, invalid record |
| Apex `@AuraEnabled` | `{ body: { message } }` | `AuraHandledException`, DML errors |
| Wire adapter | `{ body: { message } }` or array | Query errors, permissions |

### reduceErrors Utility

```javascript
// utils/errorUtils.js
/**
 * Reduces one or more LDS/Apex/JS errors into a string[] of error messages.
 * Adapted from lwc-recipes ldsUtils.
 */
export function reduceErrors(errors) {
    if (!Array.isArray(errors)) {
        errors = [errors];
    }

    return errors
        .filter((error) => !!error)
        .map((error) => {
            // UI API read errors
            if (Array.isArray(error.body)) {
                return error.body.map((e) => e.message);
            }
            // Page-level / field-level errors from LDS save
            if (
                error.body &&
                error.body.output &&
                error.body.output.errors &&
                error.body.output.errors.length > 0
            ) {
                return error.body.output.errors.map((e) => e.message);
            }
            // UI API DML / Apex errors
            if (error.body && typeof error.body.message === 'string') {
                return error.body.message;
            }
            // JS Error object
            if (typeof error.message === 'string') {
                return error.message;
            }
            // Unknown shape
            return error.statusText || 'Unknown error';
        })
        .reduce((prev, curr) => prev.concat(curr), []);
}
```

### Toast Notifications (Preferred: lightning/toast)

Use `lightning/toast` (preferred) instead of the older `lightning/platformShowToastEvent`.

```javascript
// Modern toast API (preferred)
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import Toast from 'lightning/toast';

// --- Option 1: lightning/toast (preferred, works in LWR sites) ---
Toast.show(this, {
    label: 'Record Saved',
    message: 'The account was updated successfully.',
    variant: 'success'  // success | error | warning | info
});

// --- Option 2: ShowToastEvent (classic, Lightning Experience only) ---
this.dispatchEvent(new ShowToastEvent({
    title: 'Record Saved',
    message: 'The account was updated successfully.',
    variant: 'success'
}));
```

**Toast Variants**:

| Variant | Use Case | Auto-dismiss |
|---------|----------|-------------|
| `success` | Record saved, action completed | 4.8s |
| `error` | Save failed, validation error | Sticky (user dismiss) |
| `warning` | Partial success, approaching limits | 4.8s |
| `info` | Informational messages | 4.8s |

### Centralized Error Handler Pattern

```javascript
// errorHandlerMixin.js - reusable across all components
import Toast from 'lightning/toast';
import { reduceErrors } from 'c/errorUtils';

export const ErrorHandlerMixin = (superclass) =>
    class extends superclass {
        _isLoading = false;

        get isLoading() {
            return this._isLoading;
        }

        showToast(label, message, variant = 'info') {
            Toast.show(this, { label, message, variant });
        }

        showSuccess(message) {
            this.showToast('Success', message, 'success');
        }

        showError(error) {
            const messages = reduceErrors(error);
            this.showToast('Error', messages.join(', '), 'error');
        }

        async executeWithLoading(asyncFn) {
            this._isLoading = true;
            try {
                const result = await asyncFn();
                return result;
            } catch (error) {
                this.showError(error);
                throw error;
            } finally {
                this._isLoading = false;
            }
        }
    };

// Usage:
// import { ErrorHandlerMixin } from 'c/errorHandlerMixin';
// export default class MyComponent extends ErrorHandlerMixin(LightningElement) {
//     async handleSave() {
//         await this.executeWithLoading(async () => {
//             await saveRecord({ record: this.record });
//             this.showSuccess('Record saved.');
//         });
//     }
// }
```

### Error Handling in Wire vs Imperative

```javascript
// Wire: errors handled in wired function
@wire(getAccounts, { searchTerm: '$searchTerm' })
wiredAccounts(result) {
    this.wiredResult = result;
    if (result.data) {
        this.accounts = result.data;
        this.error = undefined;
    } else if (result.error) {
        this.accounts = undefined;
        this.error = result.error;
        this.showError(result.error); // Toast notification
    }
}

// Imperative: errors handled in try-catch
async handleSave() {
    try {
        await createAccount({ accountJson: JSON.stringify(this.record) });
        this.showSuccess('Account created successfully.');
        await refreshApex(this.wiredResult);
    } catch (error) {
        this.showError(error);
    }
}
```

---

## Lightning Datatable Patterns

`lightning-datatable` is the standard component for tabular data display with sorting, inline editing, infinite scrolling, and row selection.

### Basic Datatable

```javascript
// contactDatatable.js
import { LightningElement, wire } from 'lwc';
import getContacts from '@salesforce/apex/ContactController.getContacts';
import { refreshApex } from '@salesforce/apex';
import { updateRecord } from 'lightning/uiRecordApi';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

const COLUMNS = [
    { label: 'Name', fieldName: 'Name', type: 'text', sortable: true },
    { label: 'Email', fieldName: 'Email', type: 'email', sortable: true },
    { label: 'Phone', fieldName: 'Phone', type: 'phone' },
    {
        label: 'Account',
        fieldName: 'AccountUrl',
        type: 'url',
        typeAttributes: {
            label: { fieldName: 'AccountName' },
            target: '_blank'
        }
    },
    {
        label: 'Created',
        fieldName: 'CreatedDate',
        type: 'date',
        typeAttributes: {
            year: 'numeric',
            month: 'short',
            day: '2-digit'
        }
    }
];

export default class ContactDatatable extends LightningElement {
    columns = COLUMNS;
    contacts;
    error;
    sortedBy;
    sortDirection = 'asc';
    wiredContactsResult;

    @wire(getContacts)
    wiredContacts(result) {
        this.wiredContactsResult = result;
        if (result.data) {
            this.contacts = result.data.map(contact => ({
                ...contact,
                AccountName: contact.Account?.Name,
                AccountUrl: contact.AccountId
                    ? `/${contact.AccountId}`
                    : undefined
            }));
            this.error = undefined;
        } else if (result.error) {
            this.error = result.error;
            this.contacts = undefined;
        }
    }

    handleSort(event) {
        const { fieldName, sortDirection } = event.detail;
        this.sortedBy = fieldName;
        this.sortDirection = sortDirection;

        const cloned = [...this.contacts];
        cloned.sort((a, b) => {
            let valA = a[fieldName] || '';
            let valB = b[fieldName] || '';
            if (typeof valA === 'string') {
                valA = valA.toLowerCase();
                valB = valB.toLowerCase();
            }
            const result = valA < valB ? -1 : valA > valB ? 1 : 0;
            return sortDirection === 'asc' ? result : -result;
        });
        this.contacts = cloned;
    }
}
```

```html
<!-- contactDatatable.html -->
<template>
    <lightning-card title="Contacts" icon-name="standard:contact">
        <lightning-datatable
            key-field="Id"
            data={contacts}
            columns={columns}
            sorted-by={sortedBy}
            sorted-direction={sortDirection}
            onsort={handleSort}
            hide-checkbox-column>
        </lightning-datatable>
        <template lwc:if={error}>
            <p class="slds-text-color_error slds-p-around_small">
                Error loading contacts.
            </p>
        </template>
    </lightning-card>
</template>
```

### Datatable with Inline Editing

```javascript
// editableContactTable.js
import { LightningElement, wire } from 'lwc';
import getContacts from '@salesforce/apex/ContactController.getContacts';
import { refreshApex } from '@salesforce/apex';
import { updateRecord } from 'lightning/uiRecordApi';
import { notifyRecordUpdateAvailable } from 'lightning/uiRecordApi';
import Toast from 'lightning/toast';

const COLUMNS = [
    { label: 'First Name', fieldName: 'FirstName', editable: true },
    { label: 'Last Name', fieldName: 'LastName', editable: true },
    { label: 'Email', fieldName: 'Email', type: 'email', editable: true },
    { label: 'Phone', fieldName: 'Phone', type: 'phone' }
];

export default class EditableContactTable extends LightningElement {
    columns = COLUMNS;
    draftValues = [];
    wiredContactsResult;

    @wire(getContacts)
    contacts;

    async handleSave(event) {
        const updatedFields = event.detail.draftValues;

        try {
            const updatePromises = updatedFields.map((draft) => {
                const fields = { ...draft };
                return updateRecord({ fields });
            });

            await Promise.all(updatePromises);

            Toast.show(this, {
                label: 'Success',
                message: `${updatedFields.length} record(s) updated.`,
                variant: 'success'
            });

            this.draftValues = [];

            // Notify LDS cache and refresh wire
            await notifyRecordUpdateAvailable(
                updatedFields.map((draft) => ({ recordId: draft.Id }))
            );
            await refreshApex(this.contacts);

        } catch (error) {
            Toast.show(this, {
                label: 'Error',
                message: 'Failed to update records.',
                variant: 'error'
            });
        }
    }
}
```

```html
<!-- editableContactTable.html -->
<template>
    <lightning-datatable
        key-field="Id"
        data={contacts.data}
        columns={columns}
        draft-values={draftValues}
        onsave={handleSave}
        hide-checkbox-column>
    </lightning-datatable>
</template>
```

### Datatable with Infinite Scrolling

```javascript
// infiniteScrollTable.js
import { LightningElement, track } from 'lwc';
import getRecordsBatch from '@salesforce/apex/PaginatedController.getRecordsBatch';

export default class InfiniteScrollTable extends LightningElement {
    @track data = [];
    columns = [/* column definitions */];
    isLoading = false;
    offset = 0;
    batchSize = 50;
    totalRecords = 0;

    connectedCallback() {
        this.loadData();
    }

    async loadData() {
        this.isLoading = true;
        try {
            const result = await getRecordsBatch({
                limitSize: this.batchSize,
                offsetSize: this.offset
            });
            this.data = [...this.data, ...result];
            this.offset += result.length;
        } catch (error) {
            // Handle error
        } finally {
            this.isLoading = false;
        }
    }

    handleLoadMore(event) {
        if (this.isLoading) return;
        event.target.isLoading = true;
        this.loadData().then(() => {
            event.target.isLoading = false;
        });
    }
}
```

```html
<!-- infiniteScrollTable.html -->
<template>
    <lightning-datatable
        key-field="Id"
        data={data}
        columns={columns}
        enable-infinite-loading
        onloadmore={handleLoadMore}
        hide-checkbox-column>
    </lightning-datatable>
</template>
```

### Datatable Performance Guidelines

| Guideline | Recommendation |
|-----------|----------------|
| Max rows loaded at once | 50 (use infinite scrolling) |
| Optimal column count | Up to 5 for best performance |
| Hard limit tested | 1,000 rows x 5 columns |
| Inline editing | Enable only on columns that need it |
| Custom data types | Minimize `setTimeout()` and promises |
| Large datasets (250+ rows) | Keep columns under 20 |

---

## Dynamic Components (lwc:component)

Dynamically instantiate LWC components at runtime using `lwc:component` with the `lwc:is` directive. Useful for plugin architectures, configurable UIs, and component factories.

### Requirements

- API version 55.0 or later
- Lightning Web Security (LWS) enabled
- Component meta.xml must include: `<capability>lightning__dynamicComponent</capability>`

### Basic Dynamic Component

```javascript
// dynamicLoader.js
import { LightningElement } from 'lwc';

export default class DynamicLoader extends LightningElement {
    componentConstructor;
    componentName = 'c/accountCard';

    async connectedCallback() {
        await this.loadComponent(this.componentName);
    }

    async loadComponent(name) {
        try {
            const { default: ctor } = await import(name);
            this.componentConstructor = ctor;
        } catch (error) {
            console.error(`Failed to load component: ${name}`, error);
            this.componentConstructor = null; // Renders nothing
        }
    }
}
```

```html
<!-- dynamicLoader.html -->
<template>
    <lwc:component lwc:is={componentConstructor}></lwc:component>
</template>
```

### Dynamic Component with Props (lwc:spread)

```javascript
// dynamicWithProps.js
import { LightningElement, api } from 'lwc';

export default class DynamicWithProps extends LightningElement {
    componentConstructor;
    _componentProps = {};

    @api
    async loadComponent(name, props = {}) {
        try {
            const { default: ctor } = await import(name);
            this.componentConstructor = ctor;
            this._componentProps = props;
        } catch (error) {
            console.error('Dynamic component load failed:', error);
        }
    }
}
```

```html
<!-- dynamicWithProps.html -->
<template>
    <lwc:component
        lwc:is={componentConstructor}
        lwc:spread={_componentProps}>
    </lwc:component>
</template>
```

### When to Use Dynamic Components

| Use Case | Recommended |
|----------|-------------|
| Plugin / extension architecture | Yes |
| Configurable dashboard tiles | Yes |
| A/B testing different UIs | Yes |
| Static known components | No (use direct references) |
| Performance-critical paths | No (adds async overhead) |

**Key behavior**: When the constructor changes, the existing component is removed from the DOM with all children, and the new component is rendered fresh.

---

## Light DOM vs Shadow DOM

LWC defaults to Shadow DOM for encapsulation. Light DOM is available for scenarios requiring global styling or third-party library integration.

### Decision Framework

| Factor | Shadow DOM (Default) | Light DOM |
|--------|---------------------|-----------|
| Style encapsulation | Full isolation | Styles cascade in/out |
| Security | Protected by LWS | Must nest inside shadow DOM parent |
| Third-party CSS libs | Blocked by shadow boundary | Full access |
| Global theming | Per-component hooks only | Inherits page styles |
| DOM querying | `this.template.querySelector()` | `this.querySelector()` |
| Packageable | Yes | No (cannot package) |
| Base components | N/A (always shadow) | N/A (always shadow) |
| Event retargeting | Events retargeted to host | Events not retargeted |

**Default choice**: Shadow DOM. Only use Light DOM when you have a specific need.

### Light DOM Implementation

```javascript
// lightDomComponent.js
import { LightningElement } from 'lwc';

export default class LightDomComponent extends LightningElement {
    static renderMode = 'light'; // Required
}
```

```html
<!-- lightDomComponent.html -->
<template lwc:render-mode="light">
    <div class="custom-styled-content">
        <p>This content renders in the Light DOM.</p>
        <slot></slot>
    </div>
</template>
```

### Scoped Styles for Light DOM

Use `*.scoped.css` to prevent style leakage from Light DOM components:

```css
/* lightDomComponent.scoped.css */
.custom-styled-content {
    padding: var(--slds-g-spacing-4, 1rem);
    background-color: var(--slds-g-color-surface-container-1, #ffffff);
}
```

### Light DOM Restrictions

- **Security**: Top-level light DOM components bypass LWS -- always nest inside a shadow DOM parent
- **Packaging**: Cannot be distributed in managed or unlocked packages
- **Slots**: Lifecycle hooks on slots never fire; slots inside `for:each` not supported
- **Base components**: `lightning-*` components always render in shadow DOM regardless
- **Aura**: Aura components cannot use light DOM directly (but can contain LWC light DOM children)

### Recommended Architecture Pattern

```
shadow-dom-wrapper (shadow)
  +-- light-dom-child-a (light) -- can use global CSS
  +-- light-dom-child-b (light) -- can use third-party libs
  +-- base-component (shadow)   -- always shadow
```

---

## Responsive Design (Form Factor Detection)

Detect the device form factor and adapt component layout and behavior.

### Form Factor Module

```javascript
// responsiveComponent.js
import { LightningElement } from 'lwc';
import FORM_FACTOR from '@salesforce/client/formFactor';

export default class ResponsiveComponent extends LightningElement {
    formFactor = FORM_FACTOR;

    get isDesktop() {
        return FORM_FACTOR === 'Large';
    }

    get isTablet() {
        return FORM_FACTOR === 'Medium';
    }

    get isMobile() {
        return FORM_FACTOR === 'Small';
    }

    get containerClass() {
        return FORM_FACTOR === 'Small'
            ? 'slds-p-around_small'
            : 'slds-p-around_medium';
    }

    get columnsPerRow() {
        switch (FORM_FACTOR) {
            case 'Large':  return 3;
            case 'Medium': return 2;
            case 'Small':  return 1;
            default:       return 3;
        }
    }
}
```

```html
<!-- responsiveComponent.html -->
<template>
    <div class={containerClass}>
        <template lwc:if={isDesktop}>
            <div class="slds-grid slds-wrap">
                <!-- 3-column desktop layout -->
            </div>
        </template>
        <template lwc:elseif={isMobile}>
            <div class="slds-grid slds-grid_vertical">
                <!-- Stacked mobile layout -->
            </div>
        </template>
        <template lwc:else>
            <div class="slds-grid slds-wrap">
                <!-- 2-column tablet layout -->
            </div>
        </template>
    </div>
</template>
```

**Form Factor Values**:

| Value | Device |
|-------|--------|
| `Large` | Desktop browser |
| `Medium` | Tablet |
| `Small` | Phone |

### meta.xml Form Factor Configuration

```xml
<targetConfigs>
    <targetConfig targets="lightning__RecordPage">
        <supportedFormFactors>
            <supportedFormFactor type="Large" />
            <supportedFormFactor type="Small" />
        </supportedFormFactors>
    </targetConfig>
</targetConfigs>
```

---

## SLDS 2 Validation (165-Point Scoring)

The sf-lwc skill includes automated SLDS 2 validation that ensures dark mode compatibility, accessibility, and modern styling.

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

**Scoring Thresholds**:
```
150-165 pts -> Production-ready, full SLDS 2 + Dark Mode
125-149 pts -> Good component, minor styling issues
100-124 pts -> Functional, needs SLDS cleanup
 75-99 pts  -> Basic functionality, SLDS issues
   <75 pts  -> Needs significant work
```

---

## Dark Mode Readiness

Dark mode is exclusive to SLDS 2 themes. Components must use global styling hooks to support light/dark theme switching.

### Dark Mode Checklist

- [ ] **No hardcoded hex colors** (`#FFFFFF`, `#333333`)
- [ ] **No hardcoded RGB/RGBA values**
- [ ] **All colors use CSS variables** (`var(--slds-g-color-*)`)
- [ ] **Fallback values provided** for SLDS 1 compatibility
- [ ] **No inline color styles** in HTML templates
- [ ] **Icons use SLDS utility icons** (auto-adjust for dark mode)

### SLDS 1 to SLDS 2 Migration

**Before (SLDS 1 - Deprecated)**:
```css
.my-card {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #dddddd;
    border-radius: 4px;
}
```

**After (SLDS 2 - Dark Mode Ready)**:
```css
.my-card {
    background-color: var(--slds-g-color-surface-container-1, #ffffff);
    color: var(--slds-g-color-on-surface, #181818);
    border: 1px solid var(--slds-g-color-border-1, #c9c9c9);
    border-radius: var(--slds-g-radius-border-2, 0.25rem);
}
```

### Global Styling Hooks Reference

| Category | SLDS 2 Variable | Purpose |
|----------|-----------------|---------|
| **Surface** | `--slds-g-color-surface-1` to `-4` | Background colors |
| **Container** | `--slds-g-color-surface-container-1` to `-3` | Card/section backgrounds |
| **Text** | `--slds-g-color-on-surface` | Primary text |
| **Text Secondary** | `--slds-g-color-on-surface-1`, `-2` | Muted text |
| **Border** | `--slds-g-color-border-1`, `-2` | Borders |
| **Brand** | `--slds-g-color-brand-1`, `-2` | Brand accent |
| **Error** | `--slds-g-color-error-1` | Error states |
| **Success** | `--slds-g-color-success-1` | Success states |
| **Warning** | `--slds-g-color-warning-1` | Warning states |
| **Spacing** | `--slds-g-spacing-0` to `-12` | Margins/padding |
| **Font Size** | `--slds-g-font-size-1` to `-10` | Typography |
| **Radius** | `--slds-g-radius-border-1` to `-4` | Border radius |

**Important**: Component-level hooks (`--slds-c-*`) are NOT supported in SLDS 2 yet. Use only global hooks (`--slds-g-*`).

### SLDS Validator/Linter Commands

```bash
# Install SLDS Linter
npm install -g @salesforce-ux/slds-linter

# Run validation
slds-linter lint force-app/main/default/lwc/myComponent

# Auto-fix issues
slds-linter lint --fix force-app/main/default/lwc/myComponent
```

---

## Advanced Jest Testing Patterns

Based on [James Simone's advanced testing patterns](https://www.jamessimone.net/blog/joys-of-apex/advanced-lwc-jest-testing/).

### Render Cycle Helper

```javascript
// testUtils.js
export const runRenderingLifecycle = async (reasons = ['render']) => {
    while (reasons.length > 0) {
        await Promise.resolve(reasons.pop());
    }
};

// Usage in tests
it('updates after property change', async () => {
    const element = createElement('c-example', { is: Example });
    document.body.appendChild(element);

    element.greeting = 'new value';
    await runRenderingLifecycle(['property change', 'render']);

    expect(element.shadowRoot.querySelector('div').textContent).toBe('new value');
});
```

### Proxy Unboxing (LWS Compatibility)

```javascript
// Lightning Web Security proxifies objects - unbox them for assertions
const unboxedData = JSON.parse(JSON.stringify(component.data));
expect(unboxedData).toEqual(expectedData);
```

### DOM Cleanup Pattern

```javascript
describe('c-my-component', () => {
    afterEach(() => {
        // Clean up DOM to prevent state bleed
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });
});
```

### ResizeObserver Polyfill

```javascript
// jest.setup.js
if (!window.ResizeObserver) {
    window.ResizeObserver = class ResizeObserver {
        constructor(callback) {
            this.callback = callback;
        }
        observe() {}
        unobserve() {}
        disconnect() {}
    };
}
```

### Complete Test Template

```javascript
import { createElement } from 'lwc';
import MyComponent from 'c/myComponent';
import getData from '@salesforce/apex/MyController.getData';

jest.mock('@salesforce/apex/MyController.getData', () => ({
    default: jest.fn()
}), { virtual: true });

const MOCK_DATA = [
    { Id: '001xx000001', Name: 'Test 1' },
    { Id: '001xx000002', Name: 'Test 2' }
];

const runRenderingLifecycle = async (reasons = ['render']) => {
    while (reasons.length > 0) {
        await Promise.resolve(reasons.pop());
    }
};

describe('c-my-component', () => {
    afterEach(() => {
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }
        jest.clearAllMocks();
    });

    it('displays data when loaded successfully', async () => {
        getData.mockResolvedValue(MOCK_DATA);

        const element = createElement('c-my-component', { is: MyComponent });
        document.body.appendChild(element);

        await runRenderingLifecycle(['wire data fetch', 'render']);

        const items = element.shadowRoot.querySelectorAll('.item');
        expect(items.length).toBe(2);
    });

    it('displays error when fetch fails', async () => {
        getData.mockRejectedValue(new Error('Failed'));

        const element = createElement('c-my-component', { is: MyComponent });
        document.body.appendChild(element);

        await runRenderingLifecycle(['wire error', 'render']);

        const error = element.shadowRoot.querySelector('.error');
        expect(error).not.toBeNull();
    });

    it('fires event when item clicked', async () => {
        getData.mockResolvedValue(MOCK_DATA);
        const handler = jest.fn();

        const element = createElement('c-my-component', { is: MyComponent });
        element.addEventListener('itemselected', handler);
        document.body.appendChild(element);

        await runRenderingLifecycle();

        const item = element.shadowRoot.querySelector('.item');
        item.click();

        expect(handler).toHaveBeenCalled();
        expect(handler.mock.calls[0][0].detail.id).toBe('001xx000001');
    });
});
```

---

## Apex Controller Integration

> For comprehensive Apex patterns (triggers, batch jobs, test classes), see the **sf-apex** skill.
> This section covers only the LWC-facing `@AuraEnabled` contract patterns.

### Cacheable Methods (for @wire)

```apex
public with sharing class LwcController {

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
}
```

### Non-Cacheable Methods (for DML)

```apex
@AuraEnabled
public static Account createAccount(String accountJson) {
    Account acc = (Account) JSON.deserialize(accountJson, Account.class);

    SObjectAccessDecision decision = Security.stripInaccessible(
        AccessType.CREATABLE,
        new List<Account>{ acc }
    );

    insert decision.getRecords();
    return (Account) decision.getRecords()[0];
}
```

### Error Handling in Apex Controllers

```apex
@AuraEnabled
public static void updateRecords(List<Id> recordIds) {
    try {
        // Business logic
    } catch (DmlException e) {
        throw new AuraHandledException(e.getMessage());
    } catch (Exception e) {
        throw new AuraHandledException(
            'An unexpected error occurred. Please contact your administrator.'
        );
    }
}
```

**Rule**: Always throw `AuraHandledException` -- other exceptions expose stack traces to the client.

---

## Metadata Configuration

### meta.xml Targets

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
| `sf lightning generate component --type lwc` | Create new LWC |
| `sf lightning lwc test run` | Run Jest tests |
| `sf lightning lwc test run --watch` | Watch mode |
| `sf project deploy start -m LightningComponentBundle` | Deploy LWC |

### Generate New Component

```bash
sf lightning generate component \
  --name accountDashboard \
  --type lwc \
  --output-dir force-app/main/default/lwc
```

### Run Tests

```bash
# All tests
sf lightning lwc test run

# Specific component
sf lightning lwc test run --spec force-app/main/default/lwc/accountList/__tests__

# With coverage
sf lightning lwc test run -- --coverage
```

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
<div aria-live="polite" class="slds-assistive-text">
    {statusMessage}
</div>

<!-- Accessible error display -->
<template lwc:if={errorMessage}>
    <div role="alert" class="slds-text-color_error slds-p-around_small">
        {errorMessage}
    </div>
</template>
```

---

## Flow Screen Integration

LWC components can be embedded in Flow Screens for custom UI experiences within guided processes.

### Key Concepts

| Mechanism | Direction | Purpose |
|-----------|-----------|---------|
| `@api` with `role="inputOnly"` | Flow -> LWC | Pass context data |
| `FlowAttributeChangeEvent` | LWC -> Flow | Return user selections |
| `FlowNavigationFinishEvent` | LWC -> Flow | Programmatic Next/Back/Finish |
| `availableActions` | Flow -> LWC | Check available navigation |

### Quick Example

```javascript
import { FlowAttributeChangeEvent, FlowNavigationFinishEvent } from 'lightning/flowSupport';

@api recordId;           // Input from Flow
@api selectedRecordId;   // Output to Flow
@api availableActions = [];

handleSelect(event) {
    this.selectedRecordId = event.detail.id;
    // CRITICAL: Notify Flow of the change
    this.dispatchEvent(new FlowAttributeChangeEvent(
        'selectedRecordId',
        this.selectedRecordId
    ));
}

handleNext() {
    if (this.availableActions.includes('NEXT')) {
        this.dispatchEvent(new FlowNavigationFinishEvent('NEXT'));
    }
}
```

### Template & Documentation

| Resource | Location |
|----------|----------|
| Flow Screen Component Template | `templates/flow-screen-component/` |
| Flow Integration Guide | [docs/flow-integration-guide.md](docs/flow-integration-guide.md) |
| Triangle Architecture | [shared/docs/flow-lwc-apex-triangle.md](../shared/docs/flow-lwc-apex-triangle.md) |

---

## Workspace API (Console Apps)

For components used in Service Console or Sales Console apps. Use `lightning/platformWorkspaceApi` for tab management.

```javascript
import { IsConsoleNavigation, getFocusedTabInfo, openTab,
         setTabLabel, setTabIcon } from 'lightning/platformWorkspaceApi';

// Wire IsConsoleNavigation to detect console context
@wire(IsConsoleNavigation) isConsole;

async openRecordTab(recordId) {
    if (!this.isConsole) return;
    await openTab({ recordId, focus: true });
}
```

> Full Workspace API patterns are niche. See the [Salesforce Workspace API Reference](https://developer.salesforce.com/docs/platform/lwc/guide/use-workspace-api.html) for details.

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

**Required**:
- Target org with LWC support (API 45.0+)
- `sf` CLI authenticated

**For Testing**:
- Node.js 18+
- Jest (`@salesforce/sfdx-lwc-jest`)

**For SLDS Validation**:
- `@salesforce-ux/slds-linter` (optional)

Install: `/plugin install github:Jaganpro/sf-skills/sf-lwc`

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
- [Error Handling Best Practices (Salesforce Blog)](https://developer.salesforce.com/blogs/2020/08/error-handling-best-practices-for-lightning-web-components)
- [Lightning Datatable (Component Library)](https://developer.salesforce.com/docs/component-library/bundle/lightning-datatable)
- [Datatable Inline Editing (LWC Dev Guide)](https://developer.salesforce.com/docs/platform/lwc/guide/data-table-inline-edit.html)
- [Datatable Performance (LWC Dev Guide)](https://developer.salesforce.com/docs/platform/lwc/guide/data-table-performance.html)
- [Dynamic Components (LWC Dev Guide)](https://developer.salesforce.com/docs/platform/lwc/guide/js-dynamic-components.html)
- [Light DOM (LWC Dev Guide)](https://developer.salesforce.com/docs/platform/lwc/guide/create-light-dom.html)
- [Demystifying Light DOM (Salesforce Blog)](https://developer.salesforce.com/blogs/2023/10/demystifying-light-dom-and-its-use-cases)
- [Client Form Factor (LWC Dev Guide)](https://developer.salesforce.com/docs/platform/lwc/guide/create-client-form-factor.html)
- [Compare SLDS Versions (LWC Dev Guide)](https://developer.salesforce.com/docs/platform/lwc/guide/create-components-css-slds1-slds2.html)
- [LWC Error Types (LWC Dev Guide)](https://developer.salesforce.com/docs/platform/lwc/guide/data-error-types.html)

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2026 Jag Valaiyapathy
