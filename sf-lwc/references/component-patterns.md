# LWC Component Patterns

Complete code examples for common LWC patterns: wire service, GraphQL, modals, parent-child communication, Lightning Message Service, and navigation.

---

## 1. Basic Data Display (Wire Service)

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

## 2. Wire Service with Apex

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

## 3. GraphQL Wire Pattern

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

## 4. Composable Modal Pattern

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

## 5. Parent-Child Communication

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

## 6. Lightning Message Service (Cross-DOM)

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

## 7. Navigation

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
