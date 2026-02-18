# Responsive Design (Form Factor Detection)

Detect the device form factor and adapt component layout and behavior.

---

## Form Factor Values

| Value | Device |
|-------|--------|
| `Large` | Desktop browser |
| `Medium` | Tablet |
| `Small` | Phone |

## Form Factor Module

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

## meta.xml Form Factor Configuration

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
