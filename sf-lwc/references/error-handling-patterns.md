# LWC Error Handling & Toast Patterns

Centralized error handling patterns including `reduceErrors` utility, toast notifications, error handler mixin, and wire vs imperative error handling.

---

## Error Types in LWC

| Error Source | Structure | Common Cause |
|-------------|-----------|--------------|
| JavaScript | Standard `Error` object | Null references, bad bindings |
| Lightning Data Service | `{ body: { message, output } }` | FLS violations, invalid record |
| Apex `@AuraEnabled` | `{ body: { message } }` | `AuraHandledException`, DML errors |
| Wire adapter | `{ body: { message } }` or array | Query errors, permissions |

## reduceErrors Utility

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

## Toast Notifications

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

## Centralized Error Handler Mixin

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

## Error Handling: Wire vs Imperative

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
