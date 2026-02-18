# Lightning Datatable Patterns

Complete examples for `lightning-datatable` including sorting, inline editing, and infinite scrolling.

---

## Basic Datatable with Sorting

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

## Datatable with Inline Editing

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

## Datatable with Infinite Scrolling

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

## Datatable Performance Guidelines

| Guideline | Recommendation |
|-----------|----------------|
| Max rows loaded at once | 50 (use infinite scrolling) |
| Optimal column count | Up to 5 for best performance |
| Hard limit tested | 1,000 rows x 5 columns |
| Inline editing | Enable only on columns that need it |
| Custom data types | Minimize `setTimeout()` and promises |
| Large datasets (250+ rows) | Keep columns under 20 |
